"""
main.py
=======
Entry point for the Ambulance Dispatch System.

Starts the Qt application, shows the Login window,
and transitions to the Main window on successful authentication.

Usage:
    python main.py
"""

import sys
import os

# Ensure the project root is on the Python path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.login_window import LoginWindow
from ui.main_window  import MainWindow


def main():
    # ── Create Qt application ─────────────────────────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName("Ambulance Dispatch System")
    app.setOrganizationName("Emergency Response Inc.")

    # Set a clean default font
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    # ── Login window ──────────────────────────────────────────────────────
    login = LoginWindow()

    main_window: MainWindow = None   # Will hold the main window reference

    def on_login_success(user: dict):
        """Transition from login to main window."""
        nonlocal main_window

        login.close()

        main_window = MainWindow(user)
        main_window.show()
        main_window.raise_()

        # Wire logout back to login screen
        def on_logout():
            main_window.close()
            login.username_input.clear()
            login.password_input.clear()
            login.error_label.clear()
            login.show()
            login.username_input.setFocus()

        main_window.logout_requested.connect(on_logout)

    login.login_successful.connect(on_login_success)
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
