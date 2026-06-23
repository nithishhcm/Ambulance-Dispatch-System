"""
models/driver.py
================
Data model for Driver entity.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Driver:
    """Represents a driver in the dispatch system."""

    id: int = 0
    name: str = ""
    phone: str = ""
    license_number: str = ""
    experience_years: int = 0
    availability_status: str = "Available"   # Available | On Duty | Off Duty
    created_at: str = ""

    STATUS_COLORS = {
        "Available": "#2ecc71",
        "On Duty":   "#e74c3c",
        "Off Duty":  "#95a5a6",
    }

    @classmethod
    def from_dict(cls, data: dict) -> "Driver":
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            license_number=data.get("license_number", ""),
            experience_years=data.get("experience_years", 0),
            availability_status=data.get("availability_status", "Available"),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "license_number": self.license_number,
            "experience_years": self.experience_years,
            "availability_status": self.availability_status,
        }

    @property
    def is_available(self) -> bool:
        return self.availability_status == "Available"

    @property
    def experience_label(self) -> str:
        y = self.experience_years
        return f"{y} yr{'s' if y != 1 else ''}"

    def __str__(self) -> str:
        return f"Driver({self.name}, {self.availability_status})"
