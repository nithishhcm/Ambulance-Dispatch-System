"""
ui/reports_window.py
=====================
Reports and Analytics panel.
Embeds Matplotlib charts inside PyQt5 using FigureCanvasQTAgg.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QFrame, QSizePolicy,
    QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use("Agg")   # non-interactive backend; Qt canvas does the display
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from services.analytics_service import AnalyticsService
from ui.styles import COLORS


# ── Dark theme for all charts ─────────────────────────────────────────────────
CHART_BG   = "#1a1a2e"
CHART_TEXT = "#ecf0f1"
CHART_GRID = "#2c3e50"
ACCENT_RED = "#e94560"

plt.rcParams.update({
    "figure.facecolor": CHART_BG,
    "axes.facecolor":   CHART_BG,
    "axes.edgecolor":   CHART_GRID,
    "axes.labelcolor":  CHART_TEXT,
    "xtick.color":      CHART_TEXT,
    "ytick.color":      CHART_TEXT,
    "text.color":       CHART_TEXT,
    "grid.color":       CHART_GRID,
    "legend.facecolor": "#16213e",
    "legend.edgecolor": CHART_GRID,
})


class ReportsWindow(QWidget):
    """
    Reports & Analytics panel with four embedded chart tabs:
      1. Emergency Overview      — Severity distribution pie chart
      2. Monthly Trend           — Line chart over time
      3. Ambulance Utilization   — Horizontal bar chart
      4. Response Time Analysis  — Bar chart by severity
    Plus a KPI summary strip at the top.
    """

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user      = user
        self.analytics = AnalyticsService()
        self._build_ui()
        self.refresh_all()

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Reports & Analytics")
        title.setObjectName("page_title")
        sub   = QLabel("Data-driven insights into emergency response performance")
        sub.setObjectName("page_subtitle")
        v = QVBoxLayout()
        v.addWidget(title); v.addWidget(sub)
        hdr.addLayout(v)
        hdr.addStretch()
        btn_refresh = QPushButton("↻  Refresh Data")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_all)
        hdr.addWidget(btn_refresh)
        layout.addLayout(hdr)

        # KPI Strip
        self.kpi_strip = self._build_kpi_strip()
        layout.addWidget(self.kpi_strip)

        # Chart tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_chart_tab("severity"),    "🥧  Severity")
        self.tabs.addTab(self._make_chart_tab("trend"),       "📈  Monthly Trend")
        self.tabs.addTab(self._make_chart_tab("utilization"), "🚑  Utilization")
        self.tabs.addTab(self._make_chart_tab("response"),    "⏱  Response Times")
        layout.addWidget(self.tabs)

    def _build_kpi_strip(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        row = QHBoxLayout(frame)
        row.setSpacing(12)
        row.setContentsMargins(0, 0, 0, 0)

        self.kpi_labels = {}
        kpis = [
            ("total_emergencies",   "Total Emergencies", "📋"),
            ("active_emergencies",  "Active Now",        "🔴"),
            ("avg_response_time",   "Avg Response (min)","⏱"),
            ("available_ambulances","Available Units",   "🚑"),
        ]
        for key, label, icon in kpis:
            card = self._kpi_card(icon, label, "—")
            row.addWidget(card)
            self.kpi_labels[key] = card.findChild(QLabel, "kv")
        row.addStretch()
        return frame

    def _kpi_card(self, icon: str, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vb = QVBoxLayout(card)
        vb.setContentsMargins(16, 10, 16, 10)

        icon_lbl = QLabel(icon + "  " + title)
        icon_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: bold;")

        val_lbl = QLabel(value)
        val_lbl.setObjectName("kv")
        val_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 28px; font-weight: bold;")
        val_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))

        vb.addWidget(icon_lbl)
        vb.addWidget(val_lbl)
        return card

    def _make_chart_tab(self, chart_type: str) -> QWidget:
        """Create a tab widget containing a Matplotlib canvas."""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 0)

        fig = Figure(figsize=(10, 5), tight_layout=True)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(canvas)

        # Store references for refresh
        setattr(self, f"_fig_{chart_type}", fig)
        setattr(self, f"_canvas_{chart_type}", canvas)
        return w

    # ─────────────────────────────────────────────
    # REFRESH
    # ─────────────────────────────────────────────

    def refresh_all(self):
        self._update_kpis()
        self._draw_severity_chart()
        self._draw_trend_chart()
        self._draw_utilization_chart()
        self._draw_response_chart()

    def _update_kpis(self):
        stats = self.analytics.get_kpi_summary()
        mapping = {
            "total_emergencies":   str(stats.get("total_emergencies", 0)),
            "active_emergencies":  str(stats.get("active_emergencies", 0)),
            "avg_response_time":   f"{stats.get('avg_response_time', 0):.1f}",
            "available_ambulances": str(stats.get("available_ambulances", 0)),
        }
        for key, value in mapping.items():
            lbl = self.kpi_labels.get(key)
            if lbl:
                lbl.setText(value)

    # ─────────────────────────────────────────────
    # CHART RENDERERS
    # ─────────────────────────────────────────────

    def _draw_severity_chart(self):
        fig: Figure = self._fig_severity
        fig.clear()

        labels, counts, colors = self.analytics.severity_distribution_chart_data()
        if not counts or sum(counts) == 0:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                    fontsize=14, color=CHART_TEXT)
            self._canvas_severity.draw()
            return

        ax1 = fig.add_subplot(121)   # Pie chart
        ax2 = fig.add_subplot(122)   # Bar chart

        # Pie
        wedges, texts, auto_texts = ax1.pie(
            counts, labels=labels, colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": CHART_BG, "linewidth": 2},
            textprops={"color": CHART_TEXT},
        )
        for at in auto_texts:
            at.set_fontsize(9)
        ax1.set_title("Severity Distribution", color=CHART_TEXT, fontsize=13, pad=15)

        # Bar
        bars = ax2.bar(labels, counts, color=colors, edgecolor=CHART_BG, linewidth=1.5)
        ax2.set_title("Emergency Count by Severity", color=CHART_TEXT, fontsize=13)
        ax2.set_ylabel("Count", color=CHART_TEXT)
        ax2.grid(axis="y", alpha=0.3)
        for bar, count in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     str(count), ha="center", va="bottom", color=CHART_TEXT, fontsize=11)

        self._canvas_severity.draw()

    def _draw_trend_chart(self):
        fig: Figure = self._fig_trend
        fig.clear()
        ax = fig.add_subplot(111)

        months, counts = self.analytics.monthly_trend_chart_data()
        if not months:
            ax.text(0.5, 0.5, "No trend data available", ha="center", va="center",
                    fontsize=14, color=CHART_TEXT)
            self._canvas_trend.draw()
            return

        ax.plot(months, counts, color=ACCENT_RED, linewidth=2.5, marker="o",
                markersize=7, markerfacecolor=CHART_TEXT)
        ax.fill_between(months, counts, alpha=0.15, color=ACCENT_RED)
        ax.set_title("Monthly Emergency Trend", color=CHART_TEXT, fontsize=14)
        ax.set_xlabel("Month", color=CHART_TEXT)
        ax.set_ylabel("Emergencies", color=CHART_TEXT)
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        for x, y in zip(months, counts):
            ax.annotate(str(y), (x, y), textcoords="offset points",
                        xytext=(0, 8), ha="center", color=CHART_TEXT, fontsize=9)

        self._canvas_trend.draw()

    def _draw_utilization_chart(self):
        fig: Figure = self._fig_utilization
        fig.clear()
        ax = fig.add_subplot(111)

        vehicles, counts = self.analytics.ambulance_utilization_chart_data()
        if not vehicles:
            ax.text(0.5, 0.5, "No utilization data", ha="center", va="center",
                    fontsize=14, color=CHART_TEXT)
            self._canvas_utilization.draw()
            return

        gradient_colors = plt.cm.RdYlGn_r(
            [i / max(len(vehicles) - 1, 1) for i in range(len(vehicles))]
        )
        bars = ax.barh(vehicles, counts, color=gradient_colors, edgecolor=CHART_BG, height=0.6)
        ax.set_title("Ambulance Utilization (Dispatch Count)", color=CHART_TEXT, fontsize=14)
        ax.set_xlabel("Total Dispatches", color=CHART_TEXT)
        ax.grid(axis="x", alpha=0.3)
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                    str(count), va="center", color=CHART_TEXT, fontsize=10)

        self._canvas_utilization.draw()

    def _draw_response_chart(self):
        fig: Figure = self._fig_response
        fig.clear()
        ax = fig.add_subplot(111)

        labels, values = self.analytics.response_time_by_severity_chart_data()
        if not labels:
            ax.text(0.5, 0.5, "No response time data", ha="center", va="center",
                    fontsize=14, color=CHART_TEXT)
            self._canvas_response.draw()
            return

        colors = ["#e74c3c", "#e67e22", "#f39c12", "#3498db"][:len(labels)]
        bars = ax.bar(labels, values, color=colors, edgecolor=CHART_BG, linewidth=1.5, width=0.5)
        ax.set_title("Average Response Time by Severity (minutes)", color=CHART_TEXT, fontsize=14)
        ax.set_ylabel("Avg Response Time (min)", color=CHART_TEXT)
        ax.grid(axis="y", alpha=0.3)

        # Threshold line at 10 min
        ax.axhline(10, color="#f39c12", linestyle="--", linewidth=1.2, alpha=0.7)
        ax.text(len(labels) - 0.5, 10.3, "10 min target", color="#f39c12", fontsize=9)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{val:.1f}", ha="center", va="bottom", color=CHART_TEXT, fontsize=11)

        self._canvas_response.draw()
