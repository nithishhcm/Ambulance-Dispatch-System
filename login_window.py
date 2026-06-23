"""
ui/login_window.py
==================
Secure login window with role-based authentication.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

from database.db_manager import DatabaseManager
from ui.styles import LOGIN_STYLE, COLORS


class LoginWindow(QWidget):
    """
    Login screen.
    Emits `login_successful(user_dict)` on valid credentials.
    """

    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self._build_ui()
        self.setStyleSheet(LOGIN_STYLE)

    def _build_ui(self):
        self.setWindowTitle("Ambulance Dispatch System — Login")
        self.setFixedSize(480, 560)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # ── Outer layout (centers the card) ──────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        # ── Card ─────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedSize(420, 500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(0)

        # Ambulance icon area
        icon_lbl = QLabel("🚑")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI", 48))
        icon_lbl.setFixedHeight(80)
        card_layout.addWidget(icon_lbl)

        # Title
        title = QLabel("Dispatch System")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Emergency Response Management")
        subtitle.setObjectName("login_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(30)

        # Username field
        user_label = QLabel("Username")
        user_label.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(user_label)
        card_layout.addSpacing(4)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFixedHeight(44)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(16)

        # Password field
        pass_label = QLabel("Password")
        pass_label.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(pass_label)
        card_layout.addSpacing(4)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.returnPressed.connect(self._attempt_login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(6)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(20)

        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setFixedHeight(48)
        self.login_btn.clicked.connect(self._attempt_login)
        card_layout.addWidget(self.login_btn)

        card_layout.addSpacing(16)

        # Hint
        hint = QLabel("Demo: admin / admin123  ·  dispatcher / dispatch123")
        hint.setObjectName("login_subtitle")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        card_layout.addWidget(hint)

        # Close button (top-right)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{ color: {COLORS['danger']}; }}
        """)
        close_btn.clicked.connect(self.close)

        # Overlay close button on card
        close_btn.setParent(card)
        close_btn.move(384, 8)

        outer.addWidget(card)

    def _attempt_login(self):
        """Validate credentials and emit signal on success."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("⚠ Please enter both username and password.")
            return

        user = self.db.authenticate_user(username, password)
        if user:
            self.error_label.setText("")
            self.login_successful.emit(user)
        else:
            self.error_label.setText("✗ Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()

    # ── Draggable frameless window ────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPos() - self._drag_pos)
