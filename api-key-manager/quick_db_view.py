#!/usr/bin/env python3
"""
Quick database viewer - shows API keys in a simple table format
"""
import sqlite3
import os
from datetime import datetime

def quick_view_db(db_path="api_keys.db"):
    """Quick view of database contents"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database '{db_path}' not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all API keys
    cursor.execute("""
        SELECT id, key_prefix, name, role, user_email, status, created_at
        FROM api_keys 
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    
    print("🔑 API Keys Database - Quick View")
    print("=" * 100)
    print(f"{'ID':<3} {'Key Prefix':<15} {'Role':<10} {'Name':<20} {'Email':<25} {'Status':<8} {'Created'}")
    print("-" * 100)
    
    for row in rows:
        created = row[6][:16] if row[6] else "N/A"  # Show only date and time
        print(f"{row[0]:<3} {row[1]:<15} {row[3].upper():<10} {row[2][:20]:<20} {row[4][:25]:<25} {row[5]:<8} {created}")
    
    print(f"\nTotal records: {len(rows)}")
    
    conn.close()

if __name__ == "__main__":
    quick_view_db()
