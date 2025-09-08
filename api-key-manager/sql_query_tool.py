#!/usr/bin/env python3
"""
Interactive SQL query tool for api_keys.db
"""
import sqlite3
import os

def run_sql_query(db_path="api_keys.db"):
    """Interactive SQL query runner"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database '{db_path}' not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🗄️ SQL Query Tool for API Keys Database")
    print("Type 'help' for common queries, 'quit' to exit")
    print("=" * 60)
    
    # Common queries
    common_queries = {
        "help": "Show this help",
        "all": "SELECT * FROM api_keys",
        "roles": "SELECT role, COUNT(*) as count FROM api_keys GROUP BY role",
        "active": "SELECT * FROM api_keys WHERE status = 'active'",
        "admins": "SELECT * FROM api_keys WHERE role IN ('admin', 'superadmin')",
        "schema": "PRAGMA table_info(api_keys)",
        "recent": "SELECT * FROM api_keys ORDER BY created_at DESC LIMIT 5"
    }
    
    while True:
        query = input("\nSQL> ").strip()
        
        if query.lower() == 'quit':
            break
        elif query.lower() == 'help':
            print("\n📚 Common Queries:")
            for cmd, desc in common_queries.items():
                if cmd != "help":
                    print(f"  {cmd:<8} - {desc}")
            continue
        elif query.lower() in common_queries:
            query = common_queries[query.lower()]
        
        try:
            cursor.execute(query)
            
            if query.upper().startswith('SELECT') or query.upper().startswith('PRAGMA'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                if results:
                    # Print column headers
                    print("\n" + " | ".join(f"{col:<15}" for col in columns))
                    print("-" * (len(columns) * 17))
                    
                    # Print rows
                    for row in results:
                        print(" | ".join(f"{str(val)[:15]:<15}" for val in row))
                    
                    print(f"\n📊 {len(results)} rows returned")
                else:
                    print("No results found")
            else:
                conn.commit()
                print(f"✅ Query executed successfully")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    conn.close()
    print("👋 Goodbye!")

if __name__ == "__main__":
    run_sql_query()
