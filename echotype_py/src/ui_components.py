"""Arcade UI components for EchoType.

Follows the component contract used by the f1-race-replay reference project: a
`BaseComponent` with `draw` / `on_resize` / `on_mouse_press` / `on_mouse_motion`
hooks, each panel hand-drawn as a dark translucent rectangle with a gray border,
white headers and light-gray body text, and independent visibility toggles.
"""

from typing import Callable, List, Optional, Sequence, Tuple

import arcade

from .constants import COLORS, CONTROLS_HELP, FONT


def _panel(cx: float, cy: float, width: float, height: float,
           fill=COLORS["panel_background"], border=COLORS["panel_border"],
           border_width: int = 2) -> None:
    rect = arcade.XYWH(cx, cy, width, height)
    arcade.draw_rect_filled(rect, fill)
    arcade.draw_rect_outline(rect, border, border_width)


class BaseComponent:
    """Draw/interaction contract. Subclasses override what they need."""

    def on_resize(self, window) -> None:
        pass

    def draw(self, window) -> None:
        pass

    def on_mouse_press(self, window, x: float, y: float, button: int, modifiers: int) -> bool:
        return False

    def on_mouse_motion(self, window, x: float, y: float) -> None:
        pass


class ToggleableComponent(BaseComponent):
    def __init__(self, visible: bool = True) -> None:
        self._visible = visible

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    def toggle_visibility(self) -> bool:
        self._visible = not self._visible
        return self._visible


