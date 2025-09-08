# 🎨 AI Image Generation System with Role-Based Access Control

A complete microservices-based AI image generation platform featuring role-based authentication, team collaboration tools, and ComfyUI integration.

## 🚀 **Quick Start for New Team Members**

### For New Team Members:
1. **Clone the repository**
2. **Follow the setup guide**: [api-key-manager/SETUP.md](api-key-manager/SETUP.md)
3. **Get super admin key** from your team lead
4. **Create your personal admin account** after initial setup

### TL;DR Setup:
```bash
git clone https://github.com/FLRS-CV/ai-image-generation-system.git
cd ai-image-generation-system/api-key-manager
pip install -r requirements.txt
cp .env.example .env
# Edit .env with super admin key, then:
python run_server.py
```
🌐 **Access**: `http://localhost:8004`

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────┐
│                Next.js Frontend                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ UI/UX       │  │ Middleware  │  │ API Route│ │ 
│  │ Components  │  │ (Security)  │  │(Gateway) │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
            ┌───────▼──────┐ ┌────▼─────────┐
            │ API Key Mgr  │ │ Flask Backend│
            │  (FastAPI)   │ │  + ComfyUI   │
            │   Port 8004  │ │   Port 5000  │
            └──────────────┘ └──────────────┘
```

## 🚀 **Features**

### **🔐 Role-Based Access Control**
- ✅ **Super Admin**: Create admins/users, manage all keys, virtual staging
- ✅ **Admin**: Create users only, virtual staging access  
- ✅ **User**: Virtual staging access only
- ✅ **Environment-Based Security**: Super admin key via secure .env configuration

### **👥 Team Collaboration**
- ✅ **Shared Super Admin Key**: Secure team access for onboarding
- ✅ **Personal Admin Accounts**: Individual admin accounts for daily use
- ✅ **Automated Setup Validation**: Script to verify correct configuration
- ✅ **Comprehensive Documentation**: Step-by-step guides for new team members

### **Security & Authentication**
- ✅ **API Key Management**: Generate, validate, and manage API keys
- ✅ **Request Middleware**: Automatic validation on every API call
- ✅ **Rate Limiting**: Configurable rate limits per API key
- ✅ **Quota Management**: Daily usage limits and tracking
- ✅ **Real-time Validation**: 500ms debounced frontend validation

### **User Experience**
- ✅ **Gated Interface**: Users must authenticate before accessing features
- ✅ **Conditional Rendering**: UI elements appear only after valid authentication
- ✅ **Real-time Feedback**: Immediate validation status updates
- ✅ **Error Handling**: Comprehensive error messages and recovery

### **Image Generation**
- ✅ **ComfyUI Integration**: Advanced AI image processing pipeline
- ✅ **Custom Workflows**: Configurable image generation workflows
- ✅ **Batch Processing**: Multiple image generation support
- ✅ **Format Support**: Multiple input/output image formats

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 14.2.32 + TypeScript | User interface & middleware |
| **Authentication** | FastAPI + SQLite | API key management |
| **Image Processing** | Flask + ComfyUI | AI image generation |
| **Database** | SQLite | API key storage |
| **AI Engine** | ComfyUI + PyTorch | Image generation pipeline |

## 📋 **Prerequisites**

### **Software Requirements**
- **Python 3.8+** (for FastAPI and Flask services)
- **Node.js 18+** (for Next.js frontend)
- **Git** (for version control)

### **Hardware Requirements**
- **GPU**: NVIDIA GPU with CUDA support (recommended for ComfyUI)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ free space for models and generated images

## 🚀 **Installation & Setup**

## 🛠️ **Team Setup Instructions**

### **For Team Leads: Setting Up New Members**
1. **Share Repository Access**: Add team member to GitHub repository
2. **Share Super Admin Key**: Use secure channel (Signal, encrypted email, etc.)
3. **Provide Setup Guide**: Direct them to [api-key-manager/SETUP.md](api-key-manager/SETUP.md)

### **For New Team Members: Getting Started**
1. **Follow Setup Guide**: Complete instructions in [api-key-manager/SETUP.md](api-key-manager/SETUP.md)
2. **Validate Setup**: Run `python validate_setup.py` to check configuration
3. **Create Personal Account**: Use super admin access to create your personal admin account
4. **Test Virtual Staging**: Verify everything works with a test image

### **📚 Documentation & Resources**
- **[SETUP.md](api-key-manager/SETUP.md)** - Detailed setup instructions
- **[ONBOARDING.md](api-key-manager/ONBOARDING.md)** - Team member onboarding guide  
- **[QUICK_REFERENCE.md](api-key-manager/QUICK_REFERENCE.md)** - Essential commands and URLs

---

## 💻 **Development Setup (Full System)**

### **Step 1: Clone Repository**
```bash
git clone https://github.com/FLRS-CV/ai-image-generation-system.git
cd ai-image-generation-system
```

### **Step 2: Setup Python Virtual Environment**
```bash
# Create virtual environment
python -m venv ai_demo

