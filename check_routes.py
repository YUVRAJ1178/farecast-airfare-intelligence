import sqlite3

con = sqlite3.connect('airfare.db')
cur = con.cursor()

# What routes are in the DB?
cur.execute("""
SELECT origin, destination, COUNT(*) as cnt 
FROM airfare_observations 
GROUP BY origin, destination 
ORDER BY cnt DESC
""")
print("All DB routes:")
for row in cur.fetchall():
    print(f"  {row[0]}->{row[1]}: {row[2]}")

# What does the fares/routes endpoint show vs what's in the DB for GOI, JAI, AMD?
# Check source data 
cur.execute("""
SELECT origin, destination, source, COUNT(*) as cnt
FROM airfare_observations
WHERE origin IN ('GOI','JAI','AMD','BOM') OR destination IN ('GOI','JAI','AMD')
GROUP BY origin, destination, source
ORDER BY origin, destination
""")
print("\nGOI/JAI/AMD-related routes by source:")
for row in cur.fetchall():
    print(f"  {row[0]}->{row[1]} ({row[2]}): {row[3]}")

con.close()
