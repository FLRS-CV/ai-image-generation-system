from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.api_key_models import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyListResponse,
    APIKeyValidationRequest, APIKeyValidationResponse
)
from app.services.api_key_service import APIKeyService
from app.database.models import DatabaseManager
from app.middleware.auth import verify_admin_credentials

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

# Dependency to get database manager
def get_db_manager():
    return DatabaseManager()

# Dependency to get API key service
def get_api_key_service(db_manager: DatabaseManager = Depends(get_db_manager)):
    return APIKeyService(db_manager)

@router.post("/", response_model=dict)
async def create_api_key(
    key_data: APIKeyCreate,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """Create a new API key (Admin only)"""
    try:
        full_key, key_info = api_key_service.generate_api_key(key_data)
        
        print("="*80)
        print("🎉 NEW API KEY GENERATED")
        print("="*80)
        print(f"Name: {key_data.name}")
        print(f"User: {key_data.user_email}")
        print(f"Organization: {key_data.organization or 'N/A'}")
        print(f"Daily Quota: {key_data.daily_quota}")
        print(f"Rate Limit: {key_data.rate_limit}/min")
        print(f"🔑 API KEY: {full_key}")
        print("⚠️  IMPORTANT: Save this key securely. It won't be shown again!")
        print("="*80)
        
        return {
            "message": "API key created successfully",
            "api_key": full_key,
            "key_info": key_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=APIKeyListResponse)
async def list_api_keys(
    user_email: str = None,
    status: str = None,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """List all API keys with optional filtering (Admin only)"""
    try:
        api_keys = api_key_service.list_api_keys(user_email, status)
        return APIKeyListResponse(
            api_keys=api_keys,
            total_count=len(api_keys)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """Get a specific API key by ID (Admin only)"""
    try:
        key_info = api_key_service.get_api_key_by_id(key_id)
        if not key_info:
            raise HTTPException(status_code=404, detail="API key not found")
        return key_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: int,
    update_data: APIKeyUpdate,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """Update an API key's properties (Admin only)"""
    try:
        updated_key = api_key_service.update_api_key(key_id, update_data)
        if not updated_key:
            raise HTTPException(status_code=404, detail="API key not found or no changes made")
        return updated_key
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """Permanently delete an API key (Admin only)"""
    try:
        success = api_key_service.delete_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        return {"message": "API key deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=APIKeyValidationResponse)
async def validate_api_key(
    request: APIKeyValidationRequest,
    api_key_service: APIKeyService = Depends(get_api_key_service)
):
    """Validate an API key and return its information"""
    try:
        is_valid, key_info, message = api_key_service.validate_api_key(request.api_key)
        
        if not is_valid:
            return APIKeyValidationResponse(
                valid=False,
                message=message
            )
        
        # Check quota and rate limit
        quota_ok, quota_message, quota_info = api_key_service.check_quota_and_rate_limit(key_info.id)
        
        if not quota_ok:
            return APIKeyValidationResponse(
                valid=True,
                message=f"Key valid but {quota_message}",
                key_info=key_info,
                remaining_quota=quota_info.get("daily_quota", 0) - quota_info.get("current_usage", 0),
                rate_limit_remaining=quota_info.get("rate_limit", 0)
            )
        
        return APIKeyValidationResponse(
            valid=True,
            message="API key valid and ready to use",
            key_info=key_info,
            remaining_quota=quota_info.get("daily_quota", 0) - quota_info.get("current_usage", 0),
            rate_limit_remaining=quota_info.get("rate_limit", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: int,
    api_key_service: APIKeyService = Depends(get_api_key_service),
    admin_user: str = Depends(verify_admin_credentials)
):
    """Revoke an API key (soft delete) (Admin only)"""
    try:
        success = api_key_service.revoke_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found or already revoked")
        return {"message": "API key revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
