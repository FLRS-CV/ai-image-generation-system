import hashlib
import secrets
import uuid
import os
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, Dict, List
from app.database.models import DatabaseManager
from app.models.api_key_models import APIKeyCreate, APIKeyUpdate, APIKeyResponse, UsageLogResponse, UserRole

class APIKeyService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_api_key(self, key_data: APIKeyCreate) -> Tuple[str, APIKeyResponse]:
        """Generate a new API key and store it in the database"""
        # Generate unique API key
        full_key = f"sk-proj-{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        key_prefix = full_key[:12] + "..."
        
        # Check if hash already exists (collision detection)
        if self._hash_exists(key_hash):
            raise Exception("Hash collision detected. Please try again.")
        
        # Insert into database
        query = '''
            INSERT INTO api_keys (
                key_hash, key_prefix, name, user_email, organization, role,
                daily_quota, rate_limit, created_at, last_quota_reset
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.now()
        params = (
            key_hash, key_prefix, key_data.name, key_data.user_email,
            key_data.organization, key_data.role.value, key_data.daily_quota, 
            key_data.rate_limit, now.isoformat(), now.date().isoformat()
        )
        
        key_id = self.db_manager.execute_insert(query, params)
        
        # Create response object
        response = APIKeyResponse(
            id=key_id,
            key_prefix=key_prefix,
            name=key_data.name,
            status="active",
            user_email=key_data.user_email,
            organization=key_data.organization,
            role=key_data.role.value,
            created_at=now.isoformat(),
            last_used=None,
            revoked_at=None,
            rate_limit=key_data.rate_limit,
            daily_quota=key_data.daily_quota,
            current_daily_usage=0,
            last_quota_reset=now.date().isoformat()
        )
        
        return full_key, response
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[APIKeyResponse], str]:
        """Validate an API key and return key info if valid"""
        if not api_key.startswith("sk-proj-"):
            return False, None, "Invalid API key format"
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Look up in database
        query = "SELECT * FROM api_keys WHERE key_hash = ? AND status = 'active'"
        results = self.db_manager.execute_query(query, (key_hash,))
        
        if not results:
            return False, None, "API key not found or inactive"
        
        # Convert result to APIKeyResponse
        row = results[0]
        key_info = self._row_to_api_key_response(row)
        
        return True, key_info, "API key valid"
    
    def revoke_api_key(self, key_id: int) -> bool:
        """Revoke an API key by setting status to revoked"""
        query = '''
            UPDATE api_keys 
            SET status = 'revoked', revoked_at = ? 
            WHERE id = ? AND status = 'active'
        '''
        
        affected_rows = self.db_manager.execute_update(
            query, (datetime.now().isoformat(), key_id)
        )
        
        return affected_rows > 0
    
    def update_api_key(self, key_id: int, update_data: APIKeyUpdate) -> Optional[APIKeyResponse]:
        """Update an API key's properties"""
        # Build dynamic update query
        update_fields = []
        params = []
        
        if update_data.name is not None:
            update_fields.append("name = ?")
            params.append(update_data.name)
        
        if update_data.daily_quota is not None:
            update_fields.append("daily_quota = ?")
            params.append(update_data.daily_quota)
        
        if update_data.rate_limit is not None:
            update_fields.append("rate_limit = ?")
            params.append(update_data.rate_limit)
        
        if update_data.organization is not None:
            update_fields.append("organization = ?")
            params.append(update_data.organization)
        
        if not update_fields:
            return None
        
        query = f"UPDATE api_keys SET {', '.join(update_fields)} WHERE id = ?"
        params.append(key_id)
        
        affected_rows = self.db_manager.execute_update(query, tuple(params))
        
        if affected_rows > 0:
            return self.get_api_key_by_id(key_id)
        
        return None
    
    def delete_api_key(self, key_id: int) -> bool:
        """Permanently delete an API key"""
        # First delete associated usage logs
        self.db_manager.execute_update(
            "DELETE FROM usage_logs WHERE api_key_id = ?", (key_id,)
        )
        
        # Then delete the API key
        affected_rows = self.db_manager.execute_update(
            "DELETE FROM api_keys WHERE id = ?", (key_id,)
        )
        
        return affected_rows > 0
    
    def get_api_key_by_id(self, key_id: int) -> Optional[APIKeyResponse]:
        """Get API key by ID"""
        query = "SELECT * FROM api_keys WHERE id = ?"
        results = self.db_manager.execute_query(query, (key_id,))
        
        if results:
            return self._row_to_api_key_response(results[0])
        
        return None
    
    def list_api_keys(self, user_email: Optional[str] = None, status: Optional[str] = None) -> List[APIKeyResponse]:
        """List all API keys with optional filtering"""
        query = "SELECT * FROM api_keys WHERE 1=1"
        params = []
        
        if user_email:
            query += " AND user_email = ?"
            params.append(user_email)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        results = self.db_manager.execute_query(query, tuple(params))
        return [self._row_to_api_key_response(row) for row in results]
    
    def log_usage(self, key_id: int, service_name: str, success: bool = True, 
                  response_time_ms: Optional[int] = None, error_message: Optional[str] = None):
        """Log API usage"""
        query = '''
            INSERT INTO usage_logs (
                api_key_id, service_name, success, response_time_ms, error_message
            ) VALUES (?, ?, ?, ?, ?)
        '''
        
        self.db_manager.execute_insert(query, (
            key_id, service_name, success, response_time_ms, error_message
        ))
        
        # Update last_used timestamp
        self.db_manager.execute_update(
            "UPDATE api_keys SET last_used = ? WHERE id = ?",
            (datetime.now().isoformat(), key_id)
        )
    
    def check_quota_and_rate_limit(self, key_id: int) -> Tuple[bool, str, Dict]:
        """Check if API key has quota and rate limit available"""
        # Get current key info
        key_info = self.get_api_key_by_id(key_id)
        if not key_info:
            return False, "API key not found", {}
        
        now = datetime.now()
        today = now.date()
        
        # Check if we need to reset daily quota
        if key_info.last_quota_reset != today.isoformat():
            self._reset_daily_quota(key_id, today)
            key_info.current_daily_usage = 0
        
        # Check daily quota
        if key_info.current_daily_usage >= key_info.daily_quota:
            return False, "Daily quota exceeded", {
                "daily_quota": key_info.daily_quota,
                "current_usage": key_info.current_daily_usage
            }
        
        # Check rate limit (simplified - in production, use Redis for this)
        if not self._check_rate_limit(key_id, key_info.rate_limit):
            return False, "Rate limit exceeded", {
                "rate_limit": key_info.rate_limit
            }
        
        return True, "Quota and rate limit OK", {
            "daily_quota": key_info.daily_quota,
            "current_usage": key_info.current_daily_usage,
            "rate_limit": key_info.rate_limit
        }
    
    def increment_usage(self, key_id: int):
        """Increment the daily usage counter"""
        query = "UPDATE api_keys SET current_daily_usage = current_daily_usage + 1 WHERE id = ?"
        self.db_manager.execute_update(query, (key_id,))
    
    def _hash_exists(self, key_hash: str) -> bool:
        """Check if a hash already exists in the database"""
        query = "SELECT COUNT(*) FROM api_keys WHERE key_hash = ?"
        results = self.db_manager.execute_query(query, (key_hash,))
        return results[0][0] > 0
    
    def _reset_daily_quota(self, key_id: int, new_date: date):
        """Reset the daily quota for a new day"""
        query = '''
            UPDATE api_keys 
            SET current_daily_usage = 0, last_quota_reset = ? 
            WHERE id = ?
        '''
        self.db_manager.execute_update(query, (new_date.isoformat(), key_id))
    
    def _check_rate_limit(self, key_id: int, rate_limit: int) -> bool:
        """Check rate limit for the last minute"""
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        
        query = '''
            SELECT COUNT(*) FROM usage_logs 
            WHERE api_key_id = ? AND request_timestamp > ?
        '''
        
        results = self.db_manager.execute_query(query, (key_id, one_minute_ago.isoformat()))
        current_rate = results[0][0]
        
        return current_rate < rate_limit
    
    def _row_to_api_key_response(self, row: tuple) -> APIKeyResponse:
        """Convert database row to APIKeyResponse object"""
        # Database schema:
        # 0:id, 1:key_hash, 2:key_prefix, 3:name, 4:status, 5:user_email, 6:organization,
        # 7:created_at, 8:last_used, 9:revoked_at, 10:rate_limit, 11:daily_quota, 
        # 12:current_daily_usage, 13:last_quota_reset, 14:role
        return APIKeyResponse(
            id=row[0],
            key_prefix=row[2],
            name=row[3],
            status=row[4],
            user_email=row[5],
            organization=row[6],
            role=row[14] if len(row) > 14 and row[14] else "user",  # role is at index 14
            created_at=row[7],
            last_used=row[8],
            revoked_at=row[9],
            rate_limit=row[10],
            daily_quota=row[11],
            current_daily_usage=row[12],
            last_quota_reset=row[13]
        )

    def validate_super_admin_key(self, api_key: str) -> bool:
        """Validate if the provided key is the super admin key"""
        super_admin_key = os.getenv("SUPER_ADMIN_API_KEY", "sk-proj-superadmin-default-key-change-me")
        return api_key == super_admin_key

    def validate_api_key_with_role(self, api_key: str) -> Tuple[bool, Optional[APIKeyResponse], str, Optional[UserRole]]:
        """Validate an API key and return key info with role if valid"""
        # First check if it's the super admin key
        if self.validate_super_admin_key(api_key):
            # Create a mock response for super admin
            super_admin_response = APIKeyResponse(
                id=-1,  # Special ID for super admin
                key_prefix="sk-proj-super...",
                name="Super Administrator",
                status="active",
                user_email="superadmin@system.local",
                organization="System",
                role=UserRole.SUPERADMIN.value,
                created_at=datetime.now().isoformat(),
                last_used=None,
                revoked_at=None,
                rate_limit=9999,
                daily_quota=9999,
                current_daily_usage=0,
                last_quota_reset=date.today().isoformat()
            )
            return True, super_admin_response, "Super admin key valid", UserRole.SUPERADMIN

        # Regular API key validation
        is_valid, key_info, message = self.validate_api_key(api_key)
        if not is_valid:
            return False, None, message, None

        # Convert role string to enum
        try:
            role = UserRole(key_info.role)
        except ValueError:
            role = UserRole.USER  # Default fallback

        return True, key_info, message, role

    def check_role_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user role has permission for the required role"""
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.ADMIN: 2,
            UserRole.SUPERADMIN: 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

    def can_create_role(self, creator_role: UserRole, target_role: UserRole) -> bool:
        """Check if a role can create another role"""
        if creator_role == UserRole.SUPERADMIN:
            return True  # Super admin can create any role
        elif creator_role == UserRole.ADMIN:
            return target_role == UserRole.USER  # Admin can only create users
        else:
            return False  # Users cannot create any roles
