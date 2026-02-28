# api/dependencies.py

import sqlite3
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt

from utils.auth_utils import decode_access_token
from config.settings import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> Dict[str, Any]:
    """Dependency to validate JWT or API Key and return the current user's data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Try API Key first (Technical Access)
    if api_key:
        conn = sqlite3.connect(settings.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM api_keys WHERE key = ?", (api_key,))
            key_data = cursor.fetchone()
            if key_data:
                # Return a virtual user representing the technical access
                return {"id": f"key_{key_data['id']}", "username": key_data['name'], "role": "admin"}
        except sqlite3.Error as e:
            logger.error(f"Database error in API Key validation: {e}")
        finally:
            conn.close()

    # 2. Try JWT Token (User Access)
    if token:
        payload = decode_access_token(token)
        if payload:
            username: str = payload.get("sub")
            if username:
                conn = sqlite3.connect(settings.db_path)
                conn.row_factory = sqlite3.Row
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, username, role FROM app_users WHERE username = ?", (username,))
                    user = cursor.fetchone()
                    if user:
                        return dict(user)
                except sqlite3.Error as e:
                    logger.error(f"Database error in get_current_user: {e}")
                finally:
                    conn.close()

    raise credentials_exception

async def requires_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependency to ensure the current user is an admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. Admin role required."
        )
    return current_user
