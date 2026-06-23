"""
models/emergency.py
===================
Data model for Emergency entity.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Emergency:
    """Represents an emergency request."""

    id: int = 0
    patient_name: str = ""
    phone: str = ""
    severity: str = "Medium"         # Low | Medium | High | Critical
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""
    request_time: str = ""
    assigned_ambulance_id: Optional[int] = None
    vehicle_number: Optional[str] = None
    response_time: Optional[float] = None    # minutes
    status: str = "Pending"          # Pending | Assigned | Completed | Cancelled
    notes: str = ""

    # Severity color mapping
    SEVERITY_COLORS = {
        "Low":      "#3498db",   # Blue
        "Medium":   "#f39c12",   # Orange
        "High":     "#e67e22",   # Dark Orange
        "Critical": "#e74c3c",   # Red
    }

    # Severity priority (lower = higher priority)
    SEVERITY_PRIORITY = {
        "Critical": 1,
        "High":     2,
        "Medium":   3,
        "Low":      4,
    }

    STATUS_COLORS = {
        "Pending":   "#f39c12",
        "Assigned":  "#3498db",
        "Completed": "#2ecc71",
        "Cancelled": "#95a5a6",
    }

    @classmethod
    def from_dict(cls, data: dict) -> "Emergency":
        return cls(
            id=data.get("id", 0),
            patient_name=data.get("patient_name", ""),
            phone=data.get("phone", ""),
            severity=data.get("severity", "Medium"),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            address=data.get("address", ""),
            request_time=data.get("request_time", ""),
            assigned_ambulance_id=data.get("assigned_ambulance_id"),
            vehicle_number=data.get("vehicle_number"),
            response_time=data.get("response_time"),
            status=data.get("status", "Pending"),
            notes=data.get("notes", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "patient_name": self.patient_name,
            "phone": self.phone,
            "severity": self.severity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "status": self.status,
        }

    @property
    def severity_color(self) -> str:
        return self.SEVERITY_COLORS.get(self.severity, "#95a5a6")

    @property
    def status_color(self) -> str:
        return self.STATUS_COLORS.get(self.status, "#95a5a6")

    @property
    def priority(self) -> int:
        return self.SEVERITY_PRIORITY.get(self.severity, 99)

    @property
    def response_time_label(self) -> str:
        if self.response_time is None:
            return "N/A"
        return f"{self.response_time:.1f} min"

    def __str__(self) -> str:
        return f"Emergency({self.patient_name}, {self.severity}, {self.status})"
