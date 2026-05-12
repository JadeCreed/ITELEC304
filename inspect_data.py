#!/usr/bin/env python
"""
Data inspection and quality check script for ScreenTimeLog
"""
import os
import sys
import django
from datetime import date, timedelta
from collections import Counter

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focusflow.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from analytics.models import ScreenTimeLog, CATEGORY_CHOICES

def inspect_data():
    """Inspect data quality issues."""
    logs = ScreenTimeLog.objects.all()
    total_records = logs.count()
    
    print(f"\n{'='*60}")
    print(f"DATA QUALITY INSPECTION REPORT")
    print(f"{'='*60}\n")
    
    print(f"Total Records: {total_records}\n")
    
    if total_records == 0:
        print("✅ Database is empty - no data quality issues found.")
        return
    
    # Issue 1: Invalid categories
    print("1️⃣  INVALID CATEGORIES")
    print("-" * 60)
    valid_cats = [c[0] for c in CATEGORY_CHOICES]
    invalid_logs = logs.exclude(category__in=valid_cats)
    if invalid_logs.exists():
        print(f"❌ Found {invalid_logs.count()} records with invalid categories:")
        for log in invalid_logs[:10]:
            print(f"   - ID {log.id}: '{log.category}' (valid: {', '.join(valid_cats)})")
    else:
        print("✅ All categories are valid\n")
    
    # Issue 2: Negative/Zero durations
    print("2️⃣  INVALID DURATIONS (≤ 0)")
    print("-" * 60)
    invalid_duration = logs.filter(duration_minutes__lte=0)
    if invalid_duration.exists():
        print(f"❌ Found {invalid_duration.count()} records with invalid durations:")
        for log in invalid_duration[:10]:
            print(f"   - ID {log.id}: {log.app_name} = {log.duration_minutes} min")
    else:
        print("✅ All durations are positive\n")
    
    # Issue 3: Future dates
    print("3️⃣  FUTURE DATES")
    print("-" * 60)
    future_logs = logs.filter(date__gt=date.today())
    if future_logs.exists():
        print(f"❌ Found {future_logs.count()} records with future dates:")
        for log in future_logs[:10]:
            print(f"   - ID {log.id}: {log.date} (today: {date.today()})")
    else:
        print("✅ No future dates\n")
    
    # Issue 4: Empty/whitespace app names
    print("4️⃣  EMPTY OR WHITESPACE APP NAMES")
    print("-" * 60)
    empty_app_logs = logs.filter(app_name__in=['', ' '])
    if empty_app_logs.exists():
        print(f"❌ Found {empty_app_logs.count()} records with empty app names")
    else:
        print("✅ All app names are populated\n")
    
    # Issue 5: Duplicates (same app, category, date, duration)
    print("5️⃣  POTENTIAL DUPLICATES")
    print("-" * 60)
    # Find exact duplicates
    seen = {}
    duplicates = []
    for log in logs:
        key = (log.app_name, log.category, log.date, log.duration_minutes)
        if key in seen:
            duplicates.append((log.id, seen[key]))
        else:
            seen[key] = log.id
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate records:")
        for curr_id, original_id in duplicates[:10]:
            log = logs.get(id=curr_id)
            print(f"   - ID {curr_id} duplicates ID {original_id}: {log.app_name} ({log.category}) on {log.date}")
    else:
        print("✅ No exact duplicates found\n")
    
    # Issue 6: Unrealistic durations (>1440 min per day)
    print("6️⃣  UNREALISTIC DURATIONS (> 1440 min/day)")
    print("-" * 60)
    unrealistic = logs.filter(duration_minutes__gt=1440)
    if unrealistic.exists():
        print(f"❌ Found {unrealistic.count()} records with >1440 minutes:")
        for log in unrealistic[:10]:
            print(f"   - ID {log.id}: {log.app_name} = {log.duration_minutes} min on {log.date}")
    else:
        print("✅ All durations are realistic (≤ 1440 min/day)\n")
    
    # Issue 7: Whitespace in app names (leading/trailing)
    print("7️⃣  WHITESPACE IN APP NAMES")
    print("-" * 60)
    whitespace_issues = []
    for log in logs:
        if log.app_name != log.app_name.strip():
            whitespace_issues.append(log.id)
    
    if whitespace_issues:
        print(f"❌ Found {len(whitespace_issues)} records with whitespace in app names:")
        for log_id in whitespace_issues[:10]:
            log = logs.get(id=log_id)
            print(f"   - ID {log.id}: '{log.app_name}'")
    else:
        print("✅ No whitespace issues in app names\n")
    
    # Issue 8: Very old dates (> 365 days ago)
    print("8️⃣  VERY OLD DATES (> 365 days ago)")
    print("-" * 60)
    old_threshold = date.today() - timedelta(days=365)
    old_logs = logs.filter(date__lt=old_threshold)
    if old_logs.exists():
        print(f"⚠️  Found {old_logs.count()} records older than 365 days")
        oldest = old_logs.order_by('date').first()
        print(f"   - Oldest record: {oldest.date}")
    else:
        print("✅ All records are within the last 365 days\n")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total issues found: {invalid_logs.count() + invalid_duration.count() + future_logs.count() + len(duplicates) + unrealistic.count() + len(whitespace_issues)}")
    print()

if __name__ == '__main__':
    inspect_data()