# Activate virtual environment
# Windows:
ai_demo\Scripts\activate
# macOS/Linux:
source ai_demo/bin/activate
```

### **Step 3: Install Python Dependencies**
```bash
# Install API Key Manager dependencies
cd api-key-manager
pip install -r requirements.txt
cd ..

# Install Flask backend dependencies
cd Deco_Core_POC
pip install flask flask-cors websocket-client pillow
cd ..
```

### **Step 4: Install Node.js Dependencies**
```bash
cd Deco_Core_POC/virtual-staging-app
npm install
cd ../..
```

### **Step 5: Setup ComfyUI**
```bash
# Clone ComfyUI (outside project directory)
cd ..
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Download required models (follow ComfyUI documentation)
# Place models in: ComfyUI/models/checkpoints/
```

## 🏃‍♂️ **Running the System**

### **Terminal 1: Start ComfyUI**
```bash
cd ComfyUI
python main.py
# Wait for: "Starting server on: 127.0.0.1:8188"
```

### **Terminal 2: Start API Key Manager**
```bash
cd ai-image-generation-system/api-key-manager
ai_demo\Scripts\activate  # Windows
# source ai_demo/bin/activate  # macOS/Linux
python run_server.py
# Wait for: "Uvicorn running on http://0.0.0.0:8004"
```

### **Terminal 3: Start Flask Backend**
```bash
cd ai-image-generation-system/Deco_Core_POC
ai_demo\Scripts\activate  # Windows
# source ai_demo/bin/activate  # macOS/Linux
python server.py
# Wait for: "Running on http://127.0.0.1:5000"
```

### **Terminal 4: Start Next.js Frontend**
```bash
cd ai-image-generation-system/Deco_Core_POC/virtual-staging-app
npm run dev
# Wait for: "Ready on http://localhost:3000"
```

## 🔑 **First-Time Setup**

### **1. Generate API Key**
```bash
# Visit: http://localhost:8004
# Click "Generate New API Key"
# Fill in details and save the generated key
```

### **2. Test System**
```bash
# Visit: http://localhost:3000
# Enter your API key
# Upload an image and enter a prompt
# Click "Generate" to test the complete workflow
```

## 📊 **Service Overview**

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Next.js Frontend** | 3000 | http://localhost:3000 | Main user interface |
| **API Key Manager** | 8004 | http://localhost:8004 | Authentication service |
| **Flask Backend** | 5000 | http://localhost:5000 | Image processing |
| **ComfyUI** | 8188 | http://localhost:8188 | AI generation engine |

## 🔄 **Request Flow**

```
1. User opens http://localhost:3000
   ↓
2. User enters API key in frontend
   ↓
3. Frontend validates key (debounced, 500ms)
   ↓
4. User uploads image and enters prompt
   ↓
5. Frontend sends POST to /api/generate
   ↓
6. 🛡️ Next.js Middleware intercepts request
   ↓
7. Middleware validates API key with Key Manager
   ↓ (if valid)
8. Request forwarded to API route handler
   ↓
9. API route forwards to Flask backend
   ↓
10. Flask processes with ComfyUI via WebSocket
    ↓
11. Generated image returned through chain
    ↓
