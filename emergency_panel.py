"""
ui/emergency_panel.py
======================
Emergency management panel:
- Log new emergency requests
- Auto-dispatch nearest ambulance
- View active and historical emergencies
- Complete / cancel emergencies
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QDialogButtonBox, QMessageBox, QTextEdit, QTabWidget,
    QFrame, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtGui import QColor, QFont

from database.db_manager import DatabaseManager
from services.dispatch_engine import DispatchEngine
from models.emergency import Emergency


class EmergencyPanel(QWidget):
    """
    Emergency panel with three views:
      - Active Emergencies (real-time queue)
      - All Emergencies (history)
      - New Emergency form
    """

    data_changed = pyqtSignal()

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user   = user
        self.db     = DatabaseManager()
        self.engine = DispatchEngine()
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
        title = QLabel("Emergency Response Panel")
        title.setObjectName("page_title")
        sub   = QLabel("Manage incoming emergencies and dispatch ambulances")
        sub.setObjectName("page_subtitle")
        v = QVBoxLayout()
        v.addWidget(title); v.addWidget(sub)
        hdr.addLayout(v)
        hdr.addStretch()
        btn_new = QPushButton("🚨  New Emergency")
        btn_new.setObjectName("btn_danger")
        btn_new.setFixedHeight(40)
        btn_new.clicked.connect(self._open_new_emergency_dialog)
        hdr.addWidget(btn_new)
        layout.addLayout(hdr)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_active_tab(),  "🔴  Active")
        tabs.addTab(self._build_history_tab(), "📋  All Records")
        layout.addWidget(tabs)

    def _build_active_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 10, 0, 0)

        # Action buttons
        bar = QHBoxLayout()
        self.btn_dispatch = QPushButton("⚡  Auto-Dispatch")
        self.btn_dispatch.setObjectName("btn_danger")
        self.btn_dispatch.clicked.connect(self._auto_dispatch)

        self.btn_complete = QPushButton("✅  Mark Complete")
        self.btn_complete.setObjectName("btn_success")
        self.btn_complete.clicked.connect(self._complete_emergency)

        self.btn_cancel = QPushButton("✗  Cancel")
        self.btn_cancel.setObjectName("btn_secondary")
        self.btn_cancel.clicked.connect(self._cancel_emergency)

        btn_refresh = QPushButton("↻")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.setFixedWidth(40)
        btn_refresh.clicked.connect(self.refresh_active)

        for btn in [self.btn_dispatch, self.btn_complete, self.btn_cancel, btn_refresh]:
            bar.addWidget(btn)
        bar.addStretch()
        layout.addLayout(bar)

        # Active emergencies table
        self.active_table = QTableWidget()
        self.active_table.setColumnCount(9)
        self.active_table.setHorizontalHeaderLabels([
            "ID", "Patient", "Phone", "Severity", "Location",
            "Status", "Ambulance", "ETA (min)", "Time"
        ])
        self._configure_table(self.active_table)
        layout.addWidget(self.active_table)
        return w

    def _build_history_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 10, 0, 0)

        bar = QHBoxLayout()
        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_history)
        btn_del = QPushButton("🗑  Delete Record")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete_emergency)
        for btn in [btn_refresh, btn_del]:
            bar.addWidget(btn)
        bar.addStretch()
        layout.addLayout(bar)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Patient", "Severity", "Ambulance",
            "Response Time", "Status", "Address", "Notes", "Request Time"
        ])
        self._configure_table(self.history_table)
        layout.addWidget(self.history_table)
        return w

    def _configure_table(self, table: QTableWidget):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

    # ─────────────────────────────────────────────
    # DATA REFRESH
    # ─────────────────────────────────────────────

    def refresh_all(self):
        self.refresh_active()
        self.refresh_history()

    def refresh_active(self):
        rows = self.db.get_active_emergencies()
        self.active_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            emg = Emergency.from_dict(r)
            items = [
                str(emg.id),
                emg.patient_name,
                emg.phone,
                emg.severity,
                f"{emg.latitude:.4f}, {emg.longitude:.4f}",
                emg.status,
                emg.vehicle_number or "—",
                emg.response_time_label,
                emg.request_time[:16] if emg.request_time else "",
            ]
            for j, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                # Severity color
                if j == 3:
                    item.setForeground(QColor(emg.severity_color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                # Status color
                if j == 5:
                    item.setForeground(QColor(emg.status_color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.active_table.setItem(i, j, item)

    def refresh_history(self):
        rows = self.db.get_all_emergencies()
        self.history_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            emg = Emergency.from_dict(r)
            items = [
                str(emg.id),
                emg.patient_name,
                emg.severity,
                emg.vehicle_number or "—",
                emg.response_time_label,
                emg.status,
                emg.address or "—",
                emg.notes[:30] + "…" if emg.notes and len(emg.notes) > 30 else emg.notes or "—",
                emg.request_time[:16] if emg.request_time else "",
            ]
            for j, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 2:
                    item.setForeground(QColor(emg.severity_color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                if j == 5:
                    item.setForeground(QColor(emg.status_color))
                self.history_table.setItem(i, j, item)

    # ─────────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────────

    def _get_selected_active_id(self):
        row = self.active_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select an emergency from the list.")
            return None
        return int(self.active_table.item(row, 0).text())

    def _open_new_emergency_dialog(self):
        dlg = NewEmergencyDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            emg_id = self.db.add_emergency(**data)
            self.refresh_active()
            self.data_changed.emit()

            # Offer auto-dispatch immediately
            reply = QMessageBox.question(
                self, "Auto-Dispatch?",
                f"Emergency #{emg_id} logged.\nAuto-dispatch nearest ambulance now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._dispatch_emergency_id(emg_id)

    def _auto_dispatch(self):
        emg_id = self._get_selected_active_id()
        if emg_id:
            self._dispatch_emergency_id(emg_id)

    def _dispatch_emergency_id(self, emg_id: int):
        result = self.engine.auto_dispatch(emg_id)
        if result["success"]:
            QMessageBox.information(
                self, "Dispatched ✓",
                f"✅ {result['message']}"
            )
        else:
            QMessageBox.warning(self, "Dispatch Failed", result["message"])
        self.refresh_active()
        self.data_changed.emit()

    def _complete_emergency(self):
        emg_id = self._get_selected_active_id()
        if not emg_id:
            return
        reply = QMessageBox.question(
            self, "Complete Emergency",
            "Mark this emergency as completed? The ambulance will be set back to Available.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.complete_emergency(emg_id)
            self.refresh_all()
            self.data_changed.emit()

    def _cancel_emergency(self):
        emg_id = self._get_selected_active_id()
        if not emg_id:
            return
        reply = QMessageBox.question(
            self, "Cancel Emergency",
            "Cancel this emergency?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.cancel_emergency(emg_id)
            self.refresh_all()
            self.data_changed.emit()

    def _delete_emergency(self):
        row = self.history_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a record.")
            return
        emg_id = int(self.history_table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Delete Record",
            "Permanently delete this emergency record?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_emergency(emg_id)
            self.refresh_history()


# ─────────────────────────────────────────────────────────────────────────────
# NEW EMERGENCY DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class NewEmergencyDialog(QDialog):
    """Form dialog to log a new emergency request."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Log New Emergency")
        self.setFixedSize(460, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Timestamp badge
        ts_frame = QFrame()
        ts_frame.setStyleSheet("background: #0f3460; border-radius: 6px; padding: 6px;")
        ts_layout = QHBoxLayout(ts_frame)
        ts_lbl = QLabel("🕐  " + QDateTime.currentDateTime().toString("yyyy-MM-dd  hh:mm:ss"))
        ts_lbl.setStyleSheet("color: #f39c12; font-weight: bold;")
        ts_layout.addWidget(ts_lbl)
        layout.addWidget(ts_frame)
        layout.addSpacing(10)

        form = QFormLayout()
        form.setSpacing(12)

        self.patient_input   = QLineEdit()
        self.patient_input.setPlaceholderText("Patient full name")

        self.phone_input     = QLineEdit()
        self.phone_input.setPlaceholderText("Contact number")

        self.severity_combo  = QComboBox()
        self.severity_combo.addItems(["Critical", "High", "Medium", "Low"])
        # Color the severity combo
        self.severity_combo.currentTextChanged.connect(self._update_severity_color)

        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90, 90)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(31.5204)

        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180, 180)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(74.3587)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Street address / landmark")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes (optional)")
        self.notes_input.setFixedHeight(70)

        form.addRow("Patient Name *:", self.patient_input)
        form.addRow("Phone *:",        self.phone_input)
        form.addRow("Severity:",       self.severity_combo)
        form.addRow("Latitude:",       self.lat_input)
        form.addRow("Longitude:",      self.lon_input)
        form.addRow("Address:",        self.address_input)
        form.addRow("Notes:",          self.notes_input)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Log Emergency")
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._update_severity_color("Critical")

    def _update_severity_color(self, severity):
        colors = {
            "Critical": "#e74c3c",
            "High":     "#e67e22",
            "Medium":   "#f39c12",
            "Low":      "#3498db",
        }
        color = colors.get(severity, "#aaa")
        self.severity_combo.setStyleSheet(
            f"QComboBox {{ color: {color}; font-weight: bold; border: 1px solid {color}; }}"
        )

    def _validate(self):
        if not self.patient_input.text().strip():
            QMessageBox.warning(self, "Validation", "Patient name is required.")
            return
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validation", "Phone number is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "patient_name": self.patient_input.text().strip(),
            "phone":        self.phone_input.text().strip(),
            "severity":     self.severity_combo.currentText(),
            "latitude":     self.lat_input.value(),
            "longitude":    self.lon_input.value(),
            "address":      self.address_input.text().strip(),
            "notes":        self.notes_input.toPlainText().strip(),
        }
