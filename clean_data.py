import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print(f"\n{'='*70}")
print("DATA CLEANING SCRIPT")
print(f"{'='*70}\n")

# Fix 1: Convert invalid categories "Work/Study" to "Study"
print("1️⃣  FIXING INVALID CATEGORIES (Work/Study → Study)")
cursor.execute("UPDATE analytics_screentimelog SET category='Study' WHERE category='Work/Study'")
fixed_categories = cursor.rowcount
print(f"✅ Fixed {fixed_categories} records\n")

# Fix 2: Convert future dates to realistic dates
# Strategy: Move September 2026 dates back to recent past (last 90 days from today)
# Today = May 12, 2026
# Sept 15 2026 → May 12 2026 (today)
# Sept 14 2026 → May 11 2026
# Sept 13 2026 → May 10 2026, etc.

print("2️⃣  FIXING FUTURE DATES (Moving September → May)")

# Get all records with future dates
cursor.execute("SELECT id, date FROM analytics_screentimelog WHERE date > date('now') ORDER BY date ASC")
future_records = cursor.fetchall()

today = date.fromisoformat('2026-05-12')
corrections = []

for record_id, future_date_str in future_records:
    future_date = date.fromisoformat(future_date_str)
    
    # Calculate days offset from some reference point
    # We'll map Sept 2026 dates to recent past (last 90 days)
    days_from_sept_1 = (future_date - date.fromisoformat('2026-09-01')).days
    new_date = today - timedelta(days=90) + timedelta(days=days_from_sept_1)
    
    # Make sure new_date is not in future
    if new_date > today:
        new_date = today
    
    corrections.append((new_date.isoformat(), record_id))
    cursor.execute("UPDATE analytics_screentimelog SET date=? WHERE id=?", (new_date.isoformat(), record_id))

print(f"✅ Fixed {len(corrections)} records")
if corrections[:5]:
    print("   Sample corrections:")
    for new_date, rec_id in corrections[:5]:
        print(f"   - ID {rec_id}: → {new_date}")

# Commit changes
conn.commit()

print(f"\n{'='*70}")
print("VERIFICATION")
print(f"{'='*70}\n")

# Verify fixes
cursor.execute("SELECT COUNT(*) FROM analytics_screentimelog WHERE category='Work/Study'")
remaining_invalid_cat = cursor.fetchone()[0]
print(f"Invalid categories remaining: {remaining_invalid_cat} (should be 0)")

cursor.execute("SELECT COUNT(*) FROM analytics_screentimelog WHERE date > date('now')")
remaining_future = cursor.fetchone()[0]
print(f"Future dates remaining: {remaining_future} (should be 0)")

print(f"\n{'='*70}\n")

# Show sample of fixed data
print("SAMPLE OF CLEANED DATA:")
cursor.execute("SELECT id, app_name, category, duration_minutes, date FROM analytics_screentimelog ORDER BY date DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"ID {row[0]}: {row[1]:<20} | {row[2]:<15} | {row[3]:>4} min | {row[4]}")

conn.close()
print("\n✅ Data cleaning complete!\n")
