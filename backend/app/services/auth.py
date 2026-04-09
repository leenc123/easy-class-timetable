"""
认证服务
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserInfo, LoginRequest, LoginResponse


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": user.username,
        "user_id": user.id,
        "role": user.role.value,
        "org_id": user.org_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用"
        )

    return user


def require_role(allowed_roles: list[UserRole]):
    """角色权限检查"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker


def get_org_id(current_user: User = Depends(get_current_user)) -> int:
    """获取当前用户的机构ID"""
    if current_user.role == UserRole.SUPER_ADMIN:
        # 超管可以选择任意机构，默认返回空
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="超管需要指定机构ID"
        )
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联机构"
        )
    return current_user.org_id


def check_org_access(current_user: User, org_id: int) -> bool:
    """检查用户是否有权限访问指定机构"""
    if current_user.role == UserRole.SUPER_ADMIN:
        return True
    return current_user.org_id == org_id


def login(db: Session, request: LoginRequest) -> LoginResponse:
    """用户登录"""
    user = db.query(User).filter(User.username == request.username).first()

    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已禁用"
        )

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()

    # 生成 token
    access_token = create_access_token(user)

    # 构建用户信息
    org_name = None
    if user.organization:
        org_name = user.organization.name

    user_info = UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        role=user.role,
        org_id=user.org_id,
        org_name=org_name,
        avatar_url=user.avatar_url
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_HOURS * 3600,
        user_info=user_info
    )