# API Key Manager & Deco Core POC Integration

This document outlines how to test the complete API key validation workflow.

## Prerequisites

1. **API Key Manager** running on `http://localhost:8000`
2. **ComfyUI** running on `http://localhost:8188`
3. **Flask Backend** (`server.py`) running on `http://localhost:5000`
4. **Next.js Frontend** running on `http://localhost:3000`

## Testing Steps

### 1. Start the API Key Manager
```bash
cd api-key-manager
python run_server.py
```
Server should start on: http://localhost:8000

### 2. Create an API Key
1. Open http://localhost:8000 in your browser
2. Fill in the "Create API Key" form:
   - Name: "Test Key"
   - User Email: "test@example.com"
   - Organization: "Test Org"
   - Daily Quota: 50
   - Rate Limit: 30
3. Click "Create API Key"
4. **Copy the generated API key** (starts with `sk-proj-`)

### 3. Start ComfyUI
```bash
# In your ComfyUI directory
python main.py
```
Should be running on: http://localhost:8188

### 4. Start Flask Backend
```bash
cd Deco_Core_POC
python server.py
```
Should be running on: http://localhost:5000

### 5. Start Next.js Frontend
```bash
cd Deco_Core_POC/virtual-staging-app
npm install  # First time only
npm run dev
```
Should be running on: http://localhost:3000

### 6. Test the Complete Workflow
1. Open http://localhost:3000
2. Upload an image file
3. **Enter the API key** you created in step 2
4. Fill in other parameters (prompt, etc.)
5. Click "Generate"

### Expected Behaviors

#### With Valid API Key:
- API key field turns green
- Shows "Valid API key. Quota remaining: X"
- Image generation proceeds normally
- Middleware allows the request through

#### With Invalid API Key:
- API key field turns red
- Shows "Invalid API key"
- Error message: "Invalid API key" or "API key required"
- Image generation is blocked

#### With No API Key:
- Error message: "Please provide a valid API key"
- Submit button should be disabled

## Architecture Flow

```
Frontend (Next.js) → Middleware → API Key Manager (validation) → Next.js API Route → Flask Backend → ComfyUI
```

1. **User submits form** with API key in Next.js
2. **Middleware intercepts** the request to `/api/generate`
3. **Middleware validates** API key against API Key Manager
4. **If valid**: Request proceeds to Next.js API route
5. **API route forwards** request to Flask backend
6. **Flask processes** image generation via ComfyUI
7. **Response flows back** through the chain

## Troubleshooting

### Common Issues:

1. **"API Key Manager unavailable"**
   - Ensure API Key Manager is running on port 8000
   - Check if port is already in use

2. **TypeScript errors in VS Code**
   - Run `npm install` to install dependencies
   - Restart VS Code TypeScript server

3. **CORS errors**
   - API Key Manager has CORS enabled for all origins
   - Ensure all services are running on expected ports

4. **Image generation fails**
   - Verify ComfyUI is running and accessible
   - Check Flask backend logs for errors
   - Ensure workflow files exist in ComfyUI

### Debug Commands:

Test API Key Manager directly:
```bash
curl -X POST "http://localhost:8000/api/keys/validate" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-api-key-here"}'
```

Test Flask backend directly:
```bash
curl -X POST "http://localhost:5000/generate" \
  -F "image_file=@test-image.jpg" \
  -F "prompt_text=modern living room"
```