12. User sees generated image
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# API Key Manager (.env)
DATABASE_URL=sqlite:///api_keys.db
HOST=0.0.0.0
PORT=8004

# Flask Backend
COMFY_HOST=127.0.0.1
COMFY_PORT=8188

# Next.js Frontend
NEXT_PUBLIC_API_KEY_MANAGER_URL=http://localhost:8004
```

### **Workflow Configuration**
- **Location**: `Deco_Core_POC/joger.json`
- **Purpose**: ComfyUI workflow definition
- **Customization**: Modify nodes for different image processing pipelines

## 🐛 **Troubleshooting**

### **Common Issues**

#### **ComfyUI Not Starting**
```bash
# Check GPU/CUDA installation
nvidia-smi

# Install CUDA-compatible PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **API Key Validation Failing**
```bash
# Check API Key Manager logs
# Verify database connection
# Ensure all services are running
```

#### **Image Generation Failing**
```bash
# Verify ComfyUI is running on port 8188
# Check joger.json workflow file exists
# Ensure models are downloaded in ComfyUI/models/
```

#### **Frontend Not Loading**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear npm cache
npm cache clean --force
npm install
```

## 📁 **Project Structure**

```
ai-image-generation-system/
├── api-key-manager/              # 🔐 Authentication & Team Management
│   ├── app/                     # Core application
│   │   ├── api/api_keys.py      # API endpoints
│   │   ├── database/models.py    # Database models
│   │   ├── services/            # Business logic
│   │   ├── models/              # Data models
│   │   └── static/main.js       # Frontend interface
│   ├── .env.example            # ✨ Environment template
│   ├── SETUP.md                # ✨ Setup instructions  
│   ├── ONBOARDING.md           # ✨ Team onboarding guide
│   ├── QUICK_REFERENCE.md      # ✨ Quick commands reference
│   ├── validate_setup.py       # ✨ Setup validation script
│   ├── quick_db_view.py        # 🛠️ Database viewer tool
│   ├── read_database.py        # 🛠️ Database reader tool
│   ├── sql_query_tool.py       # 🛠️ SQL query interface
│   ├── requirements.txt        # Python dependencies
│   └── run_server.py           # Server startup
│
├── Deco_Core_POC/               # Main Application
│   ├── server.py               # Flask backend
│   ├── joger.json              # ComfyUI workflow
│   └── virtual-staging-app/    # Next.js frontend
│       ├── app/
│       │   ├── page.tsx        # Main UI component
│       │   └── api/generate/   # API route
│       ├── middleware.ts       # Security middleware
│       ├── lib/               # Utility libraries
│       └── package.json       # Node.js dependencies
│
└── README.md                   # This file
```

**Legend**: ✨ New team collaboration features | 🛠️ Development tools

## 🔒 **Security Features**

### **Middleware Protection**
- **Request Interception**: All API calls validated before processing
- **Header Validation**: API keys passed securely in headers
- **Early Termination**: Invalid requests blocked before resource consumption

### **API Key Management**
- **Secure Generation**: Cryptographically secure key generation
- **Hash Storage**: Keys stored as hashes, never in plain text
- **Usage Tracking**: Comprehensive logging and analytics
- **Quota Enforcement**: Automatic rate limiting and quotas

## 🚀 **Deployment**

### **Development**
- Follow the "Running the System" steps above
- All services run locally on different ports

### **Production**
- Use environment variables for configuration
- Set up reverse proxy (nginx) for SSL termination
- Use production databases (PostgreSQL recommended)
- Implement proper logging and monitoring

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 **Authors**

- **FLRS-CV Team** - Initial work - [FLRS-CV](https://github.com/FLRS-CV)

## 🙏 **Acknowledgments**

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for the amazing AI image generation framework
- [Next.js](https://nextjs.org/) for the excellent React framework
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework

---

## 🆘 **Support**

If you encounter any issues:

1. **Check Prerequisites**: Ensure all software requirements are met
2. **Verify Services**: Confirm all 4 services are running on correct ports
3. **Check Logs**: Review terminal outputs for error messages
4. **GitHub Issues**: Create an issue with detailed error information

**Happy Generating! 🎨✨**
