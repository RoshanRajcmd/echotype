"""
Audio manager for text-to-speech functionality
"""

import pyttsx3
from typing import Callable, Optional


class AudioManager:
    """Manages text-to-speech operations"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 130)  # Speed (130 is slower for clarity)
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        self._setup_voices()
    
    def _setup_voices(self) -> None:
        """Setup the voice properties"""
        voices = self.engine.getProperty('voices')
        if voices:
            # Try to find English voice
            self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text: str, on_complete: Optional[Callable] = None) -> None:
        """
        Speak the given text
        
        Args:
            text: Text to speak
            on_complete: Optional callback when speech finishes
        """
        self.engine.say(text)
        self.engine.runAndWait()
        if on_complete:
            on_complete()
    
    def set_rate(self, rate: float) -> None:
        """Set speech rate (0.1-10, default 1)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', volume)
    
    def set_pitch(self, pitch: float) -> None:
        """Set pitch (0-2, default 1)"""
        self.engine.setProperty('pitch', pitch)
    
    def stop(self) -> None:
        """Stop speaking"""
        self.engine.stop()
