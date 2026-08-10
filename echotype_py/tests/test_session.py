import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.session import State, TypingSession, split_words  # noqa: E402


def make(words="alpha beta gamma"):
    return TypingSession(words=split_words(words))


def type_word(session, word, now):
    for ch in word:
        session.type_char(ch)
    return session.submit(now)


def test_split_words_drops_extra_whitespace():
    assert split_words("  one   two\nthree\t ") == ["one", "two", "three"]


def test_start_returns_first_word_and_sets_running():
    s = make()
    assert s.start(now=0.0) == "alpha"
    assert s.state is State.RUNNING
    assert s.started_at == 0.0


def test_submit_advances_and_returns_next_word():
    s = make()
    s.start(0.0)
    assert type_word(s, "alpha", 1.0) == "beta"
    assert s.index == 1
    assert s.typed == ""
    assert s.results[0].correct is True


def test_submit_records_incorrect_word():
    s = make()
    s.start(0.0)
    type_word(s, "alpna", 1.0)
    result = s.results[0]
    assert result.correct is False
    assert result.expected == "alpha"
    assert result.typed == "alpna"


def test_submit_empty_input_is_ignored():
    s = make()
    s.start(0.0)
    assert s.submit(1.0) is None
    assert s.results == []
    assert s.index == 0


def test_last_word_finishes_session():
    s = make("alpha beta")
    s.start(0.0)
    type_word(s, "alpha", 1.0)
    assert type_word(s, "beta", 2.0) is None
    assert s.state is State.FINISHED
    assert s.ended_at == 2.0


def test_type_char_ignores_space_and_non_running_state():
    s = make()
    s.type_char("a")
    assert s.typed == ""
    s.start(0.0)
    s.type_char(" ")
    s.type_char("a")
    assert s.typed == "a"


def test_backspace_removes_last_char():
    s = make()
    s.start(0.0)
    s.type_char("a")
    s.type_char("b")
    s.backspace()
    assert s.typed == "a"
    s.backspace()
    s.backspace()
    assert s.typed == ""


def test_pause_excludes_paused_time_from_elapsed():
    s = make()
    s.start(0.0)
    s.pause(2.0)
    s.resume(5.0)
    assert s.elapsed(6.0) == pytest.approx(3.0)
    assert s.paused_total == pytest.approx(3.0)


def test_finish_while_paused_counts_pause_once():
    s = make()
    s.start(0.0)
    s.pause(2.0)
    s.finish(4.0)
    assert s.state is State.FINISHED
    assert s.elapsed(10.0) == pytest.approx(2.0)


def test_stats_wpm_and_accuracy():
    s = make("alpha beta gamma four")
    s.start(0.0)
    type_word(s, "alpha", 15.0)
    type_word(s, "beta", 30.0)
    type_word(s, "wrong", 45.0)
    type_word(s, "four", 60.0)
    stats = s.stats(60.0)
    assert stats.words == 4
    assert stats.correct == 3
    assert stats.accuracy == 75
    assert stats.wpm == 4  # 4 words in exactly one minute
    assert stats.elapsed == pytest.approx(60.0)


def test_stats_on_untouched_session_is_zeroed():
    stats = make().stats(now=5.0)
    assert (stats.words, stats.wpm, stats.accuracy, stats.net_wpm) == (0, 0, 0, 0)


def test_progress_reflects_submitted_words():
    s = make("alpha beta gamma")
    s.start(0.0)
    assert s.progress() == 0.0
    type_word(s, "alpha", 1.0)
    assert s.progress() == pytest.approx(1 / 3)


def test_reset_clears_everything():
    s = make()
    s.start(0.0)
    type_word(s, "alpha", 1.0)
    s.reset()
    assert s.state is State.IDLE
    assert (s.index, s.typed, s.results, s.started_at) == (0, "", [], None)


def test_start_on_empty_word_list_stays_idle():
    s = TypingSession(words=[])
    assert s.start(0.0) == ""
    assert s.state is State.IDLE


def test_resume_only_applies_when_paused():
    s = make()
    s.start(0.0)
    s.resume(5.0)
    assert s.state is State.RUNNING
    assert s.paused_total == 0.0


def test_finish_on_idle_session_is_noop():
    s = make()
    s.finish(1.0)
    assert s.state is State.IDLE
    assert s.ended_at is None
