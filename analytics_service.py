"""
services/analytics_service.py
==============================
Analytics and reporting service.
Processes raw DB data into chart-ready structures for Matplotlib.
"""

from database.db_manager import DatabaseManager
from typing import Dict, List, Tuple


class AnalyticsService:
    """
    Encapsulates all analytics computations.
    Returns data structures ready for Matplotlib rendering.
    """

    def __init__(self):
        self.db = DatabaseManager()

    # ─────────────────────────────────────────────
    # SUMMARY METRICS
    # ─────────────────────────────────────────────

    def get_kpi_summary(self) -> Dict:
        """Return key performance indicators for the dashboard."""
        stats = self.db.get_dashboard_stats()
        rt_by_severity = self.db.get_response_time_by_severity()

        return {
            **stats,
            "response_time_by_severity": rt_by_severity,
        }

    def get_avg_response_time(self) -> float:
        stats = self.db.get_dashboard_stats()
        return stats.get("avg_response_time", 0.0)

    def get_ambulance_utilization_rate(self) -> Dict[str, float]:
        """
        Calculate utilization percentage per ambulance.
        Utilization = dispatches / total emergencies * 100
        """
        utilization = self.db.get_ambulance_utilization()
        total = sum(v for _, v in utilization)

        if total == 0:
            return {vn: 0.0 for vn, _ in utilization}

        return {vn: round((count / total) * 100, 1) for vn, count in utilization}

    # ─────────────────────────────────────────────
    # CHART DATA BUILDERS
    # ─────────────────────────────────────────────

    def severity_distribution_chart_data(self) -> Tuple[List[str], List[int], List[str]]:
        """
        Returns (labels, counts, colors) for a severity distribution pie/bar chart.
        """
        dist = self.db.get_severity_distribution()

        order  = ["Critical", "High", "Medium", "Low"]
        colors = ["#e74c3c",  "#e67e22", "#f39c12", "#3498db"]

        labels = []
        counts = []
        used_colors = []

        for sev, color in zip(order, colors):
            if sev in dist:
                labels.append(sev)
                counts.append(dist[sev])
                used_colors.append(color)

        return labels, counts, used_colors

    def monthly_trend_chart_data(self) -> Tuple[List[str], List[int]]:
        """
        Returns (months, counts) for a trend line chart.
        Months are reversed to show oldest → newest.
        """
        trend = self.db.get_monthly_trend()
        if not trend:
            return [], []

        # Reverse to get chronological order
        trend = list(reversed(trend))
        months = [t[0] for t in trend]
        counts = [t[1] for t in trend]
        return months, counts

    def ambulance_utilization_chart_data(self) -> Tuple[List[str], List[int]]:
        """
        Returns (vehicle_numbers, dispatch_counts) for a bar chart.
        """
        utilization = self.db.get_ambulance_utilization()
        vehicles = [v for v, _ in utilization]
        counts   = [c for _, c in utilization]
        return vehicles, counts

    def response_time_by_severity_chart_data(self) -> Tuple[List[str], List[float]]:
        """
        Returns (severity_labels, avg_response_times) for a grouped bar chart.
        """
        rt = self.db.get_response_time_by_severity()
        order = ["Critical", "High", "Medium", "Low"]
        labels = []
        values = []
        for sev in order:
            if sev in rt:
                labels.append(sev)
                values.append(rt[sev])
        return labels, values

    def ambulance_status_chart_data(self) -> Tuple[List[str], List[int], List[str]]:
        """
        Returns (statuses, counts, colors) for a donut chart on the dashboard.
        """
        stats = self.db.get_dashboard_stats()
        labels = ["Available", "On Duty", "Maintenance"]
        counts = [
            stats["available_ambulances"],
            stats["on_duty_ambulances"],
            stats["maintenance_ambulances"],
        ]
        colors = ["#2ecc71", "#e74c3c", "#f39c12"]
        return labels, counts, colors
