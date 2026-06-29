![Python](https://img.shields.io/badge/Python-3.x-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Analytics-purple)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
# 🚑 AI-Enabled Ambulance Dispatch & Emergency Response Management System

An enterprise-grade, mission-critical desktop control room simulator built using **Python 3**, **PyQt5**, **SQLite**, and **Matplotlib**. This project models a real-world emergency management ecosystem, showcasing structured object-oriented programming (OOP), asynchronous interface tracking, and automated algorithmic unit routing.

---

## 📌 Core Features

### 🔐 Operational Security & Access Control
* **Role-Based UI Customization:** The system adapts features depending on the logged-in profile role (`Admin` vs. `Dispatcher`).
* **Cryptographic Data Protection:** Passwords are fully secured via standard SHA-256 cryptographic hashing to mimic enterprise access standards.

### 🧠 Algorithmic Dispatch Engine
* **The Haversine Metric:** Calculates real-time, great-circle spatial distances across geographical coordinates ($km$) between active incidents and unit terminals.
* **Dynamic Severity Weighting:** Implements priority penalty rules to clear high-stress bottlenecks. Critical incidents penalize distance less, forcing the allocation logic to favor them first:
  * **Critical:** 1.0x baseline priority allocation (highest speed profile)
  * **High:** 1.2x baseline buffer allocation
  * **Medium:** 1.5x baseline buffer allocation
  * **Low:** 2.0x baseline buffer allocation
* **ETA Projections:** Generates precise operational arrival projections based on a calibrated 60 km/h average urban response speed.

### 📊 Tactical Data Visualization & UI
* **Embedded Analytics Panels:** Features a full dashboard suite parsing metrics directly onto low-overhead matplotlib canvases embedded natively within PyQt layouts.
* **Asynchronous Telemetry Updates:** Drives interactive KPI metrics, live ticking control room clocks, and multi-threaded tracking modules that simulate active unit GPS progression every 10 seconds.

---

## 🏗️ Architectural Topology (MVC Model)

The repository follows a clean, highly decoupled **Model-View-Controller (MVC)** software architectural pattern to isolate core telemetry algorithms from UI components:
ambulance_dispatch_system/
│
├── main.py                     # System runtime bootstrap hook
├── requirements.txt            # System dependencies manifest
├── README.md                   # System documentation homepage
│
├── database/
│   ├── schema.sql              # Relational SQLite database layout (DDL)
│   └── db_manager.py           # Thread-safe Singleton Database controller
│
├── models/
│   ├── ambulance.py            # Fleet state dataclass definitions
│   ├── driver.py               # Personnel registries and metadata
│   └── emergency.py            # Incident classification & triage rules
│
├── services/
│   ├── dispatch_engine.py      # Haversine distance computations & telemetry logic
│   └── analytics_service.py    # Multi-dimensional KPI processing layers
│
└── ui/
├── styles.py               # Centralized dark-theme design system tokens
├── login_window.py         # Frameless secure authentication portal
├── main_window.py          # Application shell layout container
├── dashboard.py            # Live operational monitoring desk
├── ambulance_management.py # Full CRUD lifecycle interfaces for fleet & personnel
├── emergency_panel.py      # Incident dispatcher logger
└── reports_window.py       # Embedded analytical charting suite

## 🗄️ Database Schema & Security Blueprint

The backend database layer (`database/dispatch.db`) leverages a relational SQLite design patterns structure built for high-throughput consistency:
* **Parameterized Query Pipeline:** All operations use strictly parameterized statements to thoroughly eliminate SQL injection vulnerabilities.
* **Relational Schema Design:** Distributed systematically across **5 system tables**:
  * `users` — Cryptographically secure credentials, profile metadata, and system access scopes.
  * `ambulances` — Active tracking matrices including status flags and dynamic live GPS coordinates.
  * `drivers` — Operational profiles detailing certifications and service history.
  * `emergencies` — Transaction logs documenting assigned units and severity indices.
  * `activity_log` — System-wide immutable audit trail mapping control actions to terminal IDs.

---

## 🛠️ Local Deploy & Installation Guide

### Prerequisites
* **Python 3.8** or higher installed on your local development terminal.

### Step-by-Step Setup

1. **Clone the Repository Environment:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
   cd YOUR_REPOSITORY

| System User ID | System Passphrase | Accessible Control Scope |
| :--- | :--- | :--- |
| `admin` | `admin123` | Complete control access scope / Personnel CRUD management modules |

| `dispatcher` | `dispatch123` | Control room access / Incident logging & active routing interfaces |

<img width="1432" height="880" alt="image" src="https://github.com/user-attachments/assets/acc3bcf8-273d-420b-a9f9-9d2e9b874d01" />
<img width="1440" height="872" alt="image" src="https://github.com/user-attachments/assets/f30ebac7-ea2e-4d17-9140-8ab1f078cd80" />
<img width="1433" height="870" alt="image" src="https://github.com/user-attachments/assets/b99e95c0-f9e7-4d5c-b0b7-e1ad96af8929" />


