import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "main.db")

os.makedirs(DB_DIR, exist_ok=True)


if os.path.exists(DB_PATH):
    try:
        sqlite3.connect(DB_PATH).close()
    except:
        print("Existing DB is invalid. Delete it manually.")
        exit()


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

#  INSTITUTIONS 
cursor.execute("""
CREATE TABLE IF NOT EXISTS institutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    college_id TEXT
)
""")

#  INSTITUTION BLOCKCHAIN 
cursor.execute("""
CREATE TABLE IF NOT EXISTS institution_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution_id INTEGER,
    student_name TEXT,
    student_id TEXT,
    college_name TEXT,
    college_id TEXT,
    year TEXT,
    course TEXT,
    department TEXT,
    cert_path TEXT,
    cert_hash TEXT,
    prev_hash TEXT,
    block_hash TEXT,
    timestamp TEXT
)
""")

#  STUDENT CERTIFICATES
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    student_id TEXT,
    college_name TEXT,
    year TEXT,
    course TEXT,
    department TEXT,
    cert_path TEXT,
    uploaded_at TEXT
)
""")

#  STUDENT HASH LEDGER 
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_cert_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_cert_path TEXT,
    student_cert_hash TEXT,
    created_at TEXT
)
""")


conn.commit()
conn.close()

print("✅ Database initialized successfully")
print("📁 Database path:", DB_PATH)
