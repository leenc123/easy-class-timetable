"""
教室管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.classroom import Classroom
from app.schemas.resource import ClassroomCreate, ClassroomUpdate, ClassroomResponse
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, get_org_id, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ClassroomResponse])
async def list_classrooms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教室列表"""
    query = db.query(Classroom)

    # 权限过滤
    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(Classroom.org_id == org_id)
    else:
        query = query.filter(Classroom.org_id == current_user.org_id)

    if is_active is not None:
        query = query.filter(Classroom.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[ClassroomResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[ClassroomResponse])
async def create_classroom(
    request: ClassroomCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """创建教室"""
    # 获取机构ID
    if current_user.role == UserRole.SUPER_ADMIN:
        if not request.org_id:
            raise HTTPException(status_code=400, detail="需要指定机构ID")
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    classroom = Classroom(
        org_id=org_id,
        **request.model_dump()
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return ResponseBase(
        data=ClassroomResponse.model_validate(classroom),
        message="教室创建成功"
    )


@router.get("/{classroom_id}", response_model=ResponseBase[ClassroomResponse])
async def get_classroom(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教室详情"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="教室不存在")

    if not check_org_access(current_user, classroom.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    return ResponseBase(data=ClassroomResponse.model_validate(classroom))


@router.put("/{classroom_id}", response_model=ResponseBase[ClassroomResponse])
async def update_classroom(
    classroom_id: int,
    request: ClassroomUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新教室"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="教室不存在")

    if not check_org_access(current_user, classroom.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(classroom, key, value)

    db.commit()
    db.refresh(classroom)

    return ResponseBase(
        data=ClassroomResponse.model_validate(classroom),
        message="教室更新成功"
    )


@router.delete("/{classroom_id}", response_model=ResponseBase)
async def delete_classroom(
    classroom_id: int,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """删除/禁用教室"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="教室不存在")

    if not check_org_access(current_user, classroom.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    classroom.is_active = False
    db.commit()

    return ResponseBase(message="教室已禁用")