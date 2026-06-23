"""
services/dispatch_engine.py
============================
Smart Dispatch Engine for the Ambulance Dispatch System.

Implements:
- Haversine distance calculation
- Nearest available ambulance selection
- Priority-weighted dispatch
- Response time estimation
- Real-time status management
"""

import math
import random
from typing import Optional, Tuple, List, Dict
from database.db_manager import DatabaseManager
from models.ambulance import Ambulance
from models.emergency import Emergency


# ── Constants ────────────────────────────────────────────────────────────────
EARTH_RADIUS_KM = 6371.0
AVG_SPEED_KMH   = 60.0   # Assumed ambulance average speed in urban area

# Severity score multipliers for dispatch priority
SEVERITY_WEIGHT = {
    "Critical": 1.0,
    "High":     1.2,
    "Medium":   1.5,
    "Low":      2.0,
}


class DispatchEngine:
    """
    Core dispatch logic.
    Selects the optimal ambulance for an emergency using geospatial distance
    and severity-weighted scoring.
    """

    def __init__(self):
        self.db = DatabaseManager()

    # ─────────────────────────────────────────────
    # HAVERSINE DISTANCE
    # ─────────────────────────────────────────────

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance in kilometers between two coordinates.
        Uses the Haversine formula.

        Args:
            lat1, lon1: Coordinates of point A (degrees)
            lat2, lon2: Coordinates of point B (degrees)

        Returns:
            Distance in kilometers (float)
        """
        # Convert degrees → radians
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi  = math.radians(lat2 - lat1)
        d_lamb = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(d_phi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(d_lamb / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return EARTH_RADIUS_KM * c

    @staticmethod
    def estimate_eta_minutes(distance_km: float, speed_kmh: float = AVG_SPEED_KMH) -> float:
        """
        Estimate ETA from distance.

        Args:
            distance_km: Distance in kilometers
            speed_kmh: Average speed (default city speed)

        Returns:
            ETA in minutes
        """
        if speed_kmh <= 0:
            return float("inf")
        return (distance_km / speed_kmh) * 60.0

    # ─────────────────────────────────────────────
    # FIND NEAREST AMBULANCE
    # ─────────────────────────────────────────────

    def find_nearest_ambulance(
        self,
        emergency_lat: float,
        emergency_lon: float,
        severity: str = "Medium"
    ) -> Optional[Dict]:
        """
        Find the best available ambulance for an emergency location.

        Uses severity-weighted scoring:
            score = distance * severity_weight
        Lower score = higher priority for dispatch.

        Args:
            emergency_lat: Emergency latitude
            emergency_lon: Emergency longitude
            severity: Emergency severity level

        Returns:
            Dict with keys: ambulance, distance_km, eta_minutes
            Or None if no ambulances are available.
        """
        available_ambulances = self.db.get_available_ambulances()

        if not available_ambulances:
            return None

        weight = SEVERITY_WEIGHT.get(severity, 1.5)
        best = None
        best_score = float("inf")

        for amb_data in available_ambulances:
            amb = Ambulance.from_dict(amb_data)
            dist = self.haversine(
                emergency_lat, emergency_lon,
                amb.latitude, amb.longitude
            )
            # Score: lower is better; critical emergencies penalize distance less
            score = dist * weight

            if score < best_score:
                best_score = score
                best = {
                    "ambulance": amb,
                    "distance_km": round(dist, 3),
                    "eta_minutes": round(self.estimate_eta_minutes(dist), 2),
                    "score": round(score, 3),
                }

        return best

    # ─────────────────────────────────────────────
    # AUTO DISPATCH
    # ─────────────────────────────────────────────

    def auto_dispatch(self, emergency_id: int) -> Dict:
        """
        Automatically find and assign the best ambulance to an emergency.

        Steps:
          1. Load emergency from DB
          2. Run nearest-ambulance search
          3. Assign ambulance, update statuses
          4. Return dispatch result summary

        Returns:
            dict with dispatch outcome details
        """
        # Load emergency
        all_emg = self.db.get_all_emergencies()
        emg_data = next((e for e in all_emg if e["id"] == emergency_id), None)

        if not emg_data:
            return {"success": False, "message": "Emergency not found."}

        emg = Emergency.from_dict(emg_data)

        if emg.status != "Pending":
            return {"success": False, "message": f"Emergency is already '{emg.status}'."}

        # Find nearest
        result = self.find_nearest_ambulance(emg.latitude, emg.longitude, emg.severity)

        if result is None:
            return {
                "success": False,
                "message": "No available ambulances at this time. Please try again later.",
            }

        amb = result["ambulance"]

        # Persist assignment
        self.db.assign_ambulance_to_emergency(
            emergency_id=emergency_id,
            ambulance_id=amb.id,
            response_time_minutes=result["eta_minutes"],
        )

        return {
            "success": True,
            "ambulance_id": amb.id,
            "vehicle_number": amb.vehicle_number,
            "distance_km": result["distance_km"],
            "eta_minutes": result["eta_minutes"],
            "message": (
                f"Dispatched {amb.vehicle_number} → "
                f"{result['distance_km']:.2f} km away, "
                f"ETA ≈ {result['eta_minutes']:.1f} min"
            ),
        }

    # ─────────────────────────────────────────────
    # DISTANCE MATRIX
    # ─────────────────────────────────────────────

    def get_all_distances(
        self, emergency_lat: float, emergency_lon: float
    ) -> List[Dict]:
        """
        Return distance from every ambulance to the emergency location,
        sorted by distance ascending.

        Used to show the operator a ranked list.
        """
        ambulances = self.db.get_all_ambulances()
        distances = []

        for amb_data in ambulances:
            amb = Ambulance.from_dict(amb_data)
            dist = self.haversine(
                emergency_lat, emergency_lon,
                amb.latitude, amb.longitude
            )
            distances.append({
                "ambulance": amb,
                "distance_km": round(dist, 3),
                "eta_minutes": round(self.estimate_eta_minutes(dist), 2),
            })

        distances.sort(key=lambda x: x["distance_km"])
        return distances

    # ─────────────────────────────────────────────
    # SIMULATED REAL-TIME LOCATION UPDATES
    # ─────────────────────────────────────────────

    def simulate_location_update(self):
        """
        Randomly drift ambulance coordinates to simulate GPS movement.
        Called periodically by a QTimer in the UI.
        """
        ambulances = self.db.get_all_ambulances()
        for amb_data in ambulances:
            # Only move ambulances that are on duty
            if amb_data["status"] == "On Duty":
                new_lat = amb_data["latitude"] + random.uniform(-0.002, 0.002)
                new_lon = amb_data["longitude"] + random.uniform(-0.002, 0.002)
                self.db.update_ambulance_location(amb_data["id"], new_lat, new_lon)
