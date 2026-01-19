from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    """Request model for creating a new user."""
    username: str
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
