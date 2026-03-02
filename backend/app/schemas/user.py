"""Authentication and user schemas."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class AdminLoginRequest(BaseModel):
    """Admin login request schema."""

    emp_id: str = Field(..., min_length=1, max_length=50, description="Employee ID")
    password: str = Field(..., min_length=6, max_length=100, description="Password")


class UserLoginRequest(BaseModel):
    """Regular user login request schema."""

    emp_id: str = Field(..., min_length=1, max_length=50, description="Employee ID")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")


class UserBase(BaseModel):
    """Base user schema."""

    emp_id: str = Field(..., max_length=50, description="Employee ID")
    is_admin: bool = Field(False, description="Admin flag")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=6, max_length=100, description="Password")
    name: Optional[str] = Field(None, max_length=100, description="User name")


class UserUpdate(BaseModel):
    """User update schema."""

    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Password")
    is_admin: Optional[bool] = Field(None, description="Admin flag")


class UserResponse(UserBase):
    """User response schema."""

    id: int = Field(..., description="User ID")

    class Config:
        from_attributes = True


# Prevent forward reference issues
TokenResponse.model_rebuild()
