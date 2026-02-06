from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database import get_users_collection, get_next_sequence
from backend.models.user import UserInDB, user_from_doc
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-min-32-chars!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    users = get_users_collection()
    doc = await users.find_one({"email": email})
    return user_from_doc(doc)


async def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """Get a user by ID."""
    users = get_users_collection()
    doc = await users.find_one({"id": user_id})
    return user_from_doc(doc)


async def get_user_by_oauth(provider: str, oauth_id: str) -> Optional[UserInDB]:
    """Get a user by OAuth provider and ID."""
    users = get_users_collection()
    doc = await users.find_one({
        "oauth_provider": provider,
        "oauth_id": oauth_id
    })
    return user_from_doc(doc)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserInDB:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Convert string sub to int (JWT spec requires sub to be string)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Optional[UserInDB]:
    """Get the current user if authenticated, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if payload is None:
            return None
        
        # Convert string sub to int (JWT spec requires sub to be string)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None
        
        user = await get_user_by_id(user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception:
        return None


async def create_user(
    email: str, 
    password: Optional[str] = None, 
    full_name: Optional[str] = None, 
    oauth_provider: Optional[str] = None,
    oauth_id: Optional[str] = None, 
    avatar_url: Optional[str] = None
) -> UserInDB:
    """Create a new user."""
    hashed_password = get_password_hash(password) if password else None
    
    # Get next user ID
    user_id = await get_next_sequence("users")
    now = datetime.utcnow()
    
    user_doc = {
        "id": user_id,
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "oauth_provider": oauth_provider,
        "oauth_id": oauth_id,
        "avatar_url": avatar_url,
        "is_active": True,
        "is_verified": True if oauth_provider else False,
        "created_at": now,
        "updated_at": now,
        "last_login": None
    }
    
    users = get_users_collection()
    await users.insert_one(user_doc)
    
    return user_from_doc(user_doc)


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not user.hashed_password:
        return None  # OAuth user trying to login with password
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user_last_login(user_id: int):
    """Update user's last login timestamp."""
    users = get_users_collection()
    await users.update_one(
        {"id": user_id},
        {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
    )

