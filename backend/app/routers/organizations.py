"""
机构管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrganizationResponse])
async def list_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """获取机构列表"""
    query = db.query(Organization)

    # 权限过滤：机构管理员只能看自己机构
    if current_user.role == UserRole.ORG_ADMIN:
        query = query.filter(Organization.id == current_user.org_id)

    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[OrganizationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[OrganizationResponse])
async def create_organization(
    request: OrganizationCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建机构（仅超管）"""
    # 检查编码是否存在
    existing = db.query(Organization).filter(Organization.code == request.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="机构编码已存在"
        )

    org = Organization(**request.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)

    return ResponseBase(
        data=OrganizationResponse.model_validate(org),
        message="机构创建成功"
    )


@router.get("/{org_id}", response_model=ResponseBase[OrganizationResponse])
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机构详情"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机构不存在"
        )

    # 权限检查
    if not check_org_access(current_user, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机构"
        )

    return ResponseBase(data=OrganizationResponse.model_validate(org))


@router.put("/{org_id}", response_model=ResponseBase[OrganizationResponse])
async def update_organization(
    org_id: int,
    request: OrganizationUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新机构"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机构不存在"
        )

    # 权限检查
    if current_user.role == UserRole.ORG_ADMIN and org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能管理本机构"
        )

    # 更新字段
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(org, key, value)

    db.commit()
    db.refresh(org)

    return ResponseBase(
        data=OrganizationResponse.model_validate(org),
        message="机构更新成功"
    )