# api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any
import sqlite3
import logging

from utils.auth_utils import verify_password, get_password_hash, create_access_token
from config.settings import settings
from api.models import UserRegister, Token, UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserRegister):
    """Register a new user."""
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        
        if len(user_in.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        # Normalise email: treat empty string same as None/NULL
        email_val = user_in.email if user_in.email and user_in.email.strip() else None

        # Check username uniqueness always; check email uniqueness only when a real email is provided
        cursor.execute("SELECT id FROM app_users WHERE username = ?", (user_in.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")

        if email_val:
            cursor.execute("SELECT id FROM app_users WHERE email = ?", (email_val,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")

        # Insert
        hashed_pw = get_password_hash(user_in.password)
        cursor.execute(
            "INSERT INTO app_users (username, hashed_password, role, email) VALUES (?, ?, ?, ?)",
            (user_in.username, hashed_pw, user_in.role, email_val)
        )
        conn.commit()

        return UserResponse(username=user_in.username, role=user_in.role, email=email_val)
    except sqlite3.Error as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")
    finally:
        conn.close()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login, retrieve a JWT."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM app_users WHERE username = ?", (form_data.username,))
        user = cursor.fetchone()
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
        return Token(access_token=access_token, token_type="bearer")
    except sqlite3.Error as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during login")
    finally:
        conn.close()

# --- Password Reset ---

from pydantic import BaseModel

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """
    Trigger password reset flow. 
    In PROD: Sends email.
    In LOCAL: Logs reset link.
    """
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM app_users WHERE email = ?", (req.email,))
        user = cursor.fetchone()
        
        if user:
            # Generate a temporary reset token (valid for 15 mins)
            # We reuse create_access_token but with specific purpose
            reset_token = create_access_token(
                data={"sub": user["username"], "purpose": "password_reset"}, 
                expires_delta=timedelta(minutes=15)
            )
            
            # MOCK EMAIL
            # MOCK EMAIL CONTENT
            reset_link = f"http://localhost:8504/?reset_token={reset_token}"
            email_body = f"""
            [MOCK EMAIL SERVICE]
            To: {req.email}
            Subject: Password Reset Request
            
            Hi {user['username']},
            
            You requested to reset your password.
            Click the link below to set a new password:
            {reset_link}
            
            (If you did not request this, please ignore this email.)
            """
            
            # Try to send real email
            from utils.email_utils import send_email
            
            email_sent = False
            # We strip the [MOCK...] header for the real email body
            real_body = email_body.replace("[MOCK EMAIL SERVICE]", "").strip()
            
            if send_email(req.email, "Password Reset Request", real_body):
                email_sent = True
            
            # Always log mock email for debugging/fallback
            logger.warning(email_body)
            print(email_body, flush=True) 
            
            if email_sent:
                return {"message": "Reset link sent to your email."}
            else:
                return {"message": "SMTP not configured. Link logged to console (Mock Mode)."}
            
        # User not found case (security: ambiguous)
        return {"message": "If that email exists, a reset link has been sent."}
    finally:
        conn.close()

@router.post("/reset-password")
async def reset_password_endpoint(req: ResetPasswordRequest):
    """Reset password using token."""
    from utils.auth_utils import decode_access_token
    
    # 1. Verify Token
    payload = decode_access_token(req.token)
    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    username = payload.get("sub")
    
    # 2. Update Password
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        new_hash = get_password_hash(req.new_password)
        cursor.execute("UPDATE app_users SET hashed_password = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        return {"message": "Password updated successfully. You can now login."}
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")
    finally:
        conn.close()
