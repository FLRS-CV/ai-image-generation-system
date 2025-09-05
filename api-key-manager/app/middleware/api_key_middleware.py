"""
API Key Middleware and Validation
Provides optional API key validation for endpoints
"""
from fastapi import HTTPException, Depends, Header
from typing import Optional
from app.services.api_key_service import APIKeyService
from app.database.models import DatabaseManager

# Dependency to get API key service
def get_api_key_service():
    db_manager = DatabaseManager()
    return APIKeyService(db_manager)

async def validate_api_key_optional(
    x_api_key: Optional[str] = Header(None, description="Optional API key for tracking and rate limiting"),
    api_key_service: APIKeyService = Depends(get_api_key_service)
) -> Optional[dict]:
    """
    Optional API key validation - returns API key info if provided and valid, None if not provided
    """
    if not x_api_key:
        return None
    
    # Validate the API key with role support (includes super admin)
    is_valid, key_info, message, role = api_key_service.validate_api_key_with_role(x_api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid API key: {message}"
        )
    
    # Update usage statistics (skip for super admin as it has unlimited access)
    if role and role.value != "superadmin" and key_info:
        api_key_service.increment_usage(key_info.id)
    
    return {
        "api_key": x_api_key,
        "key_info": key_info.__dict__ if key_info else {},
        "authenticated": True,
        "role": role.value if role else "user"
    }

async def validate_api_key_required(
    x_api_key: str = Header(..., description="Required API key for authentication"),
    api_key_service: APIKeyService = Depends(get_api_key_service)
) -> dict:
    """
    Required API key validation - raises exception if not provided or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required. Provide it in the X-API-Key header."
        )
    
    # Validate the API key with role support (includes super admin)
    is_valid, key_info, message, role = api_key_service.validate_api_key_with_role(x_api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid API key: {message}"
        )
    
    # Update usage statistics (skip for super admin as it has unlimited access)
    if role and role.value != "superadmin" and key_info:
        api_key_service.increment_usage(key_info.id)
    
    return {
        "api_key": x_api_key,
        "key_info": key_info.__dict__ if key_info else {},
        "authenticated": True,
        "role": role.value if role else "user"
    }
