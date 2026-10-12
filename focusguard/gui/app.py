"""GUI Application Launcher for FocusGuard."""

import sys
from PySide6.QtWidgets import QApplication
from focusguard.gui.main_window import MainWindow

def run_gui():
    """Launch the FocusGuard PySide6 Desktop GUI."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    app.setApplicationName("FocusGuard")
    app.setApplicationDisplayName("FocusGuard")
    
    window = MainWindow()
    window.show()
    return app.exec()
