"""
教师管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.teacher import Teacher, TeacherAvailability
from app.schemas.resource import TeacherCreate, TeacherUpdate, TeacherResponse, AvailabilityCreate, AvailabilityResponse
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, get_password_hash, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TeacherResponse])
async def list_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    subject: Optional[str] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教师列表"""
    query = db.query(Teacher)

    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(Teacher.org_id == org_id)
    else:
        query = query.filter(Teacher.org_id == current_user.org_id)

    if is_active is not None:
        query = query.filter(Teacher.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[TeacherResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[TeacherResponse])
async def create_teacher(
    request: TeacherCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建教师"""
    # 确定机构ID
    if current_user.role == UserRole.SUPER_ADMIN:
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    if not org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    # 如果需要同时创建用户账号
    user_id = None
    if request.create_user_account:
        username = f"teacher_{request.phone or request.name}"
        user = User(
            org_id=org_id,
            username=username,
            password_hash=get_password_hash("123456"),  # 默认密码
            real_name=request.name,
            phone=request.phone,
            email=request.email,
            role=UserRole.TEACHER
        )
        db.add(user)
        db.flush()
        user_id = user.id

    teacher = Teacher(
        org_id=org_id,
        user_id=user_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        subjects=request.subjects,
        max_hours_per_week=request.max_hours_per_week,
        bio=request.bio
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return ResponseBase(
        data=TeacherResponse.model_validate(teacher),
        message="教师创建成功"
    )


@router.get("/{teacher_id}", response_model=ResponseBase[TeacherResponse])
async def get_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教师详情"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    if not check_org_access(current_user, teacher.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    return ResponseBase(data=TeacherResponse.model_validate(teacher))


@router.put("/{teacher_id}", response_model=ResponseBase[TeacherResponse])
async def update_teacher(
    teacher_id: int,
    request: TeacherUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新教师"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    if not check_org_access(current_user, teacher.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)

    return ResponseBase(
        data=TeacherResponse.model_validate(teacher),
        message="教师更新成功"
    )


# ============ 教师可用时间 ============
@router.get("/{teacher_id}/availability", response_model=ResponseBase[List[AvailabilityResponse]])
async def get_teacher_availability(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教师可用时间"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    if not check_org_access(current_user, teacher.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    availabilities = db.query(TeacherAvailability).filter(
        TeacherAvailability.teacher_id == teacher_id
    ).all()

    return ResponseBase(data=[AvailabilityResponse.model_validate(a) for a in availabilities])


@router.put("/{teacher_id}/availability", response_model=ResponseBase)
async def set_teacher_availability(
    teacher_id: int,
    request: List[AvailabilityCreate],
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """设置教师可用时间"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    # 权限：教师只能修改自己的，管理员可以修改机构的
    if current_user.role == UserRole.TEACHER:
        if teacher.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能修改自己的可用时间")
    else:
        if not check_org_access(current_user, teacher.org_id):
            raise HTTPException(status_code=403, detail="无权访问")

    # 清除旧数据
    db.query(TeacherAvailability).filter(
        TeacherAvailability.teacher_id == teacher_id
    ).delete()

    # 添加新数据
    for avail in request:
        availability = TeacherAvailability(
            teacher_id=teacher_id,
            **avail.model_dump()
        )
        db.add(availability)

    db.commit()

    return ResponseBase(message="可用时间设置成功")