from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Tuple
from app.models.api_key_models import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyListResponse,
    APIKeyValidationRequest, APIKeyValidationResponse, UserRole
)
from app.services.api_key_service import APIKeyService
from app.database.models import DatabaseManager
from app.middleware.auth import (
    verify_admin_credentials, require_admin_role, require_superadmin_role,
    get_current_user
)

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
    request: Request,
    api_key_service: APIKeyService = Depends(get_api_key_service)
):
    """Create a new API key (Admin+ required, role restrictions apply)"""
    try:
        # Get current user info
        current_user = get_current_user(request, api_key_service)
        if not current_user:
            # Fallback to basic auth for backward compatibility
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_role, current_user_info = current_user
        
        # Check if user can create the requested role
        if not api_key_service.can_create_role(current_role, key_data.role):
            allowed_roles = []
            if current_role == UserRole.SUPERADMIN:
                allowed_roles = ["user", "admin"]
            elif current_role == UserRole.ADMIN:
                allowed_roles = ["user"]
            
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Your role ({current_role.value}) can only create: {', '.join(allowed_roles)}"
            )
        
        # Require minimum admin role for key creation
        if current_role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only admins and super admins can create API keys"
            )
        
        full_key, key_info = api_key_service.generate_api_key(key_data)
        
        print("="*80)
        print("🎉 NEW API KEY GENERATED")
        print("="*80)
        print(f"Created by: {current_user_info.user_email} ({current_role.value})")
        print(f"Name: {key_data.name}")
        print(f"User: {key_data.user_email}")
        print(f"Role: {key_data.role.value}")
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
    request: Request = None,
    api_key_service: APIKeyService = Depends(get_api_key_service)
):
    """List API keys (Admin+ required)"""
    try:
        # Get current user info
        current_user = get_current_user(request, api_key_service)
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_role, current_user_info = current_user
        
        # Require minimum admin role
        if current_role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only admins and super admins can list API keys"
            )
        
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
        # Use the enhanced validation that includes super admin check
        is_valid, key_info, message, role = api_key_service.validate_api_key_with_role(request.api_key)
        
        if not is_valid:
            return APIKeyValidationResponse(
                valid=False,
                message=message
            )
        
        # For super admin, skip quota checks (unlimited access)
        if role and role.value == "superadmin":
            return APIKeyValidationResponse(
                valid=True,
                message="Super admin key valid - unlimited access",
                key_info=key_info,
                remaining_quota=9999,
                rate_limit_remaining=9999
            )
        
        # Check quota and rate limit for regular users
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
    request: Request,
    api_key_service: APIKeyService = Depends(get_api_key_service)
):
    """Revoke an API key (Super Admin only)"""
    try:
        # Get current user info
        current_user = get_current_user(request, api_key_service)
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_role, current_user_info = current_user
        
        # Only super admins can revoke keys
        if current_role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can revoke API keys"
            )
        
        success = api_key_service.revoke_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found or already revoked")
        
        print(f"🚫 API Key {key_id} revoked by {current_user_info.user_email}")
        return {"message": "API key revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
