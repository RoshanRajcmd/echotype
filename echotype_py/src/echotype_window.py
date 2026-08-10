"""Arcade window for EchoType: imperative shell around `TypingSession`.

All state transitions go through the pure session object; this module only owns
side effects (clock, audio, keyboard, drawing).
"""

import time
from typing import List, Optional

import arcade

from . import constants as C
from .session import State, TypingSession, split_words
from .speech import Speaker
from .ui_components import (
    ButtonBarComponent,
    ButtonComponent,
    ControlsPopupComponent,
    LegendComponent,
    ProgressBarComponent,
    ResultsComponent,
    SessionInfoComponent,
    StartScreenComponent,
    StatsPanelComponent,
    ToastComponent,
    WordFlashComponent,
    WordHistoryComponent,
)

CARET_BLINK_SECONDS = 0.5


class EchoTypeWindow(arcade.Window):
    def __init__(self, paragraph: str = C.DEFAULT_PARAGRAPH,
                 rate: int = C.SPEECH["DEFAULT_RATE"],
                 flash: bool = C.FLASH["ENABLED"],
                 speech_backend: Optional[str] = None) -> None:
        super().__init__(
            width=C.APP["WINDOW_WIDTH"],
            height=C.APP["WINDOW_HEIGHT"],
            title=f"{C.APP['NAME']} - {C.APP['TAGLINE']}",
            resizable=True,
            center_window=True,
        )
        self.set_minimum_size(C.APP["MIN_WIDTH"], C.APP["MIN_HEIGHT"])
        self.background_color = C.COLORS["window_background"]

        self.paragraph = paragraph
        self.session = TypingSession(words=split_words(paragraph))
        self.speaker = Speaker(rate=rate, preferred_voices=C.SPEECH["PREFERRED_VOICES"],
                              backend=speech_backend)
        self.rate_index = self._nearest_rate_index(rate)

        # Flash state
        self.flash_word = ""
        self.flash_remaining = 0.0
        self.caret_on = True
        self._caret_timer = 0.0

        # Components
        self.session_info = SessionInfoComponent()
        self.start_screen = StartScreenComponent()
        self.word_flash = WordFlashComponent(visible=flash)
        self.stats_panel = StatsPanelComponent(visible=False)
        self.history = WordHistoryComponent(visible=False)
        self.progress_bar = ProgressBarComponent(visible=False)
        self.results = ResultsComponent()
        self.legend = LegendComponent()
        self.controls_popup = ControlsPopupComponent()
        self.toast = ToastComponent()

        self.start_button = ButtonComponent("START", self._on_start_button, width=150, height=44,
                                            font_size=16)
        self.repeat_button = ButtonComponent("REPEAT", self._repeat_word, width=120)
        self.pause_button = ButtonComponent("PAUSE", self._toggle_pause, width=120)
        self.restart_button = ButtonComponent("RESTART", self._restart, width=120)
        self.quit_button = ButtonComponent("END", self._end_test, width=120)
        self.button_bar = ButtonBarComponent(
            [self.start_button, self.repeat_button, self.pause_button,
             self.restart_button, self.quit_button]
        )

        # Draw order: background panels first, modal popup last.
        self.components = [
            self.session_info,
            self.start_screen,
            self.word_flash,
            self.stats_panel,
            self.history,
            self.progress_bar,
            self.results,
            self.button_bar,
            self.legend,
            self.toast,
            self.controls_popup,
        ]

        self._refresh_visibility()
        self.start_screen.set_content(
            C.APP["NAME"].upper(), C.APP["TAGLINE"], self.paragraph
        )

    # ------------------------------------------------------------- utilities
    @staticmethod
    def _now() -> float:
        return time.monotonic()

    @staticmethod
    def _nearest_rate_index(rate: int) -> int:
        rates = C.SPEECH["RATES"]
        return min(range(len(rates)), key=lambda i: abs(rates[i] - rate))

    def _speak(self, word: str) -> None:
        if not word:
            return
        self.speaker.interrupt()
        self.speaker.say(word)
        self.flash_word = word
        self.flash_remaining = C.FLASH["DURATION_MS"] / 1000.0

    def _refresh_visibility(self) -> None:
        state = self.session.state
        idle = state is State.IDLE
        finished = state is State.FINISHED
        playing = state in (State.RUNNING, State.PAUSED)

        self.start_screen.visible = idle
        self.results.visible = finished
        self.stats_panel.visible = playing or finished
        self.history.visible = playing or finished
        self.progress_bar.visible = playing or finished

        self.start_button.label = "START" if idle else "RESUME"
        self.start_button.enabled = idle or state is State.PAUSED
        self.repeat_button.enabled = state is State.RUNNING
        self.pause_button.enabled = playing
        self.pause_button.label = "RESUME" if state is State.PAUSED else "PAUSE"
        self.pause_button.active = state is State.PAUSED
        self.quit_button.enabled = playing
        self.restart_button.enabled = not idle

    # --------------------------------------------------------------- actions
    def _on_start_button(self) -> None:
        if self.session.state is State.PAUSED:
            self._toggle_pause()
        elif self.session.state is State.IDLE:
            self._start_test()

    def _start_test(self) -> None:
        word = self.session.start(self._now())
        self._speak(word)
        self._refresh_visibility()

    def _restart(self) -> None:
        self.speaker.interrupt()
        self.session.reset()
        self.flash_word = ""
        self.flash_remaining = 0.0
        self._refresh_visibility()
        self.toast.show("session reset")

    def _end_test(self) -> None:
        if self.session.state in (State.RUNNING, State.PAUSED):
            self.speaker.interrupt()
            self.session.finish(self._now())
            self.flash_remaining = 0.0
            self._refresh_visibility()

    def _toggle_pause(self) -> None:
        now = self._now()
        if self.session.state is State.RUNNING:
            self.session.pause(now)
            self.speaker.interrupt()
            self.toast.show("paused")
        elif self.session.state is State.PAUSED:
            self.session.resume(now)
            self._speak(self.session.current_word)
        self._refresh_visibility()

    def _repeat_word(self) -> None:
        if self.session.state is State.RUNNING:
            self._speak(self.session.current_word)

    def _submit_word(self) -> None:
        next_word = self.session.submit(self._now())
        if next_word:
            self._speak(next_word)
        elif self.session.state is State.FINISHED:
            self.speaker.interrupt()
            self.flash_remaining = 0.0
        self._refresh_visibility()

    def _change_rate(self, step: int) -> None:
        rates = C.SPEECH["RATES"]
        self.rate_index = max(0, min(len(rates) - 1, self.rate_index + step))
        self.speaker.set_rate(rates[self.rate_index])
        self.toast.show(f"speech rate {rates[self.rate_index]} wpm")

    # ---------------------------------------------------------------- events
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        key = arcade.key
        state = self.session.state

        if symbol == key.ESCAPE:
            if self.controls_popup.visible:
                self.controls_popup.visible = False
            elif state in (State.RUNNING, State.PAUSED):
                self._end_test()
            else:
                self.close()
            return

        if symbol == key.F1:
            self.controls_popup.toggle_visibility()
            return
        if symbol == key.F2:
            on = self.word_flash.toggle_visibility()
            self.toast.show(f"word flash {'on' if on else 'off'}")
            return
        if symbol == key.F3:
            self.progress_bar.toggle_visibility()
            return
        if symbol == key.F4:
            self.history.toggle_visibility()
            return
        if symbol == key.F5:
            self.legend.toggle_visibility()
            return
        if symbol in (key.MINUS, key.NUM_SUBTRACT):
            self._change_rate(-1)
            return
        if symbol in (key.PLUS, key.EQUAL, key.NUM_ADD):
            self._change_rate(1)
            return

        if symbol == key.SPACE:
            if state is State.IDLE:
                self._start_test()
            elif state is State.RUNNING:
                self._submit_word()
            elif state is State.PAUSED:
                self._toggle_pause()
            return

        if symbol == key.TAB and state is State.RUNNING:
            self._repeat_word()
            return

        if symbol == key.BACKSPACE:
            self.session.backspace()
            return

        # R / P are shortcuts only when they cannot be part of a typed word.
        if state in (State.IDLE, State.FINISHED):
            if symbol == key.R:
                self._restart()
                if state is State.FINISHED:
                    self._start_test()
            elif symbol == key.P:
                self._toggle_pause()
        elif state is State.PAUSED and symbol == key.P:
            self._toggle_pause()

    def on_text(self, text: str) -> None:
        """Character input; `on_key_press` already handled SPACE and controls."""
        if self.session.state is not State.RUNNING:
            return
        for ch in text:
            self.session.type_char(ch)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        for comp in self.components:
            comp.on_mouse_motion(self, x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for comp in reversed(self.components):
            if comp.on_mouse_press(self, x, y, button, modifiers):
                return

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        for comp in self.components:
            comp.on_resize(self)

    def on_update(self, delta_time: float) -> None:
        if self.flash_remaining > 0:
            self.flash_remaining = max(0.0, self.flash_remaining - delta_time)

        self._caret_timer += delta_time
        if self._caret_timer >= CARET_BLINK_SECONDS:
            self._caret_timer = 0.0
            self.caret_on = not self.caret_on

        self.toast.update(delta_time)
        self._sync_components()

    def _sync_components(self) -> None:
        now = self._now()
        session = self.session
        stats = session.stats(now)

        fade = C.FLASH["FADE_MS"] / 1000.0
        alpha = 1.0 if self.flash_remaining > fade else self.flash_remaining / fade
        self.word_flash.set_flash(
            self.flash_word if session.state is State.RUNNING else "", alpha
        )

        state_label = {
            State.IDLE: "READY",
            State.RUNNING: "IN PROGRESS",
            State.PAUSED: "PAUSED",
            State.FINISHED: "COMPLETE",
        }[session.state]
        voice = self.speaker.voice or "system default"
        self.session_info.set_info(
            title=f"{C.APP['NAME']} - {C.APP['TAGLINE']}",
            subtitle=[
                state_label,
                f"{session.total_words} words",
                f"voice: {voice}",
                f"{self.speaker.backend_name} @ {C.SPEECH['RATES'][self.rate_index]} wpm",
            ],
        )

        self.stats_panel.set_rows([
            ("WPM", str(stats.wpm), C.COLORS["accent"]),
            ("Net WPM", str(stats.net_wpm), C.COLORS["header_text"]),
            ("Accuracy", f"{stats.accuracy}%",
             C.COLORS["correct"] if stats.accuracy >= 80 else C.COLORS["amber"]),
            ("Correct", f"{stats.correct}/{stats.words}", C.COLORS["body_text"]),
            ("Elapsed", f"{stats.elapsed:.1f}s", C.COLORS["body_text"]),
        ])

        self.history.set_entries([
            {"index": r.index, "typed": r.typed, "expected": r.expected,
             "correct": r.correct}
            for r in session.results
        ])

        self.progress_bar.set_progress(
            session.total_words, [r.correct for r in session.results], session.index
        )

        if session.state is State.FINISHED:
            self.results.set_results(
                [
                    ("wpm", str(stats.wpm), C.COLORS["accent"]),
                    ("net wpm", str(stats.net_wpm), C.COLORS["header_text"]),
                    ("accuracy", f"{stats.accuracy}%",
                     C.COLORS["correct"] if stats.accuracy >= 80 else C.COLORS["amber"]),
                    ("time", f"{stats.elapsed:.1f}s", C.COLORS["body_text"]),
                ],
                f"{stats.correct} of {stats.words} words correct  -  press R to run it again",
            )

    def on_draw(self) -> None:
        self.clear()
        for comp in self.components:
            comp.draw(self)

    def on_close(self) -> None:
        self.speaker.shutdown()
        super().on_close()


def run(paragraph: str = C.DEFAULT_PARAGRAPH, rate: int = C.SPEECH["DEFAULT_RATE"],
        flash: bool = C.FLASH["ENABLED"], speech_backend: Optional[str] = None) -> None:
    EchoTypeWindow(paragraph=paragraph, rate=rate, flash=flash,
                   speech_backend=speech_backend)
    arcade.run()
