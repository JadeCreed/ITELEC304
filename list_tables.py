import sqlite3
c = sqlite3.connect('db.sqlite3')
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("Tables found:", tables)
c.close()
