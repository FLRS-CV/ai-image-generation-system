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

# Include API routers
app.include_router(api_keys_router, tags=["API Keys"])
app.include_router(virtual_staging_router, prefix="/api/virtual-staging", tags=["Virtual Staging"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page with role-based UI"""
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Virtual Staging API is running"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
