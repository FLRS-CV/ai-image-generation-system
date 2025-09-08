#!/usr/bin/env python3
"""
Setup Validation Script
Run this after setup to verify everything is configured correctly
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is sufficient"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version.major}.{version.minor} (need 3.8+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path('.env')
    if not env_path.exists():
        return False, ".env file not found"
    
    env_content = env_path.read_text()
    if 'your-super-admin-key-here' in env_content:
        return False, ".env still contains placeholder key"
    
    if 'SUPER_ADMIN_API_KEY=' not in env_content:
        return False, "SUPER_ADMIN_API_KEY not found in .env"
    
    return True, ".env file configured"

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn', 
        'pydantic': 'pydantic',
        'python-dotenv': 'dotenv'  # Package name vs import name
    }
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    return True, "All dependencies installed"

def check_database():
    """Check if database can be created/accessed"""
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        conn.close()
        return True, "Database access OK"
    except Exception as e:
        return False, f"Database error: {e}"

def main():
    """Run all validation checks"""
    print("🔍 AI Image Generation System - Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Database Access", check_database),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{name:<20} {status} - {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"{name:<20} ❌ ERROR - {e}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 Setup validation completed successfully!")
        print("Next steps:")
        print("1. Run: python run_server.py")
        print("2. Open: http://localhost:8004")
        print("3. Test super admin login")
        return 0
    else:
        print("⚠️  Setup validation failed!")
        print("Please fix the issues above and run validation again.")
        print("See SETUP.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
