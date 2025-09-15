from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.api.api_keys import router as api_keys_router
from app.api.virtual_staging import router as virtual_staging_router
from app.middleware.auth import verify_admin_credentials
from app.database.models import DatabaseManager
from app.services.api_key_service import APIKeyService

app = FastAPI(
    title="Virtual Staging API",
    description="API Key Management and Virtual Staging System with Role-Based Access",
    version="1.0.0"
)

# Add CORS middleware - cross origin resource sharing (CORS) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_manager = DatabaseManager()

# Serve static files (CSS, JS, images)
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Dependency functions
def get_db_manager():
    return DatabaseManager()

def get_api_key_service(db_manager: DatabaseManager = Depends(get_db_manager)):
    return APIKeyService(db_manager)

# Include API routers
app.include_router(api_keys_router, tags=["API Keys"])
app.include_router(virtual_staging_router, prefix="/api/virtual-staging", tags=["Virtual Staging"])

# Simple API validation endpoint for frontend
@app.post("/api/validate")
async def validate_api_key_simple(
    request: dict,
    api_key_service: APIKeyService = Depends(get_api_key_service)
):
    """Simple API key validation endpoint for frontend"""
    print(f"DEBUG: Received validation request: {request}")
    
    try:
        api_key = request.get("api_key", "")
        print(f"DEBUG: Validating API key: {api_key[:20]}..." if len(api_key) > 20 else f"DEBUG: Validating API key: {api_key}")
        
        if not api_key:
            print("DEBUG: No API key provided")
            return {"valid": False, "message": "No API key provided"}
        
        # Use the enhanced validation that includes super admin check
        is_valid, key_info, message, role = api_key_service.validate_api_key_with_role(api_key)
        print(f"DEBUG: Validation result - valid: {is_valid}, message: {message}, role: {role}")
        
        if not is_valid:
            return {"valid": False, "message": message}
        
        # For super admin, return unlimited access
        if role and role.value == "superadmin":
            print("DEBUG: Super admin key detected")
            return {
                "valid": True,
                "message": "Super admin key valid - unlimited access",
                "role": "superadmin"
            }
        
        # For regular users, check quota
        quota_ok, quota_message, quota_info = api_key_service.check_quota_and_rate_limit(key_info.id)
        print(f"DEBUG: Quota check - ok: {quota_ok}, message: {quota_message}")
        
        if not quota_ok:
            return {"valid": False, "message": quota_message}
        
        return {
            "valid": True,
            "message": f"Valid {role.value if role else 'user'} key",
            "role": role.value if role else "user"
        }
        
    except Exception as e:
        print(f"DEBUG: Error during validation: {str(e)}")
        return {"valid": False, "message": f"Validation error: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
async def virtual_staging_interface(request: Request):
    """Serve the modern virtual staging interface"""
    return templates.TemplateResponse("virtual_staging.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Serve the admin panel interface"""
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Virtual Staging API is running"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
