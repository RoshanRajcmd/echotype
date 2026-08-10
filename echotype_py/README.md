# EchoType (Python)

Python port of EchoType, the **vocalized typing practice** app: a word is spoken
aloud, you type what you hear and press `SPACE`. The UI follows the style of
[IAmTomShaw/f1-race-replay](https://github.com/IAmTomShaw/f1-race-replay) —
a single [Arcade](https://api.arcade.academy/) OpenGL window with hand-drawn dark
translucent panels, gray borders, white headers and light-gray body text, and
hotkey-toggled overlays.

The original Electron + React + TypeScript app is untouched on the default
branch; this port lives beside it in `echotype_py/`.

## Setup

Requires Python 3.9+ and an OpenGL 3.3+ capable display.

```bash
cd echotype_py
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python main.py
```

Options:

| Flag | Purpose |
| --- | --- |
| `--text "..."` | dictate a custom sentence instead of the default paragraph |
| `--file words.txt` | read the practice text from a file |
| `--rate 190` | speech rate in words per minute (default 170) |
| `--no-flash` | start with the on-screen word flash disabled |
| `--speech-backend {pyttsx3,say}` | force a TTS backend instead of auto-detecting |

## Controls

| Key | Action |
| --- | --- |
| `SPACE` | start the test / submit the current word |
| `TAB` | repeat the current word |
| `BACKSPACE` | delete a character |
| `ESC` | end the test and show results (again to close the window) |
| `R` | restart, while idle or on the results screen |
| `P` | pause / resume |
| `F1` | controls popup (also click the bottom-left legend) |
| `F2` | word flash on / off |
| `F3` | progress bar |
| `F4` | word history panel |
| `F5` | controls legend |
| `-` / `+` | speech rate down / up |

## Screens

* **Start** — title, source paragraph preview, `START` button.
* **Typing** — flashed word that fades out, input field whose border turns green
  while the prefix matches and red once it diverges, blinking caret, live stats
  panel (WPM, net WPM, accuracy, correct count, elapsed), word history panel, and
  a bottom progress bar with one tick per word plus a white playhead.
* **Results** — WPM, net WPM, accuracy and time tiles with a correct-word summary.

## Layout

```
echotype_py/
  main.py                  # argparse entry point
  requirements.txt
  requirements-dev.txt
  pytest.ini
  src/
    constants.py           # app config, palette, key map, controls help
    session.py             # pure typing-session logic (no I/O, no Arcade)
    speech.py              # threaded TTS: pyttsx3 -> macOS `say` -> silent
    ui_components.py       # BaseComponent + drawn panels, buttons, popup
    echotype_window.py     # arcade.Window shell wiring state to components
  tests/
    test_session.py
```

`src/session.py` is a functional core: it holds no clock, no audio and no
drawing, and every call that needs the current time receives it as an argument.
`echotype_window.py` is the imperative shell that owns those side effects, which
is what makes the session logic directly unit-testable.

Speech runs on a dedicated worker thread so the render loop never blocks while a
word is spoken, and `pyttsx3` failures fall back to the macOS `say` binary and
then to a silent backend, so the app stays usable without audio.

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

## Notes

* Arcade needs a real OpenGL context, so the app does not run over plain SSH
  without a display. On conda installs an `Unable to create an OpenGL 3.3+
  context` error is usually fixed with
  `conda install -c conda-forge libstdcxx-ng`.
* `pyttsx3` selects a voice from `SPEECH["PREFERRED_VOICES"]` in
  `src/constants.py` when one is available, mirroring the voice preference the
  Electron build expressed via `SpeechSynthesisUtterance`.
