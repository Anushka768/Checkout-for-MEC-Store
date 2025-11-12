import sqlite3
import glob

# Create or connect to the final master database
master_conn = sqlite3.connect("master_store.db")
master_cur = master_conn.cursor()

# Create the same table structure if not already there
master_cur.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    visit_number INTEGER,
    items TEXT,
    total REAL
)
""")

# Loop through all .db files in a folder
for db_file in glob.glob("all_databases/*.db"):
    print(f"Processing {db_file}...")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Copy all rows from the current file into master_store.db
    for row in cur.execute("SELECT team_name, visit_number, items, total FROM purchases"):
        master_cur.execute(
            "INSERT INTO purchases (team_name, visit_number, items, total) VALUES (?, ?, ?, ?)",
            row
        )

    conn.close()

# Save all combined data
master_conn.commit()
master_conn.close()

print("✅ All data merged into 'master_store.db'")

