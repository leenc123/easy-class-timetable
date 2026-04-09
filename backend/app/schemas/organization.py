"""
机构相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=50)
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True