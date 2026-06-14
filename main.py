#!/usr/bin/env python3
"""
EchoType - Vocalized typing practice desktop application
Python version using PyQt6 for the UI
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.python.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
