# 📋 Quick Reference

## 🚀 Essential Commands

```bash
# Setup (one-time)
git clone https://github.com/FLRS-CV/ai-image-generation-system.git
cd ai-image-generation-system/api-key-manager
cp .env.example .env
pip install -r requirements.txt

# Validate setup
python validate_setup.py

# Start server
python run_server.py

# Access
http://localhost:8004
```

## 🔑 Super Admin Key
**Key**: `sk-proj-superadmin-iRskCpsLWvWjAWAfqVYEZXkACrJmtYr-`
**Use**: Initial setup and emergency access only

## 👥 Role Hierarchy
- **Super Admin** → All permissions
- **Admin** → Create users + Virtual staging  
- **User** → Virtual staging only

## 📂 Key Files
- `.env` - Your local environment config (never commit!)
- `.env.example` - Template for environment setup
- `SETUP.md` - Detailed setup instructions
- `validate_setup.py` - Check if setup is correct
- `run_server.py` - Start the application

## 🌐 URLs
- **Main App**: http://localhost:8004
- **API Docs**: http://localhost:8004/docs  
- **Interactive Docs**: http://localhost:8004/redoc

## 🆘 Troubleshooting
1. Check `validate_setup.py` output
2. Verify `.env` has correct super admin key
3. Ensure virtual environment is activated
4. Check if port 8004 is available

## 📞 Getting Help
1. Read `SETUP.md` for detailed instructions
2. Check `ONBOARDING.md` for team-specific info
3. Contact your team lead for access issues
