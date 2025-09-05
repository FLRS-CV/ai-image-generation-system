"""
Authentication middleware for role-based access control
"""
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from typing import Optional, Tuple
from app.services.api_key_service import APIKeyService
from app.database.models import DatabaseManager
from app.models.api_key_models import UserRole
import secrets

security = HTTPBasic()
bearer_security = HTTPBearer(auto_error=False)

# Simple hardcoded credentials (for backward compatibility)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def get_db_manager():
    return DatabaseManager()

def get_api_key_service(db_manager: DatabaseManager = Depends(get_db_manager)):
    return APIKeyService(db_manager)

def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify admin credentials for accessing admin panel (backward compatibility)
    """
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

def extract_api_key(request: Request) -> Optional[str]:
    """Extract API key from request headers"""
    # Try X-API-Key header first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key
    
    # Try Authorization header with Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    return None

def verify_api_key_role(
    required_role: UserRole,
    request: Request,
    api_key_service: APIKeyService = Depends(get_api_key_service)
) -> Tuple[UserRole, dict]:
    """
    Verify API key and check if user has required role
    Returns (user_role, user_info)
    """
    api_key = extract_api_key(request)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate API key and get role
    is_valid, user_info, message, user_role = api_key_service.validate_api_key_with_role(api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key: {message}",
        )
    
    # Check role permission
    if not api_key_service.check_role_permission(user_role, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {required_role.value}, Current: {user_role.value}",
        )
    
    return user_role, user_info

def require_user_role(request: Request, api_key_service: APIKeyService = Depends(get_api_key_service)):
    """Require USER role or higher"""
    return verify_api_key_role(UserRole.USER, request, api_key_service)

def require_admin_role(request: Request, api_key_service: APIKeyService = Depends(get_api_key_service)):
    """Require ADMIN role or higher"""
    return verify_api_key_role(UserRole.ADMIN, request, api_key_service)

def require_superadmin_role(request: Request, api_key_service: APIKeyService = Depends(get_api_key_service)):
    """Require SUPERADMIN role"""
    return verify_api_key_role(UserRole.SUPERADMIN, request, api_key_service)

def get_current_user(
    request: Request,
    api_key_service: APIKeyService = Depends(get_api_key_service)
) -> Optional[Tuple[UserRole, dict]]:
    """
    Get current user info without requiring specific role (optional authentication)
    Returns None if no valid API key provided
    """
    api_key = extract_api_key(request)
    
    if not api_key:
        return None
    
    # Validate API key and get role
    is_valid, user_info, message, user_role = api_key_service.validate_api_key_with_role(api_key)
    
    if not is_valid:
        return None
    
    return user_role, user_info
