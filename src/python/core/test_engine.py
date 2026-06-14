"""
Test engine for managing typing test logic
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TestState(Enum):
    """States of the typing test"""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass
class TestResult:
    """Result of a typed word"""
    word: str
    correct: bool
    timestamp: float


@dataclass
class TestStats:
    """Statistics from a completed test"""
    wpm: int  # Words per minute
    accuracy: int  # Percentage accuracy
    time: float  # Total time in seconds
    correct_words: int
    total_words: int


class TestEngine:
    """Manages the typing test logic"""
    
    def __init__(self, words: List[str]):
        self.words = words
        self.current_index = 0
        self.results: List[TestResult] = []
        self.state = TestState.IDLE
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self) -> None:
        """Start the test"""
        self.state = TestState.RUNNING
        self.start_time = time.time()
        self.current_index = 0
        self.results = []
    
    def submit_word(self, typed_word: str) -> bool:
        """
        Submit a typed word
        
        Args:
            typed_word: The word the user typed
            
        Returns:
            True if correct, False if incorrect
        """
        if self.state != TestState.RUNNING or self.current_index >= len(self.words):
            return False
        
        correct = typed_word.strip() == self.words[self.current_index]
        self.results.append(TestResult(
            word=typed_word.strip(),
            correct=correct,
            timestamp=time.time()
        ))
        
        self.current_index += 1
        return correct
    
    def get_current_word(self) -> Optional[str]:
        """Get the current word to type"""
        if self.current_index < len(self.words):
            return self.words[self.current_index]
        return None
    
    def has_next_word(self) -> bool:
        """Check if there's a next word"""
        return self.current_index < len(self.words)
    
    def finish(self) -> Optional[TestStats]:
        """
        Finish the test and return statistics
        
        Returns:
            TestStats if test was running, None otherwise
        """
        if self.state == TestState.RUNNING:
            self.state = TestState.FINISHED
            self.end_time = time.time()
            return self._calculate_stats()
        return None
    
    def _calculate_stats(self) -> TestStats:
        """Calculate test statistics"""
        if not self.start_time or not self.end_time:
            return TestStats(0, 0, 0, 0, 0)
        
        total_time = self.end_time - self.start_time
        minutes = total_time / 60
        
        correct_count = sum(1 for r in self.results if r.correct)
        total_count = len(self.results)
        
        wpm = round(total_count / minutes) if minutes > 0 else 0
        accuracy = round((correct_count / total_count) * 100) if total_count > 0 else 0
        
        return TestStats(
            wpm=wpm,
            accuracy=accuracy,
            time=total_time,
            correct_words=correct_count,
            total_words=total_count
        )
