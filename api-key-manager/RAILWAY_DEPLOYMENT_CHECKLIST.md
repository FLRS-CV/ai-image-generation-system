# ✅ Railway Deployment Checklist

## 📂 Required Files in `api-key-manager-standalone` folder:

### ✅ Core Application Files:
- ✅ `app/` folder with all Python files
- ✅ `app/main.py` - Main FastAPI application (with PORT env var support)
- ✅ `app/models/api_key_models.py` - Pydantic models
- ✅ `app/services/api_key_service.py` - Business logic
- ✅ `app/database/models.py` - Database manager
- ✅ `app/api/api_keys.py` - API endpoints

### ✅ Railway Deployment Files:
- ✅ `requirements.txt` - Python dependencies (includes gunicorn)
- ✅ `Procfile` - Railway startup command
- ✅ `railway.json` - Railway configuration

### ✅ Optional Files:
- ✅ `run_server.py` - Local development server
- ✅ `api_keys.db` - Local SQLite database (will be recreated on Railway)

## 🚀 Railway Deployment Steps:

### 1. Push to Git Repository:
```bash
# Initialize git in api-key-manager-standalone folder
git init
git add .
git commit -m "Initial API Key Manager deployment"

# Push to GitHub/GitLab (create repository first)
git remote add origin https://github.com/yourusername/api-key-manager.git
git push -u origin main
```

### 2. Deploy on Railway:
1. Go to https://railway.app/
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-deploy!

### 3. Get Your Deployment URL:
Railway will provide a URL like:
```
https://api-key-manager-production-xxxx.up.railway.app
```

## 🧪 Test Your Deployment:

### 1. Health Check:
```bash
curl https://your-railway-url.railway.app/health
# Should return: {"status":"healthy","service":"API Key Manager"}
```

### 2. Create Test API Key:
```bash
curl -X POST "https://your-railway-url.railway.app/api/keys/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Key",
    "user_email": "test@example.com",
    "daily_quota": 100,
    "rate_limit": 60
  }'
```

### 3. Validate API Key:
```bash
curl -X POST "https://your-railway-url.railway.app/api/keys/validate" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-proj-your-generated-key"}'
```

## 🔧 Frontend Integration:

Update your main image generation app with:
```javascript
const API_KEY_MANAGER_URL = "https://your-railway-url.railway.app";
```

## 📧 Sharing API Keys:

1. **Web Interface**: Visit your Railway URL to create keys
2. **Programmatic**: Use the API endpoints to create keys
3. **Email**: Share keys with users via email

## 🔍 Troubleshooting:

### Deployment Issues:
- Check Railway logs in dashboard
- Verify all files are present in repository
- Ensure requirements.txt includes all dependencies

### Runtime Issues:
- Check Railway application logs
- Verify environment variables if needed
- Test health endpoint first

## ✅ Success Indicators:

- ✅ Railway deployment successful (green status)
- ✅ Health endpoint returns 200 OK
- ✅ Can create API keys via web interface
- ✅ API key validation works
- ✅ CORS allows frontend connections
- ✅ Database persists data

## 🎯 Final Integration:

Your main image generation app should:
1. **Frontend**: Validate API keys against Railway URL
2. **Backend**: Optional validation for extra security
3. **Users**: Receive API keys via email/web interface

Ready for Railway deployment! 🚀
