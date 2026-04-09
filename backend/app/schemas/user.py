"""
认证相关 Schema
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: str
    role: UserRole
    org_id: Optional[int]
    org_name: Optional[str]
    avatar_url: Optional[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UserInfo


class UserCreate(BaseModel):
    org_id: Optional[int] = None
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    real_name: str = Field(..., max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    role: UserRole = UserRole.TEACHER


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)