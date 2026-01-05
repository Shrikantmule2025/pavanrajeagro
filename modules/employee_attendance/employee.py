import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "pavanraje.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date TEXT,
    start_time TEXT,
    end_time TEXT,
    start_photo TEXT,
    end_photo TEXT,
    latitude TEXT,
    longitude TEXT,
    work_desc TEXT
)
""")


    # Default employee
    c.execute("SELECT * FROM employees WHERE username='employee1'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO employees (username, password) VALUES (?,?)",
            ("employee1", "1234")
        )

    conn.commit()
    conn.close()


def check_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id FROM employees WHERE username=? AND password=?",
        (username, password)
    )
    row = c.fetchone()
    conn.close()
    return row


def mark_attendance(employee_id):
    now = datetime.now()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO attendance (employee_id, date, time) VALUES (?,?,?)",
        (employee_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
    )
    conn.commit()
    conn.close()
