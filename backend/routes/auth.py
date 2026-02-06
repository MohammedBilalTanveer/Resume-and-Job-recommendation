from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import httpx
import os

from backend.database import get_users_collection
from backend.models.user import UserInDB, user_from_doc
from backend.utils.auth import (
    create_access_token, create_refresh_token, decode_token,
    get_password_hash, authenticate_user, get_user_by_email,
    get_user_by_oauth, create_user, get_current_user, get_user_by_id,
    update_user_last_login, verify_password
)

router = APIRouter()

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


# Request/Response Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    oauth_provider: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


# Auth Endpoints
@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """Register a new user with email and password."""
    # Check if user exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Create user
    user = await create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    # Generate tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider,
            "is_verified": user.is_verified
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login with email and password."""
    user = await authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    await update_user_last_login(user.id)
    
    # Generate tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider,
            "is_verified": user.is_verified
        }
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(token_data: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    payload = decode_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    user = await get_user_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider,
            "is_verified": user.is_verified
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        oauth_provider=current_user.oauth_provider,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )


@router.put("/me")
async def update_profile(
    full_name: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update user profile."""
    users = get_users_collection()
    update_data = {"updated_at": datetime.utcnow()}
    
    if full_name is not None:
        update_data["full_name"] = full_name
    
    await users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": full_name if full_name is not None else current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "oauth_provider": current_user.oauth_provider,
        "is_verified": current_user.is_verified
    }


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Change user password."""
    if current_user.oauth_provider and not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth accounts"
        )
    
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    users = get_users_collection()
    await users.update_one(
        {"id": current_user.id},
        {"$set": {
            "hashed_password": get_password_hash(password_data.new_password),
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Password changed successfully"}


# OAuth Endpoints
@router.get("/google")
async def google_login():
    """Redirect to Google OAuth."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    redirect_uri = f"{FRONTEND_URL}/auth/callback/google"
    scope = "openid email profile"
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline"
    )
    
    return {"auth_url": google_auth_url}


@router.post("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    redirect_uri = f"{FRONTEND_URL}/auth/callback/google"
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        token_data = token_response.json()
        google_access_token = token_data.get("access_token")
        
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info"
            )
        
        user_info = user_response.json()
    
    google_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")
    
    # Check if user exists by OAuth ID
    user = await get_user_by_oauth("google", google_id)
    users = get_users_collection()
    
    if not user:
        # Check if email exists
        existing_user = await get_user_by_email(email)
        if existing_user:
            # Link Google account to existing user
            await users.update_one(
                {"id": existing_user.id},
                {"$set": {
                    "oauth_provider": "google",
                    "oauth_id": google_id,
                    "avatar_url": existing_user.avatar_url or picture,
                    "is_verified": True,
                    "updated_at": datetime.utcnow()
                }}
            )
            user = await get_user_by_id(existing_user.id)
        else:
            # Create new user
            user = await create_user(
                email=email,
                full_name=name,
                oauth_provider="google",
                oauth_id=google_id,
                avatar_url=picture
            )
    
    # Update last login
    await update_user_last_login(user.id)
    
    # Generate tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider,
            "is_verified": user.is_verified
        }
    }


@router.get("/github")
async def github_login():
    """Redirect to GitHub OAuth."""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    redirect_uri = f"{FRONTEND_URL}/auth/callback/github"
    scope = "user:email"
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}"
    )
    
    return {"auth_url": github_auth_url}


@router.post("/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback."""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        token_data = token_response.json()
        github_access_token = token_data.get("access_token")
        
        if not github_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        
        # Get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info"
            )
        
        user_info = user_response.json()
        
        # Get user email (might need separate request)
        email = user_info.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {github_access_token}"}
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next(
                    (e for e in emails if e.get("primary") and e.get("verified")),
                    None
                )
                if primary_email:
                    email = primary_email.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get email from GitHub"
        )
    
    github_id = str(user_info.get("id"))
    name = user_info.get("name") or user_info.get("login")
    avatar = user_info.get("avatar_url")
    
    # Check if user exists by OAuth ID
    user = await get_user_by_oauth("github", github_id)
    users = get_users_collection()
    
    if not user:
        # Check if email exists
        existing_user = await get_user_by_email(email)
        if existing_user:
            # Link GitHub account to existing user
            await users.update_one(
                {"id": existing_user.id},
                {"$set": {
                    "oauth_provider": "github",
                    "oauth_id": github_id,
                    "avatar_url": existing_user.avatar_url or avatar,
                    "is_verified": True,
                    "updated_at": datetime.utcnow()
                }}
            )
            user = await get_user_by_id(existing_user.id)
        else:
            # Create new user
            user = await create_user(
                email=email,
                full_name=name,
                oauth_provider="github",
                oauth_id=github_id,
                avatar_url=avatar
            )
    
    # Update last login
    await update_user_last_login(user.id)
    
    # Generate tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider,
            "is_verified": user.is_verified
        }
    }

