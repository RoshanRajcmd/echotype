"""Text-to-speech for EchoType.

Replaces the browser `SpeechSynthesisUtterance` used by the Electron build.
Speaking happens on a dedicated worker thread so the Arcade render loop is never
blocked. Backends, in order of preference:

1. ``pyttsx3`` (cross platform, offline)
2. the macOS ``say`` binary
3. a silent no-op, so the app stays usable without audio
"""

import platform
import queue
import shutil
import subprocess
import threading
from typing import List, Optional

_STOP = object()


class _Backend:
    name = "none"
    available = False

    def voices(self) -> List[str]:
        return []

    def speak(self, word: str, rate: int, voice: Optional[str]) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        pass


class _NullBackend(_Backend):
    name = "silent"
    available = True

    def speak(self, word: str, rate: int, voice: Optional[str]) -> None:
        return


class _SayBackend(_Backend):
    """macOS `say`. One subprocess per word; killed on stop()."""

    name = "say"

    def __init__(self) -> None:
        self._binary = shutil.which("say") if platform.system() == "Darwin" else None
        self.available = self._binary is not None
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def voices(self) -> List[str]:
        if not self.available:
            return []
        try:
            out = subprocess.run(
                [self._binary, "-v", "?"], capture_output=True, text=True, timeout=5
            ).stdout
        except (OSError, subprocess.SubprocessError):
            return []
        names = []
        for line in out.splitlines():
            parts = line.split()
            if parts:
                names.append(parts[0])
        return names

    def speak(self, word: str, rate: int, voice: Optional[str]) -> None:
        if not self.available:
            return
        cmd = [self._binary, "-r", str(rate)]
        if voice:
            cmd += ["-v", voice]
        cmd.append(word)
        with self._lock:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            proc = self._proc
        proc.wait()
        with self._lock:
            if self._proc is proc:
                self._proc = None

    def stop(self) -> None:
        with self._lock:
            proc = self._proc
        if proc and proc.poll() is None:
            proc.terminate()


class _Pyttsx3Backend(_Backend):
    """pyttsx3. The engine is created lazily on the worker thread that uses it,
    since the macOS NSSpeechSynthesizer driver is not thread-portable."""

    name = "pyttsx3"

    def __init__(self) -> None:
        try:
            import pyttsx3  # noqa: F401
        except Exception:
            self.available = False
            self._module = None
            return
        self.available = True
        self._module = pyttsx3
        self._engine = None
        self._voice_map = {}

    def _ensure_engine(self):
        if self._engine is None:
            self._engine = self._module.init()
            for v in self._engine.getProperty("voices"):
                self._voice_map[v.name] = v.id
        return self._engine

    def voices(self) -> List[str]:
        if not self.available:
            return []
        try:
            engine = self._module.init()
            names = [v.name for v in engine.getProperty("voices")]
            for v in engine.getProperty("voices"):
                self._voice_map[v.name] = v.id
            return names
        except Exception:
            self.available = False
            return []

    def speak(self, word: str, rate: int, voice: Optional[str]) -> None:
        engine = self._ensure_engine()
        engine.setProperty("rate", rate)
        if voice and voice in self._voice_map:
            engine.setProperty("voice", self._voice_map[voice])
        engine.say(word)
        engine.runAndWait()

    def stop(self) -> None:
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass


def _pick_backend(prefer: Optional[str] = None) -> _Backend:
    candidates = [_Pyttsx3Backend(), _SayBackend()]
    if prefer:
        candidates.sort(key=lambda b: 0 if b.name == prefer else 1)
    for backend in candidates:
        if backend.available:
            return backend
    return _NullBackend()


class Speaker:
    """Queued, non-blocking speech.

    `say(word)` enqueues; the worker thread drains the queue. `interrupt()`
    drops anything pending so a repeat or a new word never queues up behind
    stale audio.
    """

    def __init__(
        self,
        rate: int = 170,
        preferred_voices: Optional[List[str]] = None,
        backend: Optional[str] = None,
    ) -> None:
        self.rate = rate
        self._backend = _pick_backend(backend)
        self._voice = self._choose_voice(preferred_voices or [])
        self._queue: "queue.Queue" = queue.Queue()
        self._thread = threading.Thread(
            target=self._run, name="echotype-speech", daemon=True
        )
        self._thread.start()

    @property
    def backend_name(self) -> str:
        return self._backend.name

    @property
    def voice(self) -> Optional[str]:
        return self._voice

    def _choose_voice(self, preferred: List[str]) -> Optional[str]:
        available = self._backend.voices()
        if not available:
            return None
        lowered = [(name, name.lower()) for name in available]
        for want in preferred:
            needle = want.lower()
            for name, low in lowered:
                if needle in low:
                    return name
        return None

    def set_rate(self, rate: int) -> None:
        self.rate = rate

    def say(self, word: str) -> None:
        if word:
            self._queue.put((word, self.rate, self._voice))

    def interrupt(self) -> None:
        """Drop queued words and cut off whatever is speaking now."""
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                break
            else:
                if item is _STOP:  # keep a shutdown request in flight
                    self._queue.put(_STOP)
                    break
                self._queue.task_done()
        self._backend.stop()

    def shutdown(self) -> None:
        self.interrupt()
        self._queue.put(_STOP)

    def _run(self) -> None:
        while True:
            item = self._queue.get()
            if item is _STOP:
                self._queue.task_done()
                return
            word, rate, voice = item
            try:
                self._backend.speak(word, rate, voice)
            except Exception:
                # A dead backend must not kill dictation: fall back and retry once.
                self._backend = _SayBackend()
                if not self._backend.available:
                    self._backend = _NullBackend()
                try:
                    self._backend.speak(word, rate, None)
                except Exception:
                    pass
            finally:
                self._queue.task_done()
