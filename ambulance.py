"""
models/ambulance.py
===================
Data model for Ambulance entity.
Provides object-oriented access to ambulance data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Ambulance:
    """Represents a single ambulance unit in the dispatch system."""

    id: int = 0
    vehicle_number: str = ""
    status: str = "Available"        # Available | On Duty | Maintenance
    latitude: float = 0.0
    longitude: float = 0.0
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    created_at: str = ""

    # Status color mapping for UI
    STATUS_COLORS = {
        "Available":   "#2ecc71",   # Green
        "On Duty":     "#e74c3c",   # Red
        "Maintenance": "#f39c12",   # Yellow/Orange
    }

    @classmethod
    def from_dict(cls, data: dict) -> "Ambulance":
        """Construct Ambulance from a database row dictionary."""
        return cls(
            id=data.get("id", 0),
            vehicle_number=data.get("vehicle_number", ""),
            status=data.get("status", "Available"),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            driver_id=data.get("driver_id"),
            driver_name=data.get("driver_name"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict:
        """Serialize ambulance to dictionary."""
        return {
            "id": self.id,
            "vehicle_number": self.vehicle_number,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "driver_id": self.driver_id,
            "driver_name": self.driver_name,
            "created_at": self.created_at,
        }

    @property
    def status_color(self) -> str:
        """Return color hex code for this ambulance's current status."""
        return self.STATUS_COLORS.get(self.status, "#95a5a6")

    @property
    def is_available(self) -> bool:
        return self.status == "Available"

    def __str__(self) -> str:
        return f"Ambulance({self.vehicle_number}, {self.status})"
