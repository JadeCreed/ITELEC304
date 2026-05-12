import sqlite3
from datetime import date

# Connect to database
conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_screentimelog'")
if not cursor.fetchone():
    print("❌ Table 'analytics_screentimelog' not found")
    conn.close()
    exit(1)

# Count records
cursor.execute('SELECT COUNT(*) as cnt FROM analytics_screentimelog')
total = cursor.fetchone()[0]
print(f"\n{'='*70}")
print(f"TOTAL RECORDS: {total}")
print(f"{'='*70}\n")

if total == 0:
    print("✅ Database is empty - no data quality issues")
    conn.close()
    exit(0)

# Get all records
cursor.execute('SELECT id, app_name, category, duration_minutes, date FROM analytics_screentimelog ORDER BY date DESC')
records = cursor.fetchall()

# Check for issues
issues = {
    'invalid_category': [],
    'negative_duration': [],
    'future_date': [],
    'empty_app_name': [],
    'whitespace_app_name': [],
    'unrealistic_duration': [],
    'duplicates': [],
}

valid_categories = ['Study', 'Social', 'Gaming', 'Work', 'Entertainment']
seen = {}
today = date.today()

for record in records:
    log_id, app_name, category, duration, date_str = record
    
    # Invalid category
    if category not in valid_categories:
        issues['invalid_category'].append((log_id, app_name, category))
    
    # Negative/zero duration
    if duration <= 0:
        issues['negative_duration'].append((log_id, app_name, duration))
    
    # Future date
    try:
        log_date = date.fromisoformat(date_str)
        if log_date > today:
            issues['future_date'].append((log_id, app_name, date_str))
    except:
        pass
    
    # Empty app name
    if not app_name or app_name.strip() == '':
        issues['empty_app_name'].append((log_id, app_name))
    
    # Whitespace in app name
    if app_name != app_name.strip():
        issues['whitespace_app_name'].append((log_id, app_name))
    
    # Unrealistic duration
    if duration > 1440:
        issues['unrealistic_duration'].append((log_id, app_name, duration))
    
    # Check duplicates
    key = (app_name, category, date_str, duration)
    if key in seen:
        issues['duplicates'].append((log_id, seen[key], app_name, category, date_str))
    else:
        seen[key] = log_id

# Print issues
print("1️⃣  INVALID CATEGORIES")
if issues['invalid_category']:
    print(f"❌ Found {len(issues['invalid_category'])} records:")
    for log_id, app_name, category in issues['invalid_category'][:10]:
        print(f"   ID {log_id}: '{category}' (should be: {', '.join(valid_categories)})")
else:
    print("✅ All categories valid\n")

print("\n2️⃣  NEGATIVE/ZERO DURATIONS")
if issues['negative_duration']:
    print(f"❌ Found {len(issues['negative_duration'])} records:")
    for log_id, app_name, duration in issues['negative_duration'][:10]:
        print(f"   ID {log_id}: {app_name} = {duration} min")
else:
    print("✅ All durations positive\n")

print("\n3️⃣  FUTURE DATES")
if issues['future_date']:
    print(f"❌ Found {len(issues['future_date'])} records:")
    for log_id, app_name, date_str in issues['future_date'][:10]:
        print(f"   ID {log_id}: {date_str}")
else:
    print("✅ No future dates\n")

print("\n4️⃣  EMPTY APP NAMES")
if issues['empty_app_name']:
    print(f"❌ Found {len(issues['empty_app_name'])} records")
else:
    print("✅ All app names populated\n")

print("\n5️⃣  WHITESPACE IN APP NAMES")
if issues['whitespace_app_name']:
    print(f"❌ Found {len(issues['whitespace_app_name'])} records:")
    for log_id, app_name in issues['whitespace_app_name'][:10]:
        print(f"   ID {log_id}: '{app_name}'")
else:
    print("✅ No whitespace issues\n")

print("\n6️⃣  UNREALISTIC DURATIONS (> 1440 min)")
if issues['unrealistic_duration']:
    print(f"❌ Found {len(issues['unrealistic_duration'])} records:")
    for log_id, app_name, duration in issues['unrealistic_duration'][:10]:
        print(f"   ID {log_id}: {app_name} = {duration} min")
else:
    print("✅ All durations realistic\n")

print("\n7️⃣  DUPLICATE RECORDS")
if issues['duplicates']:
    print(f"❌ Found {len(issues['duplicates'])} duplicate(s):")
    for log_id, orig_id, app_name, category, date_str in issues['duplicates'][:10]:
        print(f"   ID {log_id} duplicates ID {orig_id}: {app_name} ({category}) on {date_str}")
else:
    print("✅ No duplicates\n")

# Summary
total_issues = sum(len(v) for v in issues.values())
print(f"\n{'='*70}")
print(f"TOTAL ISSUES FOUND: {total_issues}")
print(f"{'='*70}\n")

conn.close()