# --------------------------------------------------------------------- buttons
class ButtonComponent(BaseComponent):
    """Flat rectangular button with hover and active states."""

    def __init__(self, label: str, on_click: Callable[[], None],
                 width: int = 120, height: int = 40, font_size: int = 14) -> None:
        self.label = label
        self.on_click = on_click
        self.width = width
        self.height = height
        self.font_size = font_size
        self.cx = 0.0
        self.cy = 0.0
        self.hovered = False
        self.active = False
        self.enabled = True
        self._text = arcade.Text(
            label, 0, 0, COLORS["header_text"], font_size,
            font_name=FONT, anchor_x="center", anchor_y="center", bold=True,
        )

    def place(self, cx: float, cy: float) -> None:
        self.cx = cx
        self.cy = cy

    def contains(self, x: float, y: float) -> bool:
        return (
            abs(x - self.cx) <= self.width / 2
            and abs(y - self.cy) <= self.height / 2
        )

    def draw(self, window) -> None:
        if self.active:
            fill = COLORS["button_face_active"]
        elif self.hovered and self.enabled:
            fill = COLORS["button_face_hover"]
        else:
            fill = COLORS["button_face"]
        border = COLORS["panel_border_bright"] if self.hovered else COLORS["panel_border"]
        _panel(self.cx, self.cy, self.width, self.height, fill, border, 2)
        self._text.text = self.label
        self._text.font_size = self.font_size
        self._text.color = COLORS["header_text"] if self.enabled else COLORS["muted_text"]
        self._text.x = self.cx
        self._text.y = self.cy
        self._text.draw()

    def on_mouse_motion(self, window, x: float, y: float) -> None:
        self.hovered = self.contains(x, y)

    def on_mouse_press(self, window, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.enabled and self.contains(x, y):
            self.on_click()
            return True
        return False


class ButtonBarComponent(ToggleableComponent):
    """Row of buttons anchored bottom-center."""

    def __init__(self, buttons: Sequence[ButtonComponent], bottom: int = 84,
                 gap: int = 12, visible: bool = True) -> None:
        super().__init__(visible)
        self.buttons = list(buttons)
        self.bottom = bottom
        self.gap = gap

    def _layout(self, window) -> None:
        total = sum(b.width for b in self.buttons) + self.gap * (len(self.buttons) - 1)
        x = window.width / 2 - total / 2
        for b in self.buttons:
            b.place(x + b.width / 2, self.bottom + b.height / 2)
            x += b.width + self.gap

    def on_resize(self, window) -> None:
        self._layout(window)

    def draw(self, window) -> None:
        if not self._visible:
            return
        self._layout(window)
        for b in self.buttons:
            b.draw(window)

    def on_mouse_motion(self, window, x: float, y: float) -> None:
        if not self._visible:
            return
        for b in self.buttons:
            b.on_mouse_motion(window, x, y)

    def on_mouse_press(self, window, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self._visible:
            return False
        for b in self.buttons:
            if b.on_mouse_press(window, x, y, button, modifiers):
                return True
        return False


# ------------------------------------------------------------- header / banner
class SessionInfoComponent(ToggleableComponent):
    """Top-center banner: app name, state, speech backend, word count."""

    def __init__(self, visible: bool = True) -> None:
        super().__init__(visible)
        self.info = {}
        self._text = arcade.Text("", 0, 0, COLORS["header_text"], 14, font_name=FONT,
                                 anchor_x="center", anchor_y="center")

    def set_info(self, **kwargs) -> None:
        self.info.update(kwargs)

    def draw(self, window) -> None:
        if not self._visible or not self.info:
            return
        banner_height = 64
        banner_width = min(920, window.width - 40)
        cx = window.width / 2
        top = window.height - 12
        _panel(cx, top - banner_height / 2, banner_width, banner_height,
               COLORS["panel_background_solid"], COLORS["panel_border"], 2)

        title = self.info.get("title", "")
        subtitle_parts = [p for p in self.info.get("subtitle", []) if p]

        self._text.text = title
        self._text.font_size = 18
        self._text.bold = True
        self._text.color = COLORS["header_text"]
        self._text.x = cx
        self._text.y = top - 22
        self._text.draw()

        self._text.text = " | ".join(subtitle_parts)
        self._text.font_size = 12
        self._text.bold = False
        self._text.color = COLORS["body_text"]
        self._text.y = top - 46
        self._text.draw()


# ----------------------------------------------------------------- word arena
class WordFlashComponent(ToggleableComponent):
    """Center stage: the flashed word, the type-in field and the caret.

    The flash fades out over the tail of its lifetime so a long word never
    lingers as a solid hint.
    """

    def __init__(self, visible: bool = True) -> None:
        super().__init__(visible)
        self.word = ""
        self.alpha = 0.0
        self.masked = False
        self._word_text = arcade.Text("", 0, 0, COLORS["flash_word"], 44, font_name=FONT,
                                      anchor_x="center", anchor_y="center", bold=True)
        self._typed_text = arcade.Text("", 0, 0, COLORS["header_text"], 30, font_name=FONT,
                                       anchor_x="center", anchor_y="center")
        self._hint = arcade.Text("", 0, 0, COLORS["muted_text"], 13, font_name=FONT,
                                 anchor_x="center", anchor_y="center")

    def set_flash(self, word: str, alpha: float) -> None:
        self.word = word
        self.alpha = max(0.0, min(1.0, alpha))

    def draw(self, window) -> None:
        cx = window.width / 2
        cy = window.height / 2 + 40

        # Flash line (always occupies its slot so the field never shifts).
        if self._visible and self.word and self.alpha > 0:
            r, g, b = COLORS["flash_word"]
            self._word_text.text = self.word
            self._word_text.color = (r, g, b, int(255 * self.alpha))
            self._word_text.x = cx
            self._word_text.y = cy + 60
            self._word_text.draw()
        elif not self._visible:
            self._hint.text = "word flash off (F2)"
            self._hint.color = COLORS["pending"]
            self._hint.x = cx
            self._hint.y = cy + 60
            self._hint.draw()

        # Input field.
        field_w = min(560, window.width - 120)
        field_h = 64
        session = window.session
        border = COLORS["panel_border"]
        if session.typed:
            border = (COLORS["correct"] if session.current_word.startswith(session.typed)
                      else COLORS["incorrect"])
        _panel(cx, cy - 10, field_w, field_h, COLORS["panel_background"], border, 2)

        if session.typed:
            self._typed_text.text = session.typed
            self._typed_text.color = COLORS["header_text"]
        else:
            self._typed_text.text = "type the word, then SPACE"
            self._typed_text.color = COLORS["pending"]
        self._typed_text.x = cx
        self._typed_text.y = cy - 10
        self._typed_text.draw()

        # Blinking caret to the right of the typed text.
        if window.caret_on and session.is_active:
            caret_x = cx + self._typed_text.content_width / 2 + 8 if session.typed else cx + 4
            arcade.draw_line(caret_x, cy - 30, caret_x, cy + 10, COLORS["caret"], 2)

        self._hint.text = (f"word {min(session.index + 1, session.total_words)}"
                           f" / {session.total_words}")
        self._hint.color = COLORS["muted_text"]
        self._hint.x = cx
        self._hint.y = cy - 58
        self._hint.draw()


# -------------------------------------------------------------- side panels
class StatsPanelComponent(ToggleableComponent):
    """Live WPM / accuracy / elapsed panel, top-left under the banner."""

    def __init__(self, left: int = 20, width: int = 250, top_offset: int = 92,
                 visible: bool = True) -> None:
        super().__init__(visible)
        self.left = left
        self.width = width
        self.top_offset = top_offset
        self.rows: List[Tuple[str, str, tuple]] = []
        self._header = arcade.Text("", 0, 0, COLORS["header_text"], 16, font_name=FONT,
                                   bold=True, anchor_y="top")
        self._label = arcade.Text("", 0, 0, COLORS["body_text"], 13, font_name=FONT,
                                  anchor_y="center")
        self._value = arcade.Text("", 0, 0, COLORS["header_text"], 13, font_name=FONT,
                                  anchor_x="right", anchor_y="center", bold=True)

    def set_rows(self, rows: List[Tuple[str, str, tuple]]) -> None:
        self.rows = rows

    def draw(self, window) -> None:
        if not self._visible or not self.rows:
            return
        row_h = 24
        height = 44 + row_h * len(self.rows)
        top = window.height - self.top_offset
        cx = self.left + self.width / 2
        _panel(cx, top - height / 2, self.width, height)

        self._header.text = "Live Stats"
        self._header.x = self.left + 12
        self._header.y = top - 10
        self._header.draw()

        y = top - 44
        for label, value, color in self.rows:
            self._label.text = label
            self._label.x = self.left + 12
            self._label.y = y
            self._label.draw()
            self._value.text = value
            self._value.color = color
            self._value.x = self.left + self.width - 12
            self._value.y = y
            self._value.draw()
            y -= row_h


class WordHistoryComponent(ToggleableComponent):
    """Right-side scoreboard of submitted words, newest first.

    Correct words are green, wrong ones red with the expected spelling shown.
    """

    def __init__(self, right_margin: int = 20, width: int = 280, top_offset: int = 92,
                 max_rows: int = 14, visible: bool = True) -> None:
        super().__init__(visible)
        self.right_margin = right_margin
        self.width = width
        self.top_offset = top_offset
        self.max_rows = max_rows
        self.entries: List[dict] = []
        self._header = arcade.Text("", 0, 0, COLORS["header_text"], 16, font_name=FONT,
                                   bold=True, anchor_y="top")
        self._row = arcade.Text("", 0, 0, COLORS["body_text"], 13, font_name=FONT,
                                anchor_y="center")
        self._badge = arcade.Text("", 0, 0, COLORS["body_text"], 11, font_name=FONT,
                                  anchor_x="right", anchor_y="center")

    def set_entries(self, entries: List[dict]) -> None:
        self.entries = entries

    def draw(self, window) -> None:
        if not self._visible:
            return
        rows = self.entries[-self.max_rows:][::-1]
        row_h = 24
        height = 48 + row_h * max(1, len(rows))
        left = window.width - self.right_margin - self.width
        top = window.height - self.top_offset
        cx = left + self.width / 2
        _panel(cx, top - height / 2, self.width, height)

        self._header.text = "Word History"
        self._header.x = left + 12
        self._header.y = top - 10
        self._header.draw()

        if not rows:
            self._row.text = "no words submitted yet"
            self._row.color = COLORS["pending"]
            self._row.x = left + 12
            self._row.y = top - 46
            self._row.draw()
            return

        y = top - 46
        for entry in rows:
            correct = entry["correct"]
            color = COLORS["correct"] if correct else COLORS["incorrect"]
            arcade.draw_circle_filled(left + 18, y, 4, color)
            self._row.text = entry["typed"][:20]
            self._row.color = COLORS["body_text"] if correct else color
            self._row.x = left + 32
            self._row.y = y
            self._row.draw()
            self._badge.text = f"{entry['index'] + 1}" if correct else f"→ {entry['expected'][:12]}"
            self._badge.color = COLORS["muted_text"] if correct else COLORS["amber"]
            self._badge.x = left + self.width - 12
            self._badge.y = y
            self._badge.draw()
            y -= row_h


# ------------------------------------------------------------------ progress
class ProgressBarComponent(ToggleableComponent):
    """Bottom progress bar with a per-word marker for each submitted result.

    Green tick = correct, red tick = wrong, gray tick = not reached. A white
    playhead sits at the current word.
    """

    def __init__(self, left_margin: int = 40, right_margin: int = 40,
                 bottom: int = 34, height: int = 22, visible: bool = True) -> None:
        super().__init__(visible)
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.bottom = bottom
        self.height = height
        self.total = 0
        self.results: List[bool] = []
        self.current = 0
        self._label = arcade.Text("", 0, 0, COLORS["body_text"], 11, font_name=FONT,
                                  anchor_x="center", anchor_y="top")

    def set_progress(self, total: int, results: List[bool], current: int) -> None:
        self.total = max(1, total)
        self.results = results
        self.current = current

    def draw(self, window) -> None:
        if not self._visible:
            return
        bar_left = self.left_margin
        bar_width = max(120, window.width - self.left_margin - self.right_margin)
        cy = self.bottom + self.height / 2

        _panel(bar_left + bar_width / 2, cy, bar_width, self.height,
               COLORS["panel_background"], COLORS["panel_border"], 2)

        done = len(self.results)
        if done:
            fill_w = (done / self.total) * bar_width
            arcade.draw_rect_filled(
                arcade.XYWH(bar_left + fill_w / 2, cy, fill_w, self.height - 4),
                COLORS["accent_dim"],
            )

        slot = bar_width / self.total
        for i in range(self.total):
            x = bar_left + slot * (i + 0.5)
            if i < done:
                color = COLORS["correct"] if self.results[i] else COLORS["incorrect"]
            else:
                color = COLORS["pending"]
            arcade.draw_line(x, self.bottom + 4, x, self.bottom + self.height - 4, color, 2)

        playhead_x = bar_left + slot * min(self.current, self.total)
        arcade.draw_line(playhead_x, self.bottom - 2, playhead_x,
                         self.bottom + self.height + 2, COLORS["playhead"], 2)

        self._label.text = f"{done} / {self.total} words"
        self._label.x = bar_left + bar_width / 2
        self._label.y = self.bottom - 4
        self._label.draw()


# -------------------------------------------------------- legend & help popup
class LegendComponent(ToggleableComponent):
    """Bottom-left clickable hint that opens the controls popup."""

    def __init__(self, x: int = 20, y: int = 76, visible: bool = True) -> None:
        super().__init__(visible)
        self.x = x
        self.y = y
        self.lines = ["Help (click or F1)"]
        self._text = arcade.Text("", 0, 0, COLORS["muted_text"], 13, font_name=FONT,
                                 anchor_y="center")

    def _hit_box(self) -> Tuple[float, float, float, float]:
        width = max(140.0, self._text.content_width or 140.0)
        return self.x - 6, self.y - 12, self.x + width + 6, self.y + 12

    def draw(self, window) -> None:
        if not self._visible:
            return
        for i, line in enumerate(self.lines):
            self._text.text = line
            self._text.color = COLORS["body_text"] if i == 0 else COLORS["muted_text"]
            self._text.x = self.x
            self._text.y = self.y - i * 20
            self._text.draw()

    def on_mouse_press(self, window, x: float, y: float, button: int, modifiers: int) -> bool:
        left, bottom, right, top = self._hit_box()
        if left <= x <= right and bottom <= y <= top:
            popup = getattr(window, "controls_popup", None)
            if popup:
                popup.toggle_visibility()
            return True
        return False


class ControlsPopupComponent(ToggleableComponent):
    """Modal controls list with a header bar and a close button."""

    def __init__(self, width: int = 420, height: int = 380, visible: bool = False) -> None:
        super().__init__(visible)
        self.width = width
        self.height = height
        self.rows = list(CONTROLS_HELP)
        self.cx = 0.0
        self.cy = 0.0
        self._header = arcade.Text("", 0, 0, COLORS["header_text"], 16, font_name=FONT,
                                   bold=True, anchor_y="center")
        self._key = arcade.Text("", 0, 0, COLORS["amber"], 12, font_name=FONT,
                                anchor_y="center", bold=True)
        self._desc = arcade.Text("", 0, 0, COLORS["body_text"], 12, font_name=FONT,
                                 anchor_y="center")
        self._close = arcade.Text("x", 0, 0, COLORS["header_text"], 14, font_name=FONT,
                                  anchor_x="center", anchor_y="center", bold=True)

    def draw(self, window) -> None:
        if not self._visible:
            return
        self.cx = window.width / 2
        self.cy = window.height / 2
        _panel(self.cx, self.cy, self.width, self.height,
               COLORS["panel_background_solid"], COLORS["panel_border_bright"], 2)

        top = self.cy + self.height / 2
        left = self.cx - self.width / 2
        header_h = 34
        arcade.draw_rect_filled(
            arcade.XYWH(self.cx, top - header_h / 2, self.width, header_h),
            COLORS["button_face"],
        )
        self._header.text = "Controls"
        self._header.x = left + 14
        self._header.y = top - header_h / 2
        self._header.draw()

        close_cx = left + self.width - 20
        close_cy = top - header_h / 2
        arcade.draw_rect_filled(arcade.XYWH(close_cx, close_cy, 22, 22), COLORS["incorrect"])
        self._close.x = close_cx
        self._close.y = close_cy
        self._close.draw()

        y = top - header_h - 22
        for key, desc in self.rows:
            self._key.text = key
            self._key.x = left + 18
            self._key.y = y
            self._key.draw()
            self._desc.text = desc
            self._desc.x = left + 130
            self._desc.y = y
            self._desc.draw()
            y -= 26

    def on_mouse_press(self, window, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self._visible:
            return False
        half_w, half_h = self.width / 2, self.height / 2
        inside = abs(x - self.cx) <= half_w and abs(y - self.cy) <= half_h
        if not inside:
            self._visible = False
            return True
        top = self.cy + half_h
        left = self.cx - half_w
        close_cx = left + self.width - 20
        close_cy = top - 17
        if abs(x - close_cx) <= 12 and abs(y - close_cy) <= 12:
            self._visible = False
        return True


# ------------------------------------------------------------------- results
class ResultsComponent(ToggleableComponent):
    """Centered results card shown once the test ends."""

    def __init__(self, width: int = 520, visible: bool = False) -> None:
        super().__init__(visible)
        self.width = width
        self.tiles: List[Tuple[str, str, tuple]] = []
        self.footer = ""
        self._header = arcade.Text("", 0, 0, COLORS["header_text"], 22, font_name=FONT,
                                   bold=True, anchor_x="center", anchor_y="center")
        self._tile_value = arcade.Text("", 0, 0, COLORS["header_text"], 28, font_name=FONT,
                                       bold=True, anchor_x="center", anchor_y="center")
        self._tile_label = arcade.Text("", 0, 0, COLORS["muted_text"], 11, font_name=FONT,
                                       anchor_x="center", anchor_y="center")
        self._footer = arcade.Text("", 0, 0, COLORS["body_text"], 13, font_name=FONT,
                                   anchor_x="center", anchor_y="center")

    def set_results(self, tiles: List[Tuple[str, str, tuple]], footer: str) -> None:
        self.tiles = tiles
        self.footer = footer

    def draw(self, window) -> None:
        if not self._visible or not self.tiles:
            return
        height = 230
        cx = window.width / 2
        cy = window.height / 2 + 20
        _panel(cx, cy, self.width, height,
               COLORS["panel_background_solid"], COLORS["panel_border_bright"], 2)

        top = cy + height / 2
        self._header.text = "Results"
        self._header.x = cx
        self._header.y = top - 30
        self._header.draw()

        tile_w = self.width / max(1, len(self.tiles))
        left = cx - self.width / 2
        for i, (label, value, color) in enumerate(self.tiles):
            tile_cx = left + tile_w * (i + 0.5)
            self._tile_value.text = value
            self._tile_value.color = color
            self._tile_value.x = tile_cx
            self._tile_value.y = cy + 15
            self._tile_value.draw()
            self._tile_label.text = label.upper()
            self._tile_label.x = tile_cx
            self._tile_label.y = cy - 15
            self._tile_label.draw()
            if i:
                arcade.draw_line(left + tile_w * i, cy - 30, left + tile_w * i, cy + 40,
                                 COLORS["grid"], 1)

        self._footer.text = self.footer
        self._footer.x = cx
        self._footer.y = cy - height / 2 + 28
        self._footer.draw()


# -------------------------------------------------------------------- splash
class StartScreenComponent(ToggleableComponent):
    """Idle screen: big title, source paragraph preview and the start prompt."""

    def __init__(self, visible: bool = True) -> None:
        super().__init__(visible)
        self.title = ""
        self.subtitle = ""
        self.paragraph = ""
        self._title = arcade.Text("", 0, 0, COLORS["header_text"], 56, font_name=FONT,
                                  bold=True, anchor_x="center", anchor_y="center")
        self._subtitle = arcade.Text("", 0, 0, COLORS["accent"], 16, font_name=FONT,
                                     anchor_x="center", anchor_y="center")
        self._paragraph = arcade.Text("", 0, 0, COLORS["body_text"], 14, font_name=FONT,
                                      anchor_x="center", anchor_y="center", multiline=True,
                                      width=640, align="center")
        self._prompt = arcade.Text("", 0, 0, COLORS["muted_text"], 14, font_name=FONT,
                                   anchor_x="center", anchor_y="center")

    def set_content(self, title: str, subtitle: str, paragraph: str) -> None:
        self.title = title
        self.subtitle = subtitle
        self.paragraph = paragraph

    def draw(self, window) -> None:
        if not self._visible:
            return
        cx = window.width / 2
        cy = window.height / 2 + 60

        self._title.text = self.title
        self._title.x = cx
        self._title.y = cy + 70
        self._title.draw()

        arcade.draw_line(cx - 150, cy + 34, cx + 150, cy + 34, COLORS["accent"], 2)

        self._subtitle.text = self.subtitle
        self._subtitle.x = cx
        self._subtitle.y = cy + 10
        self._subtitle.draw()

        preview_w = min(700, window.width - 120)
        _panel(cx, cy - 70, preview_w, 100)
        self._paragraph.text = self.paragraph
        self._paragraph.width = int(preview_w - 40)
        self._paragraph.x = cx
        self._paragraph.y = cy - 70
        self._paragraph.draw()

        self._prompt.text = "click START or press SPACE to begin"
        self._prompt.x = cx
        self._prompt.y = cy - 150
        self._prompt.draw()


class ToastComponent(BaseComponent):
    """Short transient message just above the button bar."""

    def __init__(self, bottom: int = 140) -> None:
        self.bottom = bottom
        self.message = ""
        self.alpha = 0.0
        self._text = arcade.Text("", 0, 0, COLORS["amber"], 13, font_name=FONT,
                                 anchor_x="center", anchor_y="center")

    def show(self, message: str) -> None:
        self.message = message
        self.alpha = 1.0

    def update(self, delta: float) -> None:
        if self.alpha > 0:
            self.alpha = max(0.0, self.alpha - delta / 2.0)

    def draw(self, window) -> None:
        if not self.message or self.alpha <= 0:
            return
        r, g, b = COLORS["amber"]
        self._text.text = self.message
        self._text.color = (r, g, b, int(255 * self.alpha))
        self._text.x = window.width / 2
        self._text.y = self.bottom
        self._text.draw()
