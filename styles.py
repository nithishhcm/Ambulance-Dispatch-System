"""
ui/styles.py
============
Centralized stylesheet and color palette for the Ambulance Dispatch System UI.
All PyQt5 windows import from here for visual consistency.
"""

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#1a1a2e",
    "bg_panel":      "#16213e",
    "bg_card":       "#0f3460",
    "accent":        "#e94560",
    "accent_hover":  "#c73652",
    "success":       "#2ecc71",
    "warning":       "#f39c12",
    "danger":        "#e74c3c",
    "info":          "#3498db",
    "text_primary":  "#ecf0f1",
    "text_secondary":"#95a5a6",
    "border":        "#2c3e50",
    "sidebar":       "#0d1b2a",
    "white":         "#ffffff",
}

# ── Main Application Stylesheet ───────────────────────────────────────────────
MAIN_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

QDialog {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_primary']};
}}

/* ── Sidebar ─── */
#sidebar {{
    background-color: {COLORS['sidebar']};
    border-right: 2px solid {COLORS['accent']};
    min-width: 220px;
    max-width: 220px;
}}

#logo_label {{
    color: {COLORS['accent']};
    font-size: 16px;
    font-weight: bold;
    padding: 20px 10px 5px 10px;
}}

#version_label {{
    color: {COLORS['text_secondary']};
    font-size: 10px;
    padding: 0 10px 15px 10px;
}}

/* ── Sidebar Buttons ─── */
QPushButton#nav_btn {{
    background: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
}}
QPushButton#nav_btn:hover {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['white']};
    border-left: 3px solid {COLORS['accent']};
}}
QPushButton#nav_btn[active="true"] {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['white']};
    border-left: 3px solid {COLORS['accent']};
    font-weight: bold;
}}

/* ── General Buttons ─── */
QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{ background-color: {COLORS['accent_hover']}; }}
QPushButton:disabled {{ background-color: {COLORS['text_secondary']}; color: #666; }}

QPushButton#btn_success {{
    background-color: {COLORS['success']};
    color: white;
}}
QPushButton#btn_success:hover {{ background-color: #27ae60; }}

QPushButton#btn_warning {{
    background-color: {COLORS['warning']};
    color: white;
}}
QPushButton#btn_warning:hover {{ background-color: #d68910; }}

QPushButton#btn_danger {{
    background-color: {COLORS['danger']};
    color: white;
}}
QPushButton#btn_danger:hover {{ background-color: #c0392b; }}

QPushButton#btn_info {{
    background-color: {COLORS['info']};
    color: white;
}}
QPushButton#btn_info:hover {{ background-color: #2980b9; }}

QPushButton#btn_secondary {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}
QPushButton#btn_secondary:hover {{ background-color: {COLORS['border']}; }}

/* ── Stat Cards ─── */
QFrame#stat_card {{
    background-color: {COLORS['bg_card']};
    border-radius: 10px;
    padding: 15px;
    border: 1px solid {COLORS['border']};
}}
QLabel#card_value {{
    color: {COLORS['accent']};
    font-size: 32px;
    font-weight: bold;
}}
QLabel#card_title {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}

/* ── Tables ─── */
QTableWidget {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_primary']};
    gridline-color: {COLORS['border']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['bg_card']};
}}
QTableWidget::item {{ padding: 6px 10px; }}
QTableWidget::item:selected {{
    background-color: {COLORS['bg_card']};
    color: white;
}}
QHeaderView::section {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {COLORS['accent']};
    font-weight: bold;
    font-size: 12px;
}}

/* ── Input Fields ─── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {COLORS['accent']};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent']};
}}

/* ── Labels ─── */
QLabel#page_title {{
    color: {COLORS['text_primary']};
    font-size: 22px;
    font-weight: bold;
    padding: 0 0 5px 0;
}}
QLabel#page_subtitle {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    padding-bottom: 10px;
}}
QLabel#section_label {{
    color: {COLORS['text_secondary']};
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 15px 0 5px 0;
    letter-spacing: 1px;
}}

/* ── Scrollbars ─── */
QScrollBar:vertical {{
    background: {COLORS['bg_dark']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Group Box ─── */
QGroupBox {{
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLORS['accent']};
}}

/* ── Status Bar ─── */
QStatusBar {{
    background-color: {COLORS['sidebar']};
    color: {COLORS['text_secondary']};
    font-size: 11px;
    border-top: 1px solid {COLORS['border']};
}}

/* ── TabWidget ─── */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background: {COLORS['bg_panel']};
}}
QTabBar::tab {{
    background: {COLORS['bg_dark']};
    color: {COLORS['text_secondary']};
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: white;
    border-bottom: 2px solid {COLORS['accent']};
    background: {COLORS['bg_panel']};
}}

/* ── Severity badges ─── */
QLabel#badge_critical {{ color: #e74c3c; font-weight: bold; }}
QLabel#badge_high     {{ color: #e67e22; font-weight: bold; }}
QLabel#badge_medium   {{ color: #f39c12; font-weight: bold; }}
QLabel#badge_low      {{ color: #3498db; font-weight: bold; }}
"""

LOGIN_STYLE = f"""
QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}
QFrame#login_card {{
    background-color: {COLORS['bg_panel']};
    border-radius: 16px;
    border: 1px solid {COLORS['border']};
}}
QLineEdit {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
}}
QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
QPushButton#login_btn {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 15px;
    font-weight: bold;
}}
QPushButton#login_btn:hover {{ background-color: {COLORS['accent_hover']}; }}
QLabel#login_title {{
    color: {COLORS['white']};
    font-size: 26px;
    font-weight: bold;
}}
QLabel#login_subtitle {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
}}
QLabel#error_label {{
    color: {COLORS['danger']};
    font-size: 12px;
}}
"""
