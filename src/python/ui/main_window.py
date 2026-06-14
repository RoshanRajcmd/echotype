"""
Main application window for EchoType
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from src.python.core.constants import AppConstants
from src.python.ui.home_screen import HomeScreen


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.app_constants = AppConstants()
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self) -> None:
        """Initialize the user interface"""
        self.setWindowTitle(self.app_constants.WINDOW_TITLE)
        self.setGeometry(100, 100, self.app_constants.WINDOW_WIDTH, self.app_constants.WINDOW_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Add home screen
        self.home_screen = HomeScreen()
        main_layout.addWidget(self.home_screen)
        
        central_widget.setLayout(main_layout)
    
    def apply_styles(self) -> None:
        """Apply styling to the window"""
        # Dark theme stylesheet
        dark_stylesheet = f"""
            QMainWindow {{
                background-color: rgb{self.app_constants.PRIMARY_COLOR};
            }}
            
            QWidget {{
                background-color: rgb{self.app_constants.PRIMARY_COLOR};
                color: rgb{self.app_constants.TEXT_COLOR};
            }}
            
            QPushButton {{
                background-color: rgb{self.app_constants.PRIMARY_COLOR};
                color: rgb{self.app_constants.TEXT_COLOR};
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            
            QPushButton:hover {{
                border: 2px solid rgb{self.app_constants.ACCENT_COLOR};
                background-color: rgba(255, 193, 7, 0.1);
            }}
            
            QPushButton:pressed {{
                background-color: rgba(255, 193, 7, 0.2);
            }}
            
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                color: rgb{self.app_constants.TEXT_COLOR};
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid rgb{self.app_constants.ACCENT_COLOR};
            }}
            
            QLabel {{
                color: rgb{self.app_constants.TEXT_COLOR};
            }}
        """
        
        self.setStyleSheet(dark_stylesheet)
