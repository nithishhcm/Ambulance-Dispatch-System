"""
ui/ambulance_management.py
===========================
Panel to view, add, edit, and delete ambulances and drivers.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox, QTabWidget,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from database.db_manager import DatabaseManager
from models.ambulance import Ambulance
from models.driver import Driver


class AmbulanceManagementPanel(QWidget):
    """
    Two-tab panel:
      Tab 1 — Ambulances (CRUD + status management)
      Tab 2 — Drivers   (CRUD)
    """

    data_changed = pyqtSignal()   # emitted whenever DB is modified

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.db   = DatabaseManager()
        self._build_ui()
        self.refresh_all()

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        # Page header
        hdr = QHBoxLayout()
        title = QLabel("Fleet & Driver Management")
        title.setObjectName("page_title")
        sub   = QLabel("Manage ambulances, assign drivers, update status")
        sub.setObjectName("page_subtitle")
        v = QVBoxLayout()
        v.addWidget(title); v.addWidget(sub)
        hdr.addLayout(v)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_ambulance_tab(), "🚑  Ambulances")
        self.tabs.addTab(self._build_driver_tab(),    "👤  Drivers")
        layout.addWidget(self.tabs)

    # ── Ambulance Tab ─────────────────────────────────────────────────────

    def _build_ambulance_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 10, 0, 0)

        # Toolbar
        bar = QHBoxLayout()
        btn_add = QPushButton("➕  Add Ambulance")
        btn_add.setObjectName("btn_success")
        btn_add.clicked.connect(self._add_ambulance)
        btn_edit = QPushButton("✏  Edit")
        btn_edit.setObjectName("btn_info")
        btn_edit.clicked.connect(self._edit_ambulance)
        btn_del = QPushButton("🗑  Delete")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete_ambulance)
        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_ambulances)

        for btn in [btn_add, btn_edit, btn_del, btn_refresh]:
            bar.addWidget(btn)
        bar.addStretch()
        layout.addLayout(bar)

        # Table
        self.amb_table = QTableWidget()
        self.amb_table.setColumnCount(7)
        self.amb_table.setHorizontalHeaderLabels([
            "ID", "Vehicle No.", "Status", "Driver", "Latitude", "Longitude", "Added"
        ])
        self.amb_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.amb_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.amb_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.amb_table.setAlternatingRowColors(True)
        self.amb_table.verticalHeader().setVisible(False)
        self.amb_table.doubleClicked.connect(self._edit_ambulance)
        layout.addWidget(self.amb_table)
        return w

    # ── Driver Tab ────────────────────────────────────────────────────────

    def _build_driver_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 10, 0, 0)

        bar = QHBoxLayout()
        btn_add = QPushButton("➕  Add Driver")
        btn_add.setObjectName("btn_success")
        btn_add.clicked.connect(self._add_driver)
        btn_edit = QPushButton("✏  Edit")
        btn_edit.setObjectName("btn_info")
        btn_edit.clicked.connect(self._edit_driver)
        btn_del = QPushButton("🗑  Delete")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete_driver)
        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_drivers)
        for btn in [btn_add, btn_edit, btn_del, btn_refresh]:
            bar.addWidget(btn)
        bar.addStretch()
        layout.addLayout(bar)

        self.drv_table = QTableWidget()
        self.drv_table.setColumnCount(6)
        self.drv_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "License No.", "Experience", "Status"
        ])
        self.drv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.drv_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.drv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.drv_table.setAlternatingRowColors(True)
        self.drv_table.verticalHeader().setVisible(False)
        self.drv_table.doubleClicked.connect(self._edit_driver)
        layout.addWidget(self.drv_table)
        return w

    # ─────────────────────────────────────────────
    # DATA REFRESH
    # ─────────────────────────────────────────────

    def refresh_all(self):
        self.refresh_ambulances()
        self.refresh_drivers()

    def refresh_ambulances(self):
        rows = self.db.get_all_ambulances()
        self.amb_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            amb = Ambulance.from_dict(r)
            items = [
                str(amb.id),
                amb.vehicle_number,
                amb.status,
                amb.driver_name or "—",
                f"{amb.latitude:.4f}",
                f"{amb.longitude:.4f}",
                amb.created_at[:10] if amb.created_at else "",
            ]
            for j, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                # Color-code status
                if j == 2:
                    item.setForeground(QColor(amb.status_color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.amb_table.setItem(i, j, item)

    def refresh_drivers(self):
        rows = self.db.get_all_drivers()
        self.drv_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            drv = Driver.from_dict(r)
            items = [
                str(drv.id),
                drv.name,
                drv.phone,
                drv.license_number,
                drv.experience_label,
                drv.availability_status,
            ]
            for j, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 5:
                    item.setForeground(QColor(drv.STATUS_COLORS.get(drv.availability_status, "#aaa")))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.drv_table.setItem(i, j, item)

    # ─────────────────────────────────────────────
    # AMBULANCE CRUD
    # ─────────────────────────────────────────────

    def _get_selected_amb_id(self):
        row = self.amb_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select an ambulance first.")
            return None
        return int(self.amb_table.item(row, 0).text())

    def _add_ambulance(self):
        dlg = AmbulanceDialog(self.db, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.db.add_ambulance(**data)
            self.refresh_ambulances()
            self.data_changed.emit()

    def _edit_ambulance(self):
        amb_id = self._get_selected_amb_id()
        if not amb_id:
            return
        all_amb = self.db.get_all_ambulances()
        data = next((a for a in all_amb if a["id"] == amb_id), None)
        if not data:
            return
        dlg = AmbulanceDialog(self.db, ambulance_data=data, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_data = dlg.get_data()
            self.db.update_ambulance(amb_id, **new_data)
            self.refresh_ambulances()
            self.data_changed.emit()

    def _delete_ambulance(self):
        amb_id = self._get_selected_amb_id()
        if not amb_id:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this ambulance? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_ambulance(amb_id)
            self.refresh_ambulances()
            self.data_changed.emit()

    # ─────────────────────────────────────────────
    # DRIVER CRUD
    # ─────────────────────────────────────────────

    def _get_selected_drv_id(self):
        row = self.drv_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a driver first.")
            return None
        return int(self.drv_table.item(row, 0).text())

    def _add_driver(self):
        dlg = DriverDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.db.add_driver(**data)
            self.refresh_drivers()
            self.data_changed.emit()

    def _edit_driver(self):
        drv_id = self._get_selected_drv_id()
        if not drv_id:
            return
        all_drivers = self.db.get_all_drivers()
        data = next((d for d in all_drivers if d["id"] == drv_id), None)
        if not data:
            return
        dlg = DriverDialog(driver_data=data, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_data = dlg.get_data()
            self.db.update_driver(drv_id, **new_data)
            self.refresh_drivers()
            self.data_changed.emit()

    def _delete_driver(self):
        drv_id = self._get_selected_drv_id()
        if not drv_id:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this driver?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_driver(drv_id)
            self.refresh_drivers()
            self.data_changed.emit()


# ─────────────────────────────────────────────────────────────────────────────
# DIALOGS
# ─────────────────────────────────────────────────────────────────────────────

class AmbulanceDialog(QDialog):
    """Modal form to add or edit an ambulance."""

    def __init__(self, db: DatabaseManager, ambulance_data: dict = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.ambulance_data = ambulance_data
        self._build_ui()
        if ambulance_data:
            self._populate(ambulance_data)

    def _build_ui(self):
        is_edit = self.ambulance_data is not None
        self.setWindowTitle("Edit Ambulance" if is_edit else "Add New Ambulance")
        self.setFixedSize(420, 380)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.vehicle_input = QLineEdit()
        self.vehicle_input.setPlaceholderText("e.g. AMB-009")

        self.status_input = QComboBox()
        self.status_input.addItems(["Available", "On Duty", "Maintenance"])

        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90, 90)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(31.5204)

        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180, 180)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(74.3587)

        self.driver_combo = QComboBox()
        self.driver_combo.addItem("— Unassigned —", None)
        for drv in self.db.get_all_drivers():
            self.driver_combo.addItem(f"{drv['name']} ({drv['license_number']})", drv["id"])

        form.addRow("Vehicle Number:", self.vehicle_input)
        form.addRow("Status:", self.status_input)
        form.addRow("Latitude:", self.lat_input)
        form.addRow("Longitude:", self.lon_input)
        form.addRow("Assigned Driver:", self.driver_combo)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, data):
        self.vehicle_input.setText(data.get("vehicle_number", ""))
        idx = self.status_input.findText(data.get("status", "Available"))
        if idx >= 0:
            self.status_input.setCurrentIndex(idx)
        self.lat_input.setValue(data.get("latitude", 31.5204))
        self.lon_input.setValue(data.get("longitude", 74.3587))
        driver_id = data.get("driver_id")
        for i in range(self.driver_combo.count()):
            if self.driver_combo.itemData(i) == driver_id:
                self.driver_combo.setCurrentIndex(i)
                break

    def _validate_and_accept(self):
        if not self.vehicle_input.text().strip():
            QMessageBox.warning(self, "Validation", "Vehicle number is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "vehicle_number": self.vehicle_input.text().strip(),
            "status":         self.status_input.currentText(),
            "latitude":       self.lat_input.value(),
            "longitude":      self.lon_input.value(),
            "driver_id":      self.driver_combo.currentData(),
        }


class DriverDialog(QDialog):
    """Modal form to add or edit a driver."""

    def __init__(self, driver_data: dict = None, parent=None):
        super().__init__(parent)
        self.driver_data = driver_data
        self._build_ui()
        if driver_data:
            self._populate(driver_data)

    def _build_ui(self):
        is_edit = self.driver_data is not None
        self.setWindowTitle("Edit Driver" if is_edit else "Add New Driver")
        self.setFixedSize(400, 360)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.name_input     = QLineEdit()
        self.phone_input    = QLineEdit()
        self.license_input  = QLineEdit()
        self.exp_input      = QSpinBox()
        self.exp_input.setRange(0, 50)

        self.status_combo   = QComboBox()
        self.status_combo.addItems(["Available", "On Duty", "Off Duty"])

        form.addRow("Full Name:",       self.name_input)
        form.addRow("Phone:",           self.phone_input)
        form.addRow("License Number:",  self.license_input)
        form.addRow("Experience (yrs):", self.exp_input)
        form.addRow("Availability:",    self.status_combo)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, data):
        self.name_input.setText(data.get("name", ""))
        self.phone_input.setText(data.get("phone", ""))
        self.license_input.setText(data.get("license_number", ""))
        self.exp_input.setValue(data.get("experience_years", 0))
        idx = self.status_combo.findText(data.get("availability_status", "Available"))
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        if not self.license_input.text().strip():
            QMessageBox.warning(self, "Validation", "License number is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name":                self.name_input.text().strip(),
            "phone":               self.phone_input.text().strip(),
            "license_number":      self.license_input.text().strip(),
            "experience_years":    self.exp_input.value(),
            "availability_status": self.status_combo.currentText(),
        }
