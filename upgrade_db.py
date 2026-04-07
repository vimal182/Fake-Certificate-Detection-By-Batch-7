import sqlite3

conn = sqlite3.connect("database/main.db")
cursor = conn.cursor()

# Add qr_path
try:
    cursor.execute("ALTER TABLE institution_certificates ADD COLUMN qr_path TEXT")
    print("qr_path added")
except:
    print("qr_path already exists")

# Add status
try:
    cursor.execute("ALTER TABLE institution_certificates ADD COLUMN status TEXT DEFAULT 'ACTIVE'")
    print("status column added")
except:
    print("status already exists")

# Add revoked_at
try:
    cursor.execute("ALTER TABLE institution_certificates ADD COLUMN revoked_at TEXT")
    print("revoked_at added")
except:
    print("revoked_at already exists")

# Add revocation_reason
try:
    cursor.execute("ALTER TABLE institution_certificates ADD COLUMN revocation_reason TEXT")
    print("revocation_reason added")
except:
    print("revocation_reason already exists")

conn.commit()
conn.close()

print("Database upgraded successfully.")