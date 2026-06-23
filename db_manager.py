"""
db_manager.py
=============
Central database manager for the Ambulance Dispatch System.
Handles all SQLite operations using parameterized queries to prevent SQL injection.
Implements connection pooling pattern and singleton access.
"""

import sqlite3
import os
import hashlib
from datetime import datetime

# Resolve paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "dispatch.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


class DatabaseManager:
    """
    Singleton database manager.
    Provides all CRUD operations for every entity in the system.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db_path = DB_PATH
        self._ensure_db_directory()
        self.initialize_database()
        self._seed_default_data()

    # ─────────────────────────────────────────────
    # INITIALIZATION
    # ─────────────────────────────────────────────

    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        """Return a new SQLite connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize_database(self):
        """Read and execute the SQL schema file."""
        try:
            with open(SCHEMA_PATH, "r") as f:
                schema_sql = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
        except Exception as e:
            print(f"[DB] Schema initialization error: {e}")
            raise

    def _seed_default_data(self):
        """Insert default admin user and sample data if tables are empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Default admin user
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
                disp_pw = hashlib.sha256("dispatch123".encode()).hexdigest()
                cursor.executemany(
                    "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                    [
                        ("admin", admin_pw, "admin"),
                        ("dispatcher", disp_pw, "dispatcher"),
                    ],
                )

            # Sample drivers
            cursor.execute("SELECT COUNT(*) FROM drivers")
            if cursor.fetchone()[0] == 0:
                drivers = [
                    ("Ali Hassan",     "0300-1234567", "LIC-001", 8,  "Available"),
                    ("Sara Malik",     "0301-2345678", "LIC-002", 5,  "Available"),
                    ("Usman Ahmed",    "0302-3456789", "LIC-003", 12, "Available"),
                    ("Fatima Khan",    "0303-4567890", "LIC-004", 3,  "Available"),
                    ("Bilal Raza",     "0304-5678901", "LIC-005", 7,  "Available"),
                    ("Nadia Qureshi",  "0305-6789012", "LIC-006", 10, "Off Duty"),
                    ("Tariq Mehmood",  "0306-7890123", "LIC-007", 4,  "Available"),
                    ("Zara Siddiqui",  "0307-8901234", "LIC-008", 6,  "Available"),
                ]
                cursor.executemany(
                    "INSERT INTO drivers (name,phone,license_number,experience_years,availability_status) VALUES (?,?,?,?,?)",
                    drivers,
                )

            # Sample ambulances (Lahore area coordinates)
            cursor.execute("SELECT COUNT(*) FROM ambulances")
            if cursor.fetchone()[0] == 0:
                ambulances = [
                    ("AMB-001", "Available",   31.5204, 74.3587, 1),
                    ("AMB-002", "Available",   31.5497, 74.3436, 2),
                    ("AMB-003", "On Duty",     31.5100, 74.3400, 3),
                    ("AMB-004", "Available",   31.5600, 74.3700, 4),
                    ("AMB-005", "Maintenance", 31.5300, 74.3200, 5),
                    ("AMB-006", "Available",   31.5800, 74.3900, 6),
                    ("AMB-007", "Available",   31.4900, 74.3100, 7),
                    ("AMB-008", "On Duty",     31.5150, 74.3650, 8),
                ]
                cursor.executemany(
                    "INSERT INTO ambulances (vehicle_number,status,latitude,longitude,driver_id) VALUES (?,?,?,?,?)",
                    ambulances,
                )

            # Sample past emergencies for analytics
            cursor.execute("SELECT COUNT(*) FROM emergencies")
            if cursor.fetchone()[0] == 0:
                import random
                severities = ["Low", "Medium", "High", "Critical"]
                statuses   = ["Completed", "Completed", "Completed", "Assigned"]
                sample_emergencies = []
                for i in range(30):
                    sev    = random.choice(severities)
                    status = random.choice(statuses)
                    lat    = 31.50 + random.uniform(-0.05, 0.10)
                    lon    = 74.33 + random.uniform(-0.05, 0.10)
                    rt     = round(random.uniform(4.0, 25.0), 2) if status == "Completed" else None
                    amb_id = random.randint(1, 8) if status != "Pending" else None
                    sample_emergencies.append((
                        f"Patient-{i+1}", f"030{i}-0000000",
                        sev, lat, lon, f"Location-{i+1}",
                        amb_id, rt, status
                    ))
                cursor.executemany(
                    """INSERT INTO emergencies
                       (patient_name,phone,severity,latitude,longitude,address,
                        assigned_ambulance_id,response_time,status)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    sample_emergencies,
                )
            conn.commit()

    # ─────────────────────────────────────────────
    # USER OPERATIONS
    # ─────────────────────────────────────────────

    def authenticate_user(self, username: str, password: str):
        """Return user row if credentials match, else None."""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hashed)
            ).fetchone()
        return dict(row) if row else None

    def get_all_users(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id,username,role,created_at FROM users").fetchall()
        return [dict(r) for r in rows]

    def add_user(self, username, password, role):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        with self._get_connection() as conn:
            conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                         (username, hashed, role))
            conn.commit()

    # ─────────────────────────────────────────────
    # DRIVER OPERATIONS
    # ─────────────────────────────────────────────

    def get_all_drivers(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def get_available_drivers(self):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM drivers WHERE availability_status='Available'").fetchall()
        return [dict(r) for r in rows]

    def add_driver(self, name, phone, license_number, experience_years, availability_status):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO drivers (name,phone,license_number,experience_years,availability_status) VALUES (?,?,?,?,?)",
                (name, phone, license_number, experience_years, availability_status)
            )
            conn.commit()

    def update_driver(self, driver_id, name, phone, license_number, experience_years, availability_status):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE drivers SET name=?,phone=?,license_number=?,experience_years=?,availability_status=? WHERE id=?",
                (name, phone, license_number, experience_years, availability_status, driver_id)
            )
            conn.commit()

    def delete_driver(self, driver_id):
        with self._get_connection() as conn:
            conn.execute("UPDATE ambulances SET driver_id=NULL WHERE driver_id=?", (driver_id,))
            conn.execute("DELETE FROM drivers WHERE id=?", (driver_id,))
            conn.commit()

    # ─────────────────────────────────────────────
    # AMBULANCE OPERATIONS
    # ─────────────────────────────────────────────

    def get_all_ambulances(self):
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT a.*, d.name as driver_name
                FROM ambulances a
                LEFT JOIN drivers d ON a.driver_id = d.id
                ORDER BY a.vehicle_number
            """).fetchall()
        return [dict(r) for r in rows]

    def get_available_ambulances(self):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM ambulances WHERE status='Available'").fetchall()
        return [dict(r) for r in rows]

    def add_ambulance(self, vehicle_number, status, latitude, longitude, driver_id=None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO ambulances (vehicle_number,status,latitude,longitude,driver_id) VALUES (?,?,?,?,?)",
                (vehicle_number, status, latitude, longitude, driver_id)
            )
            conn.commit()

    def update_ambulance(self, amb_id, vehicle_number, status, latitude, longitude, driver_id=None):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE ambulances SET vehicle_number=?,status=?,latitude=?,longitude=?,driver_id=? WHERE id=?",
                (vehicle_number, status, latitude, longitude, driver_id, amb_id)
            )
            conn.commit()

    def update_ambulance_status(self, amb_id, status):
        with self._get_connection() as conn:
            conn.execute("UPDATE ambulances SET status=? WHERE id=?", (status, amb_id))
            conn.commit()

    def update_ambulance_location(self, amb_id, latitude, longitude):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE ambulances SET latitude=?,longitude=? WHERE id=?",
                (latitude, longitude, amb_id)
            )
            conn.commit()

    def delete_ambulance(self, amb_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM ambulances WHERE id=?", (amb_id,))
            conn.commit()

    # ─────────────────────────────────────────────
    # EMERGENCY OPERATIONS
    # ─────────────────────────────────────────────

    def get_all_emergencies(self):
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, a.vehicle_number
                FROM emergencies e
                LEFT JOIN ambulances a ON e.assigned_ambulance_id = a.id
                ORDER BY e.request_time DESC
            """).fetchall()
        return [dict(r) for r in rows]

    def get_active_emergencies(self):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM emergencies WHERE status IN ('Pending','Assigned') ORDER BY request_time DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def add_emergency(self, patient_name, phone, severity, latitude, longitude, address="", notes=""):
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO emergencies
                   (patient_name,phone,severity,latitude,longitude,address,notes,status)
                   VALUES (?,?,?,?,?,?,?,'Pending')""",
                (patient_name, phone, severity, latitude, longitude, address, notes)
            )
            conn.commit()
            return cursor.lastrowid

    def assign_ambulance_to_emergency(self, emergency_id, ambulance_id, response_time_minutes):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE emergencies SET assigned_ambulance_id=?,response_time=?,status='Assigned' WHERE id=?",
                (ambulance_id, response_time_minutes, emergency_id)
            )
            conn.execute("UPDATE ambulances SET status='On Duty' WHERE id=?", (ambulance_id,))
            conn.commit()

    def complete_emergency(self, emergency_id):
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT assigned_ambulance_id FROM emergencies WHERE id=?", (emergency_id,)
            ).fetchone()
            if row and row["assigned_ambulance_id"]:
                conn.execute(
                    "UPDATE ambulances SET status='Available' WHERE id=?",
                    (row["assigned_ambulance_id"],)
                )
            conn.execute("UPDATE emergencies SET status='Completed' WHERE id=?", (emergency_id,))
            conn.commit()

    def cancel_emergency(self, emergency_id):
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT assigned_ambulance_id FROM emergencies WHERE id=?", (emergency_id,)
            ).fetchone()
            if row and row["assigned_ambulance_id"]:
                conn.execute(
                    "UPDATE ambulances SET status='Available' WHERE id=?",
                    (row["assigned_ambulance_id"],)
                )
            conn.execute("UPDATE emergencies SET status='Cancelled' WHERE id=?", (emergency_id,))
            conn.commit()

    def delete_emergency(self, emergency_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM emergencies WHERE id=?", (emergency_id,))
            conn.commit()

    # ─────────────────────────────────────────────
    # ANALYTICS QUERIES
    # ─────────────────────────────────────────────

    def get_dashboard_stats(self):
        """Return key metrics for the dashboard."""
        with self._get_connection() as conn:
            c = conn.cursor()
            total_amb   = c.execute("SELECT COUNT(*) FROM ambulances").fetchone()[0]
            avail_amb   = c.execute("SELECT COUNT(*) FROM ambulances WHERE status='Available'").fetchone()[0]
            on_duty_amb = c.execute("SELECT COUNT(*) FROM ambulances WHERE status='On Duty'").fetchone()[0]
            maint_amb   = c.execute("SELECT COUNT(*) FROM ambulances WHERE status='Maintenance'").fetchone()[0]
            total_drv   = c.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
            active_emg  = c.execute("SELECT COUNT(*) FROM emergencies WHERE status IN ('Pending','Assigned')").fetchone()[0]
            total_emg   = c.execute("SELECT COUNT(*) FROM emergencies").fetchone()[0]
            avg_rt      = c.execute("SELECT AVG(response_time) FROM emergencies WHERE response_time IS NOT NULL").fetchone()[0]
        return {
            "total_ambulances":     total_amb,
            "available_ambulances": avail_amb,
            "on_duty_ambulances":   on_duty_amb,
            "maintenance_ambulances": maint_amb,
            "total_drivers":        total_drv,
            "active_emergencies":   active_emg,
            "total_emergencies":    total_emg,
            "avg_response_time":    round(avg_rt, 2) if avg_rt else 0.0,
        }

    def get_severity_distribution(self):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT severity, COUNT(*) as count FROM emergencies GROUP BY severity"
            ).fetchall()
        return {r["severity"]: r["count"] for r in rows}

    def get_monthly_trend(self):
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT strftime('%Y-%m', request_time) as month, COUNT(*) as count
                FROM emergencies
                GROUP BY month ORDER BY month DESC LIMIT 12
            """).fetchall()
        return [(r["month"], r["count"]) for r in rows]

    def get_ambulance_utilization(self):
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT a.vehicle_number,
                       COUNT(e.id) as total_dispatches
                FROM ambulances a
                LEFT JOIN emergencies e ON a.id = e.assigned_ambulance_id
                GROUP BY a.id ORDER BY total_dispatches DESC
            """).fetchall()
        return [(r["vehicle_number"], r["total_dispatches"]) for r in rows]

    def get_response_time_by_severity(self):
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT severity, AVG(response_time) as avg_rt
                FROM emergencies
                WHERE response_time IS NOT NULL
                GROUP BY severity
            """).fetchall()
        return {r["severity"]: round(r["avg_rt"], 2) for r in rows}

    def log_activity(self, user_id, action, details=""):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO activity_log (user_id,action,details) VALUES (?,?,?)",
                (user_id, action, details)
            )
            conn.commit()
