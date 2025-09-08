#!/usr/bin/env python3
"""
Simple script to read and display API keys database contents
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os

def read_api_keys_db(db_path="api_keys.db"):
    """Read and display all data from api_keys.db"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        print("🔍 Reading API Keys Database")
        print("=" * 60)
        
        # Get table schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(api_keys)")
        columns = cursor.fetchall()
        
        print("\n📋 Table Schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")
        
        # Read all API keys
        query = """
        SELECT 
            id, key_prefix, name, status, user_email, organization, role,
            created_at, last_used, revoked_at, rate_limit, daily_quota,
            current_daily_usage, last_quota_reset
        FROM api_keys 
        ORDER BY created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        print(f"\n📊 Total API Keys: {len(df)}")
        print("\n🔑 API Keys Summary:")
        print("-" * 80)
        
        if len(df) > 0:
            # Display formatted data
            for index, row in df.iterrows():
                print(f"\n#{row['id']} - {row['key_prefix']}")
                print(f"  📛 Name: {row['name']}")
                print(f"  👤 Role: {row['role'].upper()}")
                print(f"  📧 Email: {row['user_email']}")
                print(f"  🏢 Organization: {row['organization'] or 'N/A'}")
                print(f"  📊 Status: {row['status']}")
                print(f"  📅 Created: {row['created_at']}")
                print(f"  🕒 Last Used: {row['last_used'] or 'Never'}")
                print(f"  🚫 Revoked: {row['revoked_at'] or 'No'}")
                print(f"  ⚡ Rate Limit: {row['rate_limit']}/min")
                print(f"  📈 Daily Quota: {row['current_daily_usage']}/{row['daily_quota']}")
                print(f"  🔄 Quota Reset: {row['last_quota_reset']}")
                print("-" * 40)
        else:
            print("  No API keys found in database")
        
        # Role statistics
        print("\n📈 Role Statistics:")
        role_counts = df['role'].value_counts() if len(df) > 0 else pd.Series()
        for role, count in role_counts.items():
            print(f"  {role.upper()}: {count}")
        
        # Status statistics
        print("\n📊 Status Statistics:")
        status_counts = df['status'].value_counts() if len(df) > 0 else pd.Series()
        for status, count in status_counts.items():
            print(f"  {status.upper()}: {count}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def search_user(email=None, role=None, db_path="api_keys.db"):
    """Search for specific users in the database"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        
        query = "SELECT * FROM api_keys WHERE 1=1"
        params = []
        
        if email:
            query += " AND user_email LIKE ?"
            params.append(f"%{email}%")
        
        if role:
            query += " AND role = ?"
            params.append(role.lower())
        
        query += " ORDER BY created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        
        print(f"\n🔍 Search Results ({len(df)} found):")
        print("-" * 60)
        
        for index, row in df.iterrows():
            print(f"ID: {row['id']} | {row['key_prefix']} | {row['role'].upper()} | {row['user_email']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error searching database: {e}")

if __name__ == "__main__":
    print("🔐 API Keys Database Reader")
    print("Choose an option:")
    print("1. View all API keys")
    print("2. Search by email")
    print("3. Search by role")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            read_api_keys_db()
        elif choice == "2":
            email = input("Enter email to search: ").strip()
            search_user(email=email)
        elif choice == "3":
            role = input("Enter role (user/admin/superadmin): ").strip()
            search_user(role=role)
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")
