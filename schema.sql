-- ============================================================
-- Ambulance Dispatch System - Database Schema
-- ============================================================

-- Users table for authentication and role-based access
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,          -- SHA-256 hashed
    role TEXT NOT NULL DEFAULT 'dispatcher',  -- admin | dispatcher | viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    license_number TEXT NOT NULL UNIQUE,
    experience_years INTEGER DEFAULT 0,
    availability_status TEXT NOT NULL DEFAULT 'Available',  -- Available | On Duty | Off Duty
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ambulances table
CREATE TABLE IF NOT EXISTS ambulances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'Available',  -- Available | On Duty | Maintenance
    latitude REAL NOT NULL DEFAULT 0.0,
    longitude REAL NOT NULL DEFAULT 0.0,
    driver_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);

-- Emergencies table
CREATE TABLE IF NOT EXISTS emergencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'Medium',  -- Low | Medium | High | Critical
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_ambulance_id INTEGER,
    response_time REAL,              -- in minutes
    status TEXT NOT NULL DEFAULT 'Pending',  -- Pending | Assigned | Completed | Cancelled
    notes TEXT,
    FOREIGN KEY (assigned_ambulance_id) REFERENCES ambulances(id) ON DELETE SET NULL
);

-- Activity log for audit trail
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ambulances_status ON ambulances(status);
CREATE INDEX IF NOT EXISTS idx_emergencies_status ON emergencies(status);
CREATE INDEX IF NOT EXISTS idx_emergencies_request_time ON emergencies(request_time);
CREATE INDEX IF NOT EXISTS idx_drivers_availability ON drivers(availability_status);
