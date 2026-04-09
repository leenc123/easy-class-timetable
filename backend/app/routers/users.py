"""
用户管理路由（额外的管理功能）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserInfo
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserInfo])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)

    # 权限过滤
    if current_user.role == UserRole.ORG_ADMIN:
        query = query.filter(User.org_id == current_user.org_id)
    elif org_id:
        query = query.filter(User.org_id == org_id)

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[
            UserInfo(
                id=u.id,
                username=u.username,
                real_name=u.real_name,
                role=u.role,
                org_id=u.org_id,
                org_name=u.organization.name if u.organization else None,
                avatar_url=u.avatar_url
            ) for u in items
        ],
        total=total,
        page=page,
        page_size=page_size
    )