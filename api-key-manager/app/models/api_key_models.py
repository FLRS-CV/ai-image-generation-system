from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

class APIKeyCreate(BaseModel):
    name: str = Field(..., description="Human-readable name for the API key")
    user_email: str = Field(..., description="Email of the key owner")
    organization: Optional[str] = Field(None, description="Organization name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    daily_quota: int = Field(default=100, description="Daily request limit")
    rate_limit: int = Field(default=60, description="Requests per minute")

class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="New name for the API key")
    daily_quota: Optional[int] = Field(None, description="New daily request limit")
    rate_limit: Optional[int] = Field(None, description="New rate limit")
    organization: Optional[str] = Field(None, description="New organization name")

class APIKeyResponse(BaseModel):
    id: int
    key_prefix: str
    name: str
    status: str
    user_email: str
    organization: Optional[str]
    role: str
    created_at: str
    last_used: Optional[str]
    revoked_at: Optional[str]
    rate_limit: int
    daily_quota: int
    current_daily_usage: int
    last_quota_reset: str
    is_active: Optional[bool] = None
    usage_count: Optional[int] = None  # Frontend compatibility field
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set is_active based on status for frontend compatibility
        if self.is_active is None:
            self.is_active = self.status == "active"
        # Set usage_count based on current_daily_usage for frontend compatibility
        if self.usage_count is None:
            self.usage_count = self.current_daily_usage

class APIKeyListResponse(BaseModel):
    api_keys: List[APIKeyResponse]
    total_count: int

class APIKeyValidationRequest(BaseModel):
    api_key: str = Field(..., description="API key to validate")

class APIKeyValidationResponse(BaseModel):
    valid: bool
    message: str
    key_info: Optional[APIKeyResponse] = None
    remaining_quota: Optional[int] = None
    rate_limit_remaining: Optional[int] = None

class UsageLogResponse(BaseModel):
    id: int
    api_key_id: int
    service_name: str
    request_timestamp: str
    response_time_ms: Optional[int]
    success: bool
    error_message: Optional[str]

class APIKeyUsageResponse(BaseModel):
    api_key: APIKeyResponse
    usage_logs: List[UsageLogResponse]
    total_usage: int
    success_rate: float
