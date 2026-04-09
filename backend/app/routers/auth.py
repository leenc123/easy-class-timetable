"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, UserUpdate, UserInfo, PasswordChange
from app.schemas.base import ResponseBase
from app.services.auth import (
    login, get_current_user, get_password_hash, verify_password,
    require_role, check_org_access
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def user_login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    return login(db, request)


@router.get("/me", response_model=ResponseBase[UserInfo])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    org_name = current_user.organization.name if current_user.organization else None
    return ResponseBase(
        data=UserInfo(
            id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            role=current_user.role,
            org_id=current_user.org_id,
            org_name=org_name,
            avatar_url=current_user.avatar_url
        )
    )


@router.post("/change-password", response_model=ResponseBase)
async def change_password(
    request: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()

    return ResponseBase(message="密码修改成功")


@router.post("/users", response_model=ResponseBase[UserInfo])
async def create_user(
    request: UserCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建用户"""
    # 权限检查
    if current_user.role == UserRole.ORG_ADMIN:
        # 机构管理员只能在自己机构内创建用户
        if request.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能在本机构内创建用户"
            )

    # 检查用户名是否存在
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    user = User(
        org_id=request.org_id,
        username=request.username,
        password_hash=get_password_hash(request.password),
        real_name=request.real_name,
        phone=request.phone,
        email=request.email,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    org_name = user.organization.name if user.organization else None
    return ResponseBase(
        data=UserInfo(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            org_id=user.org_id,
            org_name=org_name,
            avatar_url=user.avatar_url
        ),
        message="用户创建成功"
    )


@router.put("/users/{user_id}", response_model=ResponseBase[UserInfo])
async def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 权限检查
    if current_user.role == UserRole.ORG_ADMIN:
        if user.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能管理本机构用户"
            )

    # 更新字段
    if request.real_name is not None:
        user.real_name = request.real_name
    if request.phone is not None:
        user.phone = request.phone
    if request.email is not None:
        user.email = request.email
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    if request.is_active is not None:
        user.is_active = request.is_active

    db.commit()
    db.refresh(user)

    org_name = user.organization.name if user.organization else None
    return ResponseBase(
        data=UserInfo(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            org_id=user.org_id,
            org_name=org_name,
            avatar_url=user.avatar_url
        ),
        message="用户更新成功"
    )


@router.delete("/users/{user_id}", response_model=ResponseBase)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """删除/禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 权限检查
    if current_user.role == UserRole.ORG_ADMIN:
        if user.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能管理本机构用户"
            )

    # 禁用而非删除
    user.is_active = False
    db.commit()

    return ResponseBase(message="用户已禁用")