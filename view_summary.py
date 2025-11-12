import sqlite3

conn = sqlite3.connect("master_store.db")
cursor = conn.cursor()

cursor.execute("""
SELECT team_name, COUNT(*) AS visits, SUM(total) AS total_spent
FROM purchases
GROUP BY team_name
ORDER BY total_spent DESC
""")

results = cursor.fetchall()

print("\n=== TEAM SUMMARY (ALL DATABASES) ===")
print("{:<20} {:<10} {:<10}".format("Team Name", "Visits", "Total ($)"))
print("-" * 40)

for team, visits, total in results:
    print("{:<20} {:<10} {:<10.2f}".format(team, visits, total))

conn.close()
