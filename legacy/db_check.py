import sqlite3

conn = sqlite3.connect('precision_vrt.db')
cursor = conn.cursor()

# Check integrity
cursor.execute('PRAGMA integrity_check')
print('Integrity check:', cursor.fetchone())

# Check foreign keys
cursor.execute('PRAGMA foreign_key_check')
fk = cursor.fetchall()
print('Foreign key check:', fk if fk else 'OK - No violations')

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

conn.close()
