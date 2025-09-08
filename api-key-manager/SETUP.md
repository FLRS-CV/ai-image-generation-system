# 🚀 AI Image Generation System - Setup Guide

This guide will help you set up the AI Image Generation System with role-based access control and virtual staging capabilities.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- ComfyUI (for virtual staging functionality)

## 🔧 Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/FLRS-CV/ai-image-generation-system.git
cd ai-image-generation-system/api-key-manager
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the environment template
copy .env.example .env
# On macOS/Linux: cp .env.example .env

# Edit the .env file with your text editor
# Replace 'your-super-admin-key-here' with the actual super admin key
```

**Important**: Contact your team lead to get the super admin API key. The `.env` file should look like:
```properties
SUPER_ADMIN_API_KEY=sk-proj-superadmin-iRskCpsLWvWjAWAfqVYEZXkACrJmtYr-
DATABASE_URL=sqlite:///./api_keys.db
HOST=0.0.0.0
PORT=8004
```

### Step 5: Start the Server
```bash
python run_server.py
```

You should see:
```
🚀 Starting API Key Manager Server...
📍 Server listening on: 0.0.0.0:8004
🌐 Access via: http://localhost:8004
```

### Step 6: Verify Setup
1. Open your browser and go to `http://localhost:8004`
2. Enter the super admin API key you received
3. You should see your role as "SUPERADMIN" with access to all features

## 🎯 Next Steps

### Create Your Personal Admin Account
1. Use the super admin access to navigate to **Administration > Create Key**
2. Create an admin account for yourself:
   - **Role**: Admin (for most users) or User (for virtual staging only)
   - **Email**: Your email address
   - **Name**: Your preferred name
3. Save the generated API key for your personal use
4. Test logging in with your personal API key

### Understand Role Hierarchy
- **Super Admin**: Can create admins/users, manage all keys, virtual staging
- **Admin**: Can create users only, virtual staging access
- **User**: Virtual staging access only

## 🔧 ComfyUI Setup (Optional - For Virtual Staging)

If you plan to use the virtual staging features:

1. Install ComfyUI separately
2. Start ComfyUI server (usually on port 8188)
3. Ensure ComfyUI is running before using virtual staging features

## 🐛 Troubleshooting

### Common Issues

**"Invalid API key"**
- Double-check the super admin key is correctly copied
- Ensure no extra spaces or characters
- Verify the `.env` file is in the correct location

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**"Port already in use"**
- Check if another service is using port 8004
- Change the PORT in `.env` file if needed

**Database issues**
- Delete `api_keys.db` file and restart (will reset all data)
- Check database file permissions

### Getting Help

1. Check the main `README.md` for project overview
2. Review API documentation at `http://localhost:8004/docs` when server is running
3. Contact your team lead for super admin key or access issues

## 🔐 Security Notes

- **Never commit your `.env` file to git**
- Keep your super admin key secure and private
- Create personal admin accounts instead of sharing the super admin key
- The super admin key should only be used for initial setup and emergency access

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8004/docs` (when server is running)
- **Interactive API**: `http://localhost:8004/redoc`
- **Virtual Staging**: Use the web interface or API endpoints for image generation

---

**Happy coding! 🎉**
