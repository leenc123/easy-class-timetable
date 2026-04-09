"""
学生管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.resource import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[StudentResponse])
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    grade: Optional[str] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学生列表"""
    query = db.query(Student)

    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(Student.org_id == org_id)
    else:
        query = query.filter(Student.org_id == current_user.org_id)

    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    if grade:
        query = query.filter(Student.grade == grade)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[StudentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[StudentResponse])
async def create_student(
    request: StudentCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建学生"""
    # 确定机构ID：超管可指定，其他角色使用自己的机构
    if current_user.role == UserRole.SUPER_ADMIN:
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    if not org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    student = Student(
        org_id=org_id,
        name=request.name,
        grade=request.grade,
        phone=request.phone,
        parent_name=request.parent_name,
        parent_phone=request.parent_phone,
        notes=request.notes
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return ResponseBase(
        data=StudentResponse.model_validate(student),
        message="学生创建成功"
    )


@router.get("/{student_id}", response_model=ResponseBase[StudentResponse])
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学生详情"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    return ResponseBase(data=StudentResponse.model_validate(student))


@router.put("/{student_id}", response_model=ResponseBase[StudentResponse])
async def update_student(
    student_id: int,
    request: StudentUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新学生"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return ResponseBase(
        data=StudentResponse.model_validate(student),
        message="学生更新成功"
    )


@router.delete("/{student_id}", response_model=ResponseBase)
async def delete_student(
    student_id: int,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """删除/禁用学生"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    student.is_active = False
    db.commit()

    return ResponseBase(message="学生已禁用")