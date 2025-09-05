"""
Virtual Staging API Endpoints
Handles image generation requests with API key validation
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import shutil
from typing import Optional
from ..services.comfy_wrapper import empty_2_furnished
from ..middleware.api_key_middleware import validate_api_key_required

router = APIRouter()

# Ensure directories exist
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

@router.post("/virtual-staging")
async def generate_virtual_staging(
    image_file: UploadFile = File(...),
    num_images: int = Form(default=1),
    style: str = Form(default="scandinavian"),
    api_key_info: dict = Depends(validate_api_key_required)
):
    """
    Generate virtual staging images from an empty room photo
    
    - **image_file**: Upload an image file of an empty room
    - **num_images**: Number of variations to generate (1-10)
    - **style**: Furnishing style (currently supports: scandinavian)
    - **X-API-Key**: Required API key in header for authentication
    """
    return await _generate_staging_internal(image_file, num_images, style, api_key_info)

@router.post("/generate")
async def generate_virtual_staging_alt(
    file: UploadFile = File(...),
    num_images: int = Form(default=1),
    style: str = Form(default="scandinavian"),
    api_key_info: dict = Depends(validate_api_key_required)
):
    """
    Generate virtual staging images from an empty room photo (alternative endpoint for frontend)
    
    - **file**: Upload an image file of an empty room
    - **num_images**: Number of variations to generate (1-10)
    - **style**: Furnishing style (currently supports: scandinavian)
    - **X-API-Key**: Required API key in header for authentication
    """
    return await _generate_staging_internal(file, num_images, style, api_key_info)

async def _generate_staging_internal(
    image_file: UploadFile,
    num_images: int,
    style: str,
    api_key_info: dict
):
    """Internal function to handle virtual staging generation"""
    
    # Log the API key validation success
    print("🔒 MIDDLEWARE: API key validation successful!")
    print(f"🔑 User: {api_key_info['key_info'].get('user_email', 'Unknown')}")
    print(f"🏢 Organization: {api_key_info['key_info'].get('organization', 'None')}")
    print(f"🎯 Starting virtual staging generation...")
    
    # Validate inputs
    if not image_file.content_type or not image_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if num_images < 1 or num_images > 10:
        raise HTTPException(status_code=400, detail="Number of images must be between 1 and 10")
    
    # Supported styles
    supported_styles = ["scandinavian"]
    if style not in supported_styles:
        raise HTTPException(
            status_code=400, 
            detail=f"Style '{style}' not supported. Available styles: {supported_styles}"
        )
    
    try:
        # Save uploaded file temporarily
        temp_filename = f"temp_{image_file.filename}"
        temp_path = os.path.join("temp_uploads", temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        
        # Generate images using ComfyUI wrapper
        result = empty_2_furnished(
            input_path=os.path.abspath(temp_path),
            num_images=num_images,
            style=style
        )
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass  # Don't fail if cleanup doesn't work
        
        # Return results in format expected by frontend
        if result["status"] == "success":
            # Extract image paths from results
            images = []
            for img_result in result["results"]:
                if "file_path" in img_result:
                    # Convert absolute path to relative path for web serving
                    abs_path = img_result["file_path"]
                    rel_path = os.path.relpath(abs_path, start=os.getcwd())
                    images.append(rel_path.replace("\\", "/"))  # Use forward slashes for web
            
            return {
                "success": True,
                "message": f"Successfully generated {len(images)} virtual staging images",
                "images": images,
                "metadata": {
                    "style": style,
                    "num_images": len(images),
                    "original_filename": image_file.filename
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating virtual staging: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/generated/{filename}")
async def get_generated_image(filename: str):
    """
    Download a generated image file
    """
    file_path = os.path.join("generated", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='image/png'
    )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for virtual staging service
    """
    return {
        "status": "healthy",
        "service": "virtual-staging",
        "version": "1.0.0"
    }
