"""
课程管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course, CourseTeacher, CourseStudent, CourseStatus
from app.models.teacher import Teacher
from app.models.student import Student
from app.schemas.resource import CourseCreate, CourseUpdate, CourseResponse, CourseTeacherAssign, CourseStudentAssign
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CourseResponse])
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    subject: Optional[str] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课程列表"""
    query = db.query(Course)

    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(Course.org_id == org_id)
    else:
        query = query.filter(Course.org_id == current_user.org_id)

    if status:
        query = query.filter(Course.status == status)
    if subject:
        query = query.filter(Course.subject == subject)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    # 添加教师和学生ID
    results = []
    for item in items:
        course_data = CourseResponse.model_validate(item)
        course_data.teachers = [ct.teacher_id for ct in item.course_teachers]
        course_data.students = [cs.student_id for cs in item.course_students]
        results.append(course_data)

    return PaginatedResponse(
        data=results,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[CourseResponse])
async def create_course(
    request: CourseCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建课程"""
    # 确定机构ID
    if current_user.role == UserRole.SUPER_ADMIN:
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    if not org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    course = Course(
        org_id=org_id,
        name=request.name,
        code=request.code,
        subject=request.subject,
        duration_minutes=request.duration_minutes,
        min_students=request.min_students,
        max_students=request.max_students,
        required_equipment=request.required_equipment,
        description=request.description
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    course_data = CourseResponse.model_validate(course)
    course_data.teachers = []
    course_data.students = []

    return ResponseBase(
        data=course_data,
        message="课程创建成功"
    )


@router.get("/{course_id}", response_model=ResponseBase[CourseResponse])
async def get_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课程详情"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, course.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    course_data = CourseResponse.model_validate(course)
    course_data.teachers = [ct.teacher_id for ct in course.course_teachers]
    course_data.students = [cs.student_id for cs in course.course_students]

    return ResponseBase(data=course_data)


@router.put("/{course_id}", response_model=ResponseBase[CourseResponse])
async def update_course(
    course_id: int,
    request: CourseUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新课程"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, course.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)

    course_data = CourseResponse.model_validate(course)
    course_data.teachers = [ct.teacher_id for ct in course.course_teachers]
    course_data.students = [cs.student_id for cs in course.course_students]

    return ResponseBase(
        data=course_data,
        message="课程更新成功"
    )


@router.post("/{course_id}/teachers", response_model=ResponseBase)
async def assign_teachers(
    course_id: int,
    request: CourseTeacherAssign,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """为课程分配教师"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, course.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 清除旧关联
    db.query(CourseTeacher).filter(CourseTeacher.course_id == course_id).delete()

    # 添加新关联
    for teacher_id in request.teacher_ids:
        ct = CourseTeacher(
            course_id=course_id,
            teacher_id=teacher_id,
            is_primary=(teacher_id == request.primary_teacher_id)
        )
        db.add(ct)

    db.commit()

    return ResponseBase(message="教师分配成功")


@router.post("/{course_id}/students", response_model=ResponseBase)
async def assign_students(
    course_id: int,
    request: CourseStudentAssign,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """为学生选课"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, course.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 检查学生是否属于同一机构
    students = db.query(Student).filter(Student.id.in_(request.student_ids)).all()
    for student in students:
        if student.org_id != course.org_id:
            raise HTTPException(status_code=400, detail=f"学生 {student.name} 不属于本机构")

    # 添加关联（保留已有的，添加新的）
    existing_ids = {cs.student_id for cs in course.course_students}
    for student_id in request.student_ids:
        if student_id not in existing_ids:
            cs = CourseStudent(
                course_id=course_id,
                student_id=student_id
            )
            db.add(cs)

    db.commit()

    return ResponseBase(message="学生选课成功")