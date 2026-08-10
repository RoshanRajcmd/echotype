"""Pure typing-session logic.

No I/O, no Arcade, no clock access: every call that needs the current time takes
it as an argument so the caller (the Arcade window) owns all side effects.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class State(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass(frozen=True)
class WordResult:
    index: int
    expected: str
    typed: str
    correct: bool
    seconds: float


@dataclass(frozen=True)
class Stats:
    words: int
    correct: int
    accuracy: int
    wpm: int
    net_wpm: int
    elapsed: float


def split_words(text: str) -> List[str]:
    """Split source text into the words to be dictated."""
    return [w for w in text.split() if w]


@dataclass
class TypingSession:
    """Tracks progress through a word list.

    The caller drives it with `start`, `submit`, `pause`, `resume` and `finish`,
    passing a monotonic timestamp (seconds) for each.
    """

    words: List[str]
    state: State = State.IDLE
    index: int = 0
    typed: str = ""
    results: List[WordResult] = field(default_factory=list)
    started_at: Optional[float] = None
    ended_at: Optional[float] = None
    paused_at: Optional[float] = None
    paused_total: float = 0.0
    _word_started_at: Optional[float] = None

    # ------------------------------------------------------------------ state
    @property
    def total_words(self) -> int:
        return len(self.words)

    @property
    def current_word(self) -> str:
        if 0 <= self.index < len(self.words):
            return self.words[self.index]
        return ""

    @property
    def is_active(self) -> bool:
        return self.state is State.RUNNING

    def start(self, now: float) -> str:
        """Begin the test. Returns the word that should be spoken."""
        if self.state is State.RUNNING or not self.words:
            return self.current_word
        self.state = State.RUNNING
        self.index = 0
        self.typed = ""
        self.results = []
        self.started_at = now
        self.ended_at = None
        self.paused_at = None
        self.paused_total = 0.0
        self._word_started_at = now
        return self.current_word

    def pause(self, now: float) -> None:
        if self.state is not State.RUNNING:
            return
        self.state = State.PAUSED
        self.paused_at = now

    def resume(self, now: float) -> None:
        if self.state is not State.PAUSED:
            return
        if self.paused_at is not None:
            self.paused_total += now - self.paused_at
        self.paused_at = None
        self.state = State.RUNNING

    def finish(self, now: float) -> None:
        if self.state in (State.IDLE, State.FINISHED):
            if self.state is State.IDLE:
                return
        if self.state is State.PAUSED and self.paused_at is not None:
            self.paused_total += now - self.paused_at
            self.paused_at = None
        self.state = State.FINISHED
        self.ended_at = now

    def reset(self) -> None:
        self.state = State.IDLE
        self.index = 0
        self.typed = ""
        self.results = []
        self.started_at = None
        self.ended_at = None
        self.paused_at = None
        self.paused_total = 0.0
        self._word_started_at = None

    # ------------------------------------------------------------------ input
    def type_char(self, char: str) -> None:
        if self.state is not State.RUNNING:
            return
        if not char.isprintable() or char == " ":
            return
        self.typed += char

    def backspace(self) -> None:
        if self.state is State.RUNNING:
            self.typed = self.typed[:-1]

    def submit(self, now: float) -> Optional[str]:
        """Score the typed word and advance.

        Returns the next word to speak, or None when the test just ended or the
        submission was ignored (empty input / not running).
        """
        if self.state is not State.RUNNING:
            return None
        typed = self.typed.strip()
        if not typed:
            return None

        expected = self.current_word
        started = self._word_started_at if self._word_started_at is not None else now
        self.results.append(
            WordResult(
                index=self.index,
                expected=expected,
                typed=typed,
                correct=typed == expected,
                seconds=max(0.0, now - started),
            )
        )
        self.typed = ""

        next_index = self.index + 1
        if next_index < len(self.words):
            self.index = next_index
            self._word_started_at = now
            return self.current_word

        self.index = next_index
        self.finish(now)
        return None

    # ------------------------------------------------------------------ stats
    def elapsed(self, now: float) -> float:
        if self.started_at is None:
            return 0.0
        end = self.ended_at if self.ended_at is not None else now
        pauses = self.paused_total
        if self.state is State.PAUSED and self.paused_at is not None:
            pauses += now - self.paused_at
        return max(0.0, end - self.started_at - pauses)

    def stats(self, now: float) -> Stats:
        elapsed = self.elapsed(now)
        words = len(self.results)
        correct = sum(1 for r in self.results if r.correct)
        minutes = elapsed / 60.0
        wpm = int(round(words / minutes)) if minutes > 0 else 0
        chars = sum(len(r.typed) + 1 for r in self.results)
        net_wpm = int(round((chars / 5.0) / minutes)) if minutes > 0 else 0
        accuracy = int(round((correct / words) * 100)) if words else 0
        return Stats(
            words=words,
            correct=correct,
            accuracy=accuracy,
            wpm=wpm,
            net_wpm=net_wpm,
            elapsed=elapsed,
        )

    def progress(self) -> float:
        if not self.words:
            return 0.0
        return min(1.0, len(self.results) / len(self.words))
