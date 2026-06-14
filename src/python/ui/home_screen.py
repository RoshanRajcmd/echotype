"""
Home screen/test screen for EchoType
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from src.python.core.constants import AppConstants
from src.python.core.audio_manager import AudioManager
from src.python.core.test_engine import TestEngine


class SpeakWorkerThread(QThread):
    """Worker thread for speaking (prevents UI blocking)"""
    finished = pyqtSignal()
    
    def __init__(self, audio_manager: AudioManager, text: str):
        super().__init__()
        self.audio_manager = audio_manager
        self.text = text
    
    def run(self):
        self.audio_manager.speak(self.text)
        self.finished.emit()


class HomeScreen(QWidget):
    """Home screen displaying the typing test"""
    
    def __init__(self):
        super().__init__()
        self.constants = AppConstants()
        self.audio_manager = AudioManager()
        
        # Parse default paragraph into words
        words = self.constants.DEFAULT_PARAGRAPH.split()
        self.test_engine = TestEngine(words)
        
        # State variables
        self.is_testing = False
        self.current_word = ""
        self.speak_thread = None
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel(self.constants.NAME)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Start button (shown when not testing)
        self.start_button = QPushButton("Start Test")
        start_font = QFont()
        start_font.setPointSize(20)
        self.start_button.setFont(start_font)
        self.start_button.setMinimumHeight(80)
        self.start_button.clicked.connect(self.start_test)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 0.3);
                border: 2px solid rgb(76, 175, 80);
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.5);
            }
        """)
        main_layout.addWidget(self.start_button)
        
        # Test area (hidden initially)
        test_widget = QWidget()
        test_layout = QVBoxLayout(test_widget)
        test_layout.setSpacing(15)
        
        # Current word display
        self.word_display = QLabel()
        word_font = QFont()
        word_font.setPointSize(24)
        word_font.setBold(True)
        self.word_display.setFont(word_font)
        self.word_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_display.setStyleSheet("color: rgb(76, 175, 80);")
        self.word_display.setMinimumHeight(50)
        test_layout.addWidget(self.word_display)
        
        # Input field
        self.input_field = QLineEdit()
        input_font = QFont()
        input_font.setPointSize(16)
        self.input_field.setFont(input_font)
        self.input_field.setMinimumHeight(50)
        self.input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_field.setPlaceholderText("Type the word and press SPACE...")
        self.input_field.keyPressEvent = self.handle_key_press
        test_layout.addWidget(self.input_field)
        
        # Instructions
        instructions = QLabel("Press SPACE to submit a word • Press ESC to quit")
        inst_font = QFont()
        inst_font.setPointSize(11)
        instructions.setFont(inst_font)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: rgb(150, 150, 150);")
        test_layout.addWidget(instructions)
        
        # Typed words display
        self.results_display = QLabel()
        results_font = QFont()
        results_font.setPointSize(12)
        self.results_display.setFont(results_font)
        self.results_display.setWordWrap(True)
        self.results_display.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.results_display.setMinimumHeight(100)
        test_layout.addWidget(self.results_display)
        
        self.test_area = test_widget
        self.test_area.setVisible(False)
        main_layout.addWidget(self.test_area)
        
        # Results area (hidden initially)
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        results_title = QLabel("Results")
        results_title_font = QFont()
        results_title_font.setPointSize(20)
        results_title_font.setBold(True)
        results_title.setFont(results_title_font)
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(results_title)
        
        # Results grid
        results_grid = QGridLayout()
        results_grid.setSpacing(20)
        
        # WPM
        wpm_label = QLabel("WPM:")
        wpm_font = QFont()
        wpm_font.setPointSize(14)
        wpm_label.setFont(wpm_font)
        self.wpm_value = QLabel("0")
        self.wpm_value.setFont(wpm_font)
        self.wpm_value.setStyleSheet(f"color: rgb{self.constants.ACCENT_COLOR};")
        results_grid.addWidget(wpm_label, 0, 0)
        results_grid.addWidget(self.wpm_value, 0, 1)
        
        # Accuracy
        acc_label = QLabel("Accuracy:")
        acc_label.setFont(wpm_font)
        self.acc_value = QLabel("0%")
        self.acc_value.setFont(wpm_font)
        self.acc_value.setStyleSheet(f"color: rgb{self.constants.ACCENT_COLOR};")
        results_grid.addWidget(acc_label, 1, 0)
        results_grid.addWidget(self.acc_value, 1, 1)
        
        # Time
        time_label = QLabel("Time:")
        time_label.setFont(wpm_font)
        self.time_value = QLabel("0.0s")
        self.time_value.setFont(wpm_font)
        self.time_value.setStyleSheet(f"color: rgb{self.constants.ACCENT_COLOR};")
        results_grid.addWidget(time_label, 2, 0)
        results_grid.addWidget(self.time_value, 2, 1)
        
        results_layout.addLayout(results_grid)
        
        # Restart button
        restart_button = QPushButton("Try Again")
        restart_button.setMinimumHeight(60)
        restart_button.setFont(start_font)
        restart_button.clicked.connect(self.restart_test)
        results_layout.addWidget(restart_button)
        
        self.results_area = results_widget
        self.results_area.setVisible(False)
        main_layout.addWidget(self.results_area)
        
        main_layout.addStretch()
    
    def start_test(self) -> None:
        """Start the typing test"""
        self.is_testing = True
        self.test_engine.start()
        self.start_button.setVisible(False)
        self.test_area.setVisible(True)
        self.results_area.setVisible(False)
        
        # Speak the first word
        self.speak_next_word()
        self.input_field.setFocus()
    
    def speak_next_word(self) -> None:
        """Speak the next word"""
        word = self.test_engine.get_current_word()
        if word:
            self.current_word = word
            # Flash the word
            self.word_display.setText(word)
            # Schedule fade-out
            QTimer.singleShot(self.constants.WORD_FLASH_DURATION, lambda: self.word_display.setText(""))
            
            # Speak in background thread
            self.speak_thread = SpeakWorkerThread(self.audio_manager, word)
            self.speak_thread.start()
    
    def handle_key_press(self, event) -> None:
        """Handle keyboard input"""
        if event.key() == Qt.Key.Key_Escape:
            self.end_test()
        elif event.key() == Qt.Key.Key_Space:
            event.accept()
            self.submit_word()
        else:
            super(type(self.input_field), self.input_field).keyPressEvent(event)
    
    def submit_word(self) -> None:
        """Submit the typed word"""
        typed = self.input_field.text().strip()
        if not typed:
            return
        
        # Check if correct
        is_correct = self.test_engine.submit_word(typed)
        
        # Update display with color coding
        color = "rgb(76, 175, 80)" if is_correct else "rgb(244, 67, 54)"
        current_display = self.results_display.text()
        if current_display:
            current_display += " "
        current_display += f'<span style="color: {color};">{typed}</span>'
        self.results_display.setText(current_display)
        
        # Clear input
        self.input_field.clear()
        
        # Next word or finish
        if self.test_engine.has_next_word():
            self.speak_next_word()
        else:
            self.end_test()
    
    def end_test(self) -> None:
        """End the test and show results"""
        self.is_testing = False
        stats = self.test_engine.finish()
        
        if stats:
            self.wpm_value.setText(str(stats.wpm))
            self.acc_value.setText(f"{stats.accuracy}%")
            self.time_value.setText(f"{stats.time:.1f}s")
        
        self.test_area.setVisible(False)
        self.results_area.setVisible(True)
    
    def restart_test(self) -> None:
        """Restart the test"""
        words = self.constants.DEFAULT_PARAGRAPH.split()
        self.test_engine = TestEngine(words)
        self.results_display.setText("")
        self.input_field.clear()
        self.word_display.setText("")
        self.start_test()
