"""
ui/main_window.py
==================
Main application shell.
Houses the sidebar navigation and a QStackedWidget for all panels.
Receives the authenticated user dict from LoginWindow.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSpacerItem, QSizePolicy, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from ui.dashboard           import DashboardPanel
from ui.ambulance_management import AmbulanceManagementPanel
from ui.emergency_panel      import EmergencyPanel
from ui.reports_window       import ReportsWindow
from ui.styles               import MAIN_STYLE, COLORS


class MainWindow(QMainWindow):
    """
    Main application window.
    Sidebar on the left, content panels on the right.
    Nav buttons switch between panels via QStackedWidget.
    """

    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self._build_ui()
        self.setStyleSheet(MAIN_STYLE)
        self._navigate(0)   # Start on dashboard

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("🚑 Ambulance Dispatch System")
        self.setMinimumSize(1300, 780)
        self.resize(1440, 860)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo
        logo = QLabel("🚑 AmbulanceDS")
        logo.setObjectName("logo_label")
        version = QLabel("v1.0  ·  Control Room")
        version.setObjectName("version_label")
        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(version)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px; margin: 0 12px;")
        sidebar_layout.addWidget(divider)
        sidebar_layout.addSpacing(8)

        # Nav items: (icon+label, requires_admin)
        nav_items = [
            ("🏠   Dashboard",          False),
            ("🚑   Ambulances & Drivers", False),
            ("🚨   Emergency Panel",     False),
            ("📈   Reports & Analytics", False),
        ]

        self.nav_buttons = []
        for label, admin_only in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(False)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # Connect buttons with index
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))

        sidebar_layout.addStretch()

        # User info at bottom
        sidebar_layout.addSpacing(8)
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                margin: 8px;
            }}
        """)
        uf_layout = QVBoxLayout(user_frame)
        uf_layout.setContentsMargins(12, 10, 12, 10)

        uname = QLabel(f"👤  {self.user['username'].title()}")
        uname.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: bold; font-size: 12px;")
        urole = QLabel(self.user.get("role", "").title())
        urole.setStyleSheet(f"color: {COLORS['accent']}; font-size: 11px;")
        uf_layout.addWidget(uname)
        uf_layout.addWidget(urole)
        sidebar_layout.addWidget(user_frame)

        # Logout button
        logout_btn = QPushButton("⏏  Logout")
        logout_btn.setObjectName("btn_secondary")
        logout_btn.setFixedHeight(36)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin: 4px 8px 12px 8px;
            }}
            QPushButton:hover {{
                color: {COLORS['danger']};
                border-color: {COLORS['danger']};
            }}
        """)
        logout_btn.clicked.connect(self._confirm_logout)
        sidebar_layout.addWidget(logout_btn)

        root.addWidget(sidebar)

        # ── Content Area ──────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        # Create all panels
        self.dashboard_panel   = DashboardPanel(self.user)
        self.fleet_panel       = AmbulanceManagementPanel(self.user)
        self.emergency_panel   = EmergencyPanel(self.user)
        self.reports_panel     = ReportsWindow(self.user)

        self.stack.addWidget(self.dashboard_panel)    # index 0
        self.stack.addWidget(self.fleet_panel)         # index 1
        self.stack.addWidget(self.emergency_panel)     # index 2
        self.stack.addWidget(self.reports_panel)       # index 3

        root.addWidget(self.stack, 1)

        # ── Status Bar ────────────────────────────────────────────────────
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(
            f"  Connected  ·  User: {self.user['username']}  ·  Role: {self.user['role']}"
        )

        # Cross-panel refresh connections
        self.fleet_panel.data_changed.connect(self.dashboard_panel.refresh)
        self.emergency_panel.data_changed.connect(self.dashboard_panel.refresh)
        self.emergency_panel.data_changed.connect(self.reports_panel.refresh_all)

    # ─────────────────────────────────────────────
    # NAVIGATION
    # ─────────────────────────────────────────────

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)

        # Update active styling on nav buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", str(i == index).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh panel on navigate
        panel = self.stack.currentWidget()
        if hasattr(panel, "refresh"):
            panel.refresh()
        elif hasattr(panel, "refresh_all"):
            panel.refresh_all()

        panel_names = ["Dashboard", "Fleet Management", "Emergency Panel", "Reports"]
        self.status_bar.showMessage(
            f"  {panel_names[index]}  ·  User: {self.user['username']}  ·  Role: {self.user['role']}"
        )

    # ─────────────────────────────────────────────
    # LOGOUT
    # ─────────────────────────────────────────────

    def _confirm_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Stop all timers before closing
            if hasattr(self.dashboard_panel, "refresh_timer"):
                self.dashboard_panel.refresh_timer.stop()
            if hasattr(self.dashboard_panel, "clock_timer"):
                self.dashboard_panel.clock_timer.stop()
            self.logout_requested.emit()
