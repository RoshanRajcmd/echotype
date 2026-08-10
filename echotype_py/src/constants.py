"""Static configuration for the EchoType Arcade app.

Mirrors the layout of the TypeScript `src/ui/components/constants.ts` while
adding the drawing palette used by the Arcade UI components.
"""

APP = {
    "NAME": "EchoType",
    "TAGLINE": "Vocalized Typing Practice",
    "WINDOW_WIDTH": 1280,
    "WINDOW_HEIGHT": 720,
    "MIN_WIDTH": 900,
    "MIN_HEIGHT": 600,
}

DEFAULT_PARAGRAPH = "This is a simple typing test for the Echotype application"

# Keys are resolved against arcade.key in the window; kept as names so the
# pure-logic modules stay free of any Arcade import.
KEYS = {
    "QUIT": "ESCAPE",
    "NEXT_WORD": "SPACE",
    "REPEAT_WORD": "TAB",
    "HELP": "F1",
    "TOGGLE_FLASH": "F2",
    "TOGGLE_PROGRESS": "F3",
    "TOGGLE_HISTORY": "F4",
    "TOGGLE_LEGEND": "F5",
    "RESTART": "R",  # only while idle / finished, otherwise it is typed text
}

SPEECH = {
    # Words per minute equivalents accepted by pyttsx3 / `say`.
    "RATES": [110, 130, 150, 170, 190, 220, 260],
    "DEFAULT_RATE": 170,
    "PREFERRED_VOICES": ["Daniel", "Google UK English", "Serena", "Karen", "Alex"],
}

FLASH = {
    "ENABLED": True,
    "DURATION_MS": 700,
    "FADE_MS": 250,
}

# Palette follows the reference project's convention: dark translucent panels,
# gray borders, white headers, light-gray body text, green/red status accents.
COLORS = {
    "window_background": (18, 18, 18),
    "panel_background": (30, 30, 30, 200),
    "panel_background_solid": (20, 20, 20, 220),
    "panel_border": (100, 100, 100),
    "panel_border_bright": (160, 160, 160),
    "header_text": (255, 255, 255),
    "body_text": (211, 211, 211),
    "muted_text": (140, 140, 140),
    "accent": (0, 180, 0),
    "accent_dim": (0, 110, 0),
    "correct": (0, 200, 90),
    "incorrect": (220, 50, 50),
    "pending": (80, 80, 80),
    "flash_word": (0, 220, 120),
    "caret": (255, 255, 255),
    "amber": (255, 165, 0),
    "warning": (255, 220, 0),
    "button_face": (45, 45, 45),
    "button_face_hover": (70, 70, 70),
    "button_face_active": (0, 140, 0),
    "playhead": (255, 255, 255),
    "grid": (40, 40, 40),
}

FONT = ("Menlo", "Consolas", "calibri", "arial")

CONTROLS_HELP = [
    ("SPACE", "submit word / start test"),
    ("TAB", "repeat the current word"),
    ("BACKSPACE", "delete a character"),
    ("ESC", "end the test and show results"),
    ("R", "restart (while idle or on results)"),
    ("P", "pause / resume (while idle or paused)"),
    ("F1", "toggle this controls popup"),
    ("F2", "toggle the word flash"),
    ("F3", "toggle the progress bar"),
    ("F4", "toggle the word history panel"),
    ("F5", "toggle the controls legend"),
    ("- / +", "speech rate down / up"),
]
