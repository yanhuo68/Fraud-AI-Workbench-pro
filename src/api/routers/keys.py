# api/routers/keys.py

import secrets
import sqlite3
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.dependencies import requires_admin
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: str

@router.post("/generate", response_model=APIKeyResponse)
async def generate_key(key_in: APIKeyCreate, admin=Depends(requires_admin)):
    """Generate a new technical API key."""
    # Generate a secure random key
    new_key = f"fl_{secrets.token_urlsafe(32)}"
    
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO api_keys (name, key) VALUES (?, ?)",
            (key_in.name, new_key)
        )
        key_id = cursor.lastrowid
        conn.commit()
        
        # Get created_at
        cursor.execute("SELECT created_at FROM api_keys WHERE id = ?", (key_id,))
        created_at = cursor.fetchone()[0]
        
        return APIKeyResponse(
            id=key_id,
            name=key_in.name,
            key=new_key,
            created_at=str(created_at)
        )
    except sqlite3.Error as e:
        logger.error(f"Failed to generate API Key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        conn.close()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_keys(admin=Depends(requires_admin)):
    """List all active API keys (keys themselves are partially masked)."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, key, created_at FROM api_keys")
        keys = cursor.fetchall()
        
        result = []
        for k in keys:
            kd = dict(k)
            # Mask the key for security in listing
            raw_key = kd["key"]
            kd["key"] = f"{raw_key[:6]}...{raw_key[-4:]}"
            result.append(kd)
        return result
    except sqlite3.Error as e:
        logger.error(f"Failed to list API Keys: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        conn.close()

@router.delete("/{key_id}")
async def revoke_key(key_id: int, admin=Depends(requires_admin)):
    """Delete/Revoke an API key."""
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        conn.commit()
        return {"message": "Key revoked successfully"}
    except sqlite3.Error as e:
        logger.error(f"Failed to revoke API Key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        conn.close()
