# AI Virtual Staging System with API Key Management

🎨 **Transform empty rooms into beautifully furnished spaces using AI** 

A complete FastAPI-based system that combines secure API key management with AI-powered virtual staging capabilities. Upload an empty room image and get professionally furnished variations using ComfyUI and advanced AI models.

## ✨ Features

### 🔐 **Two-Layer API Key Security**
- **Frontend Validation**: Real-time API key checking with visual feedback
- **Middleware Protection**: Server-side enforcement before AI processing
- **Usage Tracking**: Automatic increment of API usage counters
- **Admin Panel**: Secure management interface with HTTP Basic Auth

### 🎨 **AI Virtual Staging**
- **ComfyUI Integration**: Advanced AI workflows for room transformation
- **Multiple Styles**: Scandinavian (with more coming soon)
- **Batch Generation**: Create multiple variations in one request
- **High Quality**: Upscaling and refinement for professional results

### 📊 **Management Features**
- **API Key CRUD**: Create, read, update, delete, and revoke keys
- **Quota Management**: Daily usage limits and rate limiting
- **User Tracking**: Monitor usage patterns and activity
- **Comprehensive Logging**: Track all validation and generation attempts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- ComfyUI server running on port 8188
- Required AI models installed in ComfyUI

### Installation

1. **Clone and setup**:
   ```bash
   git clone https://github.com/FLRS-CV/ai-image-generation-system.git
   cd ai-image-generation-system/api-key-manager
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python run_server.py
   ```

3. **Access the application**:
   - **Virtual Staging**: http://localhost:8004/
   - **Admin Panel**: http://localhost:8004/admin (admin/admin)
   - **API Docs**: http://localhost:8004/docs

## 🎯 How It Works

### For Users:
1. **Enter API Key**: Get immediate validation feedback
2. **Upload Room Image**: Select empty room photo
3. **Choose Settings**: Number of variations and style
4. **Generate**: AI transforms your room in minutes

### For Administrators:
1. **Create API Keys**: Generate keys for users/applications
2. **Monitor Usage**: Track quotas and activity
3. **Manage Access**: Revoke or update keys as needed

## 🏗️ Architecture

```
Frontend (HTML/JS) → API Validation → Middleware Protection → ComfyUI AI → Results
     ↓                    ↓                 ↓                  ↓          ↓
Real-time UX      Layer 1 Security   Layer 2 Security    AI Processing  Base64 Images
```

## 📝 API Usage

### Authentication
All virtual staging requests require an `X-API-Key` header:

```bash
curl -X POST "http://localhost:8004/api/virtual-staging" \
  -H "X-API-Key: sk-proj-your-api-key-here" \
  -F "image_file=@room.jpg" \
  -F "num_images=3" \
  -F "style=scandinavian"
```

### Response Format
```json
{
  "success": true,
  "message": "Successfully generated 3 images",
  "results": [
    {
      "image": "data:image/png;base64,iVBORw0KGgoAAAANSU...",
      "style": "scandinavian",
      "seed": 1234567,
      "index": 1
    }
  ],
  "metadata": {
    "style": "scandinavian",
    "num_images": 3,
    "original_filename": "room.jpg"
  }
}
```

## 🔒 Security Features

### API Key Protection
- **Format Validation**: Ensures proper `sk-proj-` format
- **Database Verification**: Checks against stored hashes
- **Usage Enforcement**: Respects quotas and rate limits
- **Activity Logging**: Comprehensive audit trail

### Admin Access
- **HTTP Basic Auth**: Secure admin panel access
- **Credential Protection**: Uses `secrets.compare_digest()`
- **Session Management**: Secure authentication handling

## 🛠️ Configuration

### Environment Variables
Create `.env` file for production:
```env
ADMIN_USERNAME=your_admin_user
ADMIN_PASSWORD=your_secure_password
COMFY_HOST=127.0.0.1
COMFY_PORT=8188
DATABASE_URL=sqlite:///api_keys.db
```

### ComfyUI Setup
1. Install ComfyUI with required models:
   - `juggernaut_reborn.safetensors`
   - `stable_design_depth_diffusion_pytorch_model.safetensors`
   - `stable_design_segment_diffusion_pytorch_model.safetensors`

2. Place `joger.json` workflow in ComfyUI directory

## 📊 Monitoring & Analytics

### Built-in Logging
```
🔒 MIDDLEWARE: API key validation successful!
🔑 User: user@example.com
🏢 Organization: Company ABC
🎯 Starting virtual staging generation...
```

### Usage Tracking
- Daily quota consumption
- Request success/failure rates
- Processing times and performance
- User activity patterns

## 🧪 Testing

Run the test suite:
```bash
# Test API endpoints
python test_api.py

# Test ComfyUI connection
python test_comfy.py

# Test virtual staging directly
python test_virtual_staging.py
```

## 📁 Project Structure

```
api-key-manager/
├── app/
│   ├── api/
│   │   ├── api_keys.py          # Admin API endpoints
│   │   └── virtual_staging.py   # Protected staging endpoints
│   ├── middleware/
│   │   ├── api_key_middleware.py # Two-layer validation
│   │   └── auth.py              # Admin authentication
│   ├── services/
│   │   ├── api_key_service.py   # Business logic
│   │   └── comfy_wrapper.py     # ComfyUI integration
│   ├── database/
│   │   └── models.py            # Database operations
│   ├── models/
│   │   └── api_key_models.py    # Pydantic schemas
│   └── main.py                  # FastAPI app + frontend
├── joger.json                   # ComfyUI workflow
├── requirements.txt             # Dependencies
├── run_server.py               # Application launcher
└── VIRTUAL_STAGING_IMPLEMENTATION.md  # Technical documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues for bug reports
- **Documentation**: See `VIRTUAL_STAGING_IMPLEMENTATION.md` for detailed technical information
- **API Reference**: Available at `/docs` endpoint when server is running

## 🔮 Roadmap

- [ ] Additional furnishing styles (Modern, Traditional, Industrial)
- [ ] User account system with personal galleries
- [ ] Cloud storage integration (AWS S3)
- [ ] Advanced AI models and workflows
- [ ] Mobile app support
- [ ] Enterprise features and analytics

---

**Built with ❤️ using FastAPI, ComfyUI, and modern AI models**

**Version**: 1.0.0 | **Status**: ✅ Production Ready | **Security**: 🛡️ Two-Layer Protection
