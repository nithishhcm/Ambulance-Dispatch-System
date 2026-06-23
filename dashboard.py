"""
ui/dashboard.py
================
Main dashboard — the first screen after login.
Shows key metrics summary cards and a live ambulance status donut chart.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QGridLayout,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database.db_manager import DatabaseManager
from services.analytics_service import AnalyticsService
from services.dispatch_engine import DispatchEngine
from models.emergency import Emergency
from ui.styles import COLORS

# ── Chart dark theme ─────────────────────────────────────────────────────────
CHART_BG   = "#1a1a2e"
CHART_TEXT = "#ecf0f1"

plt.rcParams.update({
    "figure.facecolor": CHART_BG,
    "axes.facecolor":   CHART_BG,
    "axes.edgecolor":   "#2c3e50",
    "text.color":       CHART_TEXT,
    "xtick.color":      CHART_TEXT,
    "ytick.color":      CHART_TEXT,
})


class DashboardPanel(QWidget):
    """
    Main dashboard panel:
      - Real-time KPI stat cards
      - Ambulance fleet status donut chart
      - Recent active emergencies table
      - Auto-refresh every 10 seconds
    """

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user      = user
        self.db        = DatabaseManager()
        self.analytics = AnalyticsService()
        self.engine    = DispatchEngine()
        self._build_ui()
        self._start_auto_refresh()
        self.refresh()

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 16)
        outer.setSpacing(16)

        # ── Welcome header ────────────────────────────────────────────────
        hdr = QHBoxLayout()
        role = self.user.get("role", "").title()
        greeting = QLabel(f"Welcome, {self.user['username'].title()} 👋")
        greeting.setObjectName("page_title")
        role_lbl = QLabel(f"Role: {role}")
        role_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        v = QVBoxLayout()
        v.addWidget(greeting); v.addWidget(role_lbl)
        hdr.addLayout(v)
        hdr.addStretch()
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        hdr.addWidget(self.clock_lbl)
        outer.addLayout(hdr)

        # ── Stat Cards Row ────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self.card_total_amb   = self._stat_card("🚑", "Total Ambulances",   "—", COLORS["info"])
        self.card_avail       = self._stat_card("🟢", "Available",          "—", COLORS["success"])
        self.card_on_duty     = self._stat_card("🔴", "On Duty",            "—", COLORS["danger"])
        self.card_maintenance = self._stat_card("🟡", "Maintenance",        "—", COLORS["warning"])
        self.card_active_emg  = self._stat_card("🚨", "Active Emergencies", "—", COLORS["accent"])
        self.card_avg_rt      = self._stat_card("⏱", "Avg Response (min)", "—", "#9b59b6")
        self.card_drivers     = self._stat_card("👤", "Total Drivers",      "—", COLORS["info"])

        for card in [self.card_total_amb, self.card_avail, self.card_on_duty,
                     self.card_maintenance, self.card_active_emg,
                     self.card_avg_rt, self.card_drivers]:
            cards_row.addWidget(card)

        outer.addLayout(cards_row)

        # ── Bottom Row: Chart + Recent Emergencies ─────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        # Fleet status chart (left)
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"background: {COLORS['bg_card']}; border-radius: 10px;")
        chart_frame.setFixedWidth(320)
        cf_layout = QVBoxLayout(chart_frame)
        cf_layout.setContentsMargins(12, 12, 12, 12)

        chart_title = QLabel("Fleet Status")
        chart_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: bold; text-transform: uppercase;")
        cf_layout.addWidget(chart_title)

        self.fleet_fig    = Figure(figsize=(3.2, 3.2), tight_layout=True)
        self.fleet_canvas = FigureCanvas(self.fleet_fig)
        self.fleet_canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fleet_canvas.setFixedSize(296, 260)
        cf_layout.addWidget(self.fleet_canvas)
        bottom.addWidget(chart_frame)

        # Recent emergencies (right)
        emg_frame = QFrame()
        emg_frame.setStyleSheet(f"background: {COLORS['bg_card']}; border-radius: 10px;")
        ef_layout = QVBoxLayout(emg_frame)
        ef_layout.setContentsMargins(12, 12, 12, 12)
        ef_layout.setSpacing(8)

        ef_hdr = QHBoxLayout()
        emg_title = QLabel("Active Emergencies")
        emg_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: bold; text-transform: uppercase;")
        ef_hdr.addWidget(emg_title)
        ef_hdr.addStretch()
        ef_layout.addLayout(ef_hdr)

        self.emg_table = QTableWidget()
        self.emg_table.setColumnCount(5)
        self.emg_table.setHorizontalHeaderLabels(["Patient", "Severity", "Status", "Ambulance", "Time"])
        self.emg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.emg_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.emg_table.setAlternatingRowColors(True)
        self.emg_table.verticalHeader().setVisible(False)
        self.emg_table.setStyleSheet("QTableWidget { border: none; border-radius: 6px; }")
        ef_layout.addWidget(self.emg_table)

        bottom.addWidget(emg_frame)
        outer.addLayout(bottom)

    # ─────────────────────────────────────────────
    # STAT CARD FACTORY
    # ─────────────────────────────────────────────

    def _stat_card(self, icon: str, title: str, value: str, accent: str) -> QFrame:
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(100)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: {COLORS['bg_card']};
                border-radius: 10px;
                border-left: 4px solid {accent};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        icon_title = QLabel(f"{icon}  {title}")
        icon_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {accent}; font-size: 26px; font-weight: bold;")
        val_lbl.setObjectName("cv")

        layout.addWidget(icon_title)
        layout.addWidget(val_lbl)

        # Store reference to the value label
        card._val_lbl = val_lbl
        return card

    # ─────────────────────────────────────────────
    # REFRESH
    # ─────────────────────────────────────────────

    def refresh(self):
        """Pull latest data from DB and update all UI elements."""
        stats = self.analytics.get_kpi_summary()

        self.card_total_amb._val_lbl.setText(str(stats["total_ambulances"]))
        self.card_avail._val_lbl.setText(str(stats["available_ambulances"]))
        self.card_on_duty._val_lbl.setText(str(stats["on_duty_ambulances"]))
        self.card_maintenance._val_lbl.setText(str(stats["maintenance_ambulances"]))
        self.card_active_emg._val_lbl.setText(str(stats["active_emergencies"]))
        self.card_avg_rt._val_lbl.setText(f"{stats['avg_response_time']:.1f}")
        self.card_drivers._val_lbl.setText(str(stats["total_drivers"]))

        self._update_fleet_chart(stats)
        self._update_emergencies_table()
        self._simulate_gps()

    def _update_fleet_chart(self, stats: dict):
        """Redraw the fleet status donut chart."""
        self.fleet_fig.clear()
        ax = self.fleet_fig.add_subplot(111)

        labels, counts, colors = self.analytics.ambulance_status_chart_data()
        total = sum(counts)

        if total == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    fontsize=12, color=CHART_TEXT)
        else:
            wedges, texts, auto_texts = ax.pie(
                counts, labels=labels, colors=colors,
                autopct="%1.0f%%", startangle=90,
                wedgeprops={"edgecolor": CHART_BG, "linewidth": 3, "width": 0.65},
                textprops={"color": CHART_TEXT, "fontsize": 9},
            )
            # Center text
            ax.text(0, 0, f"{total}\nTotal", ha="center", va="center",
                    fontsize=12, color=CHART_TEXT, fontweight="bold")
            for at in auto_texts:
                at.set_fontsize(8)

        self.fleet_canvas.draw()

    def _update_emergencies_table(self):
        """Fill the active emergencies mini-table."""
        rows = self.db.get_active_emergencies()
        self.emg_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            emg = Emergency.from_dict(r)
            items = [
                emg.patient_name,
                emg.severity,
                emg.status,
                emg.vehicle_number or "—",
                emg.request_time[11:16] if emg.request_time else "",
            ]
            for j, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 1:
                    item.setForeground(QColor(emg.severity_color))
                    item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                if j == 2:
                    item.setForeground(QColor(emg.status_color))
                self.emg_table.setItem(i, j, item)

    def _simulate_gps(self):
        """Trigger one round of simulated GPS location drift."""
        try:
            self.engine.simulate_location_update()
        except Exception:
            pass

    # ─────────────────────────────────────────────
    # AUTO REFRESH TIMER
    # ─────────────────────────────────────────────

    def _start_auto_refresh(self):
        # Refresh dashboard data every 10 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(10_000)

        # Update clock every second
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1_000)

    def _update_clock(self):
        from PyQt5.QtCore import QDateTime
        self.clock_lbl.setText(QDateTime.currentDateTime().toString("ddd, MMM d  hh:mm:ss"))
