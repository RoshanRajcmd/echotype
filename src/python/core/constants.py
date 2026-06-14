"""
Constants and configuration for EchoType
"""

from dataclasses import dataclass


@dataclass
class AppConstants:
    """Application constants"""
    NAME = "EchoType"
    VERSION = "1.0.0"
    WINDOW_TITLE = "EchoType - Vocalized Typing Practice"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 700
    
    DEFAULT_PARAGRAPH = (
        "The quick brown fox jumps over the lazy dog. "
        "She walks to the store every morning. "
        "He enjoys reading books on weekends. "
        "They play soccer in the park. "
        "I like to drink coffee in the morning. "
        "Beautiful flowers bloom in spring. "
        "The sunset paints the sky orange and pink. "
        "Children laugh and play at the playground. "
        "Technology changes our world every day. "
        "Music brings joy to our hearts."
    )
    
    # Keyboard shortcuts
    START_KEY = "space"
    NEXT_WORD_KEY = "space"
    QUIT_KEY = "escape"
    
    # Colors (RGB tuples for PyQt6)
    PRIMARY_COLOR = (26, 26, 26)
    ACCENT_COLOR = (255, 193, 7)  # Amber
    TEXT_COLOR = (255, 255, 255)
    SUCCESS_COLOR = (76, 175, 80)  # Green
    ERROR_COLOR = (244, 67, 54)  # Red
    
    # Audio settings
    SPEECH_RATE = 130
    SPEECH_VOLUME = 0.9
    WORD_FLASH_DURATION = 700  # milliseconds
