"""
学生管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.student_subject_hours import StudentSubjectHours
from app.schemas.resource import StudentCreate, StudentUpdate, StudentResponse, StudentSubjectHoursCreate, StudentSubjectHoursUpdate, StudentSubjectHoursResponse, StudentResponseWithHours
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


# ============ 学科学时管理 ============
@router.get("/{student_id}/subject-hours", response_model=ResponseBase[list[StudentSubjectHoursResponse]])
async def list_student_subject_hours(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学生的学科学时列表"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    hours = db.query(StudentSubjectHours).filter(StudentSubjectHours.student_id == student_id).all()
    return ResponseBase(data=[StudentSubjectHoursResponse.model_validate(h) for h in hours])


@router.post("/{student_id}/subject-hours", response_model=ResponseBase[StudentSubjectHoursResponse])
async def create_student_subject_hours(
    student_id: int,
    request: StudentSubjectHoursCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """为学生添加学科学时"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 检查是否已存在该学科的学时配置
    existing = db.query(StudentSubjectHours).filter(
        StudentSubjectHours.student_id == student_id,
        StudentSubjectHours.subject == request.subject
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学科已存在学时配置")

    subject_hours = StudentSubjectHours(
        student_id=student_id,
        subject=request.subject,
        total_hours=request.total_hours,
        remaining_hours=request.total_hours  # 初始剩余学时等于总学时
    )
    db.add(subject_hours)
    db.commit()
    db.refresh(subject_hours)

    return ResponseBase(data=StudentSubjectHoursResponse.model_validate(subject_hours), message="学时配置创建成功")


@router.put("/{student_id}/subject-hours/{hours_id}", response_model=ResponseBase[StudentSubjectHoursResponse])
async def update_student_subject_hours(
    student_id: int,
    hours_id: int,
    request: StudentSubjectHoursUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新学生的学科学时"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    subject_hours = db.query(StudentSubjectHours).filter(
        StudentSubjectHours.id == hours_id,
        StudentSubjectHours.student_id == student_id
    ).first()
    if not subject_hours:
        raise HTTPException(status_code=404, detail="学时配置不存在")

    # 更新总学时时，同时调整剩余学时
    if request.total_hours is not None:
        # 计算已使用的学时
        used_hours = subject_hours.total_hours - subject_hours.remaining_hours
        # 新的剩余学时 = 新总学时 - 已使用学时
        new_remaining = request.total_hours - used_hours
        if new_remaining < 0:
            raise HTTPException(status_code=400, detail="总学时不能小于已使用的学时")
        subject_hours.total_hours = request.total_hours
        subject_hours.remaining_hours = new_remaining

    if request.remaining_hours is not None:
        if request.remaining_hours > subject_hours.total_hours:
            raise HTTPException(status_code=400, detail="剩余学时不能大于总学时")
        subject_hours.remaining_hours = request.remaining_hours

    db.commit()
    db.refresh(subject_hours)

    return ResponseBase(data=StudentSubjectHoursResponse.model_validate(subject_hours), message="学时配置更新成功")


@router.delete("/{student_id}/subject-hours/{hours_id}", response_model=ResponseBase)
async def delete_student_subject_hours(
    student_id: int,
    hours_id: int,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """删除学生的学科学时配置"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not check_org_access(current_user, student.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    subject_hours = db.query(StudentSubjectHours).filter(
        StudentSubjectHours.id == hours_id,
        StudentSubjectHours.student_id == student_id
    ).first()
    if not subject_hours:
        raise HTTPException(status_code=404, detail="学时配置不存在")

    db.delete(subject_hours)
    db.commit()

    return ResponseBase(message="学时配置删除成功")