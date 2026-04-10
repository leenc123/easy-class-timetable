"""
课表调度路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import ClassSession, SessionStatus, SessionCheckin, SessionStudent
from app.models.cycle import TimeSlot
from app.models.conflict import SchedulingConflict, ConflictType
from app.schemas.schedule import (
    SessionCreate, SessionUpdate, SessionResponse,
    BatchSessionCreate, ConflictCheckRequest, ConflictInfo, ConflictResponse,
    CheckinResponse
)
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access
from app.services.conflict import check_session_conflicts

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SessionResponse])
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    teacher_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
    course_id: Optional[int] = None,
    cycle_id: Optional[int] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课表列表"""
    query = db.query(ClassSession)

    # 权限过滤
    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(ClassSession.org_id == org_id)
    else:
        query = query.filter(ClassSession.org_id == current_user.org_id)

    # 条件过滤
    if start_date:
        query = query.filter(ClassSession.session_date >= start_date)
    if end_date:
        query = query.filter(ClassSession.session_date <= end_date)
    if teacher_id:
        query = query.filter(ClassSession.teacher_id == teacher_id)
    if classroom_id:
        query = query.filter(ClassSession.classroom_id == classroom_id)
    if course_id:
        query = query.filter(ClassSession.course_id == course_id)
    if cycle_id:
        query = query.filter(ClassSession.cycle_id == cycle_id)

    total = query.count()
    items = query.order_by(ClassSession.session_date, ClassSession.time_slot_id).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 构建响应
    results = []
    for item in items:
        session_data = SessionResponse.model_validate(item)
        session_data.course_name = item.course.name if item.course else None
        session_data.teacher_name = item.teacher.name if item.teacher else None
        session_data.classroom_name = item.classroom.name if item.classroom else None
        session_data.time_slot_name = item.time_slot.name if item.time_slot else None
        session_data.start_time = item.time_slot.start_time if item.time_slot else None
        session_data.end_time = item.time_slot.end_time if item.time_slot else None
        # 从 session_students 获取学生ID列表
        session_data.student_ids = [ss.student_id for ss in item.session_students] if item.session_students else []
        session_data.student_count = len(session_data.student_ids)

        # 添加盘点信息
        if item.checkin:
            checkin_data = CheckinResponse.model_validate(item.checkin)
            checkin_data.teacher_name = item.checkin.teacher.name if item.checkin.teacher else None
            session_data.checkin = checkin_data

        results.append(session_data)

    return PaginatedResponse(
        data=results,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase)
async def create_session(
    request: SessionCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """创建课程实例"""
    # 获取机构ID
    from app.models.course import Course
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    org_id = course.org_id
    if not check_org_access(current_user, org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 检查冲突
    conflicts = check_session_conflicts(
        db=db,
        org_id=org_id,
        teacher_id=request.teacher_id,
        classroom_id=request.classroom_id,
        session_date=request.session_date,
        time_slot_id=request.time_slot_id
    )

    if conflicts:
        return ResponseBase(
            success=False,
            data={"conflicts": [c.model_dump() for c in conflicts]},
            message="排课冲突，无法创建"
        )

    # 创建课程实例
    session = ClassSession(
        org_id=org_id,
        course_id=request.course_id,
        teacher_id=request.teacher_id,
        classroom_id=request.classroom_id,
        cycle_id=request.cycle_id,
        cycle_day=request.cycle_day,
        session_date=request.session_date,
        time_slot_id=request.time_slot_id,
        notes=request.notes
    )
    db.add(session)
    db.flush()

    # 添加学生
    if request.student_ids:
        for student_id in request.student_ids:
            session_student = SessionStudent(
                session_id=session.id,
                student_id=student_id
            )
            db.add(session_student)

    db.commit()

    return ResponseBase(
        data={"session_id": session.id},
        message="课程创建成功"
    )


@router.put("/{session_id}", response_model=ResponseBase[SessionResponse])
async def update_session(
    session_id: int,
    request: SessionUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """更新课程实例"""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, session.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 如果修改了时间或资源，检查冲突
    if request.teacher_id or request.classroom_id or request.session_date or request.time_slot_id:
        conflicts = check_session_conflicts(
            db=db,
            org_id=session.org_id,
            teacher_id=request.teacher_id or session.teacher_id,
            classroom_id=request.classroom_id or session.classroom_id,
            session_date=request.session_date or session.session_date,
            time_slot_id=request.time_slot_id or session.time_slot_id,
            exclude_session_id=session_id
        )

        if conflicts:
            return ResponseBase(
                success=False,
                data={"conflicts": [c.model_dump() for c in conflicts]},
                message="排课冲突，无法更新"
            )

    # 更新基本字段
    update_data = request.model_dump(exclude_unset=True, exclude={"student_ids"})
    for key, value in update_data.items():
        setattr(session, key, value)

    # 更新学生列表
    if request.student_ids is not None:
        # 删除旧的学生记录
        db.query(SessionStudent).filter(SessionStudent.session_id == session_id).delete()
        # 添加新的学生记录
        for student_id in request.student_ids:
            session_student = SessionStudent(
                session_id=session_id,
                student_id=student_id
            )
            db.add(session_student)

    db.commit()
    db.refresh(session)

    # 构建响应
    session_data = SessionResponse.model_validate(session)
    session_data.course_name = session.course.name if session.course else None
    session_data.teacher_name = session.teacher.name if session.teacher else None
    session_data.classroom_name = session.classroom.name if session.classroom else None
    session_data.time_slot_name = session.time_slot.name if session.time_slot else None
    session_data.start_time = session.time_slot.start_time if session.time_slot else None
    session_data.end_time = session.time_slot.end_time if session.time_slot else None
    session_data.student_ids = [ss.student_id for ss in session.session_students] if session.session_students else []
    session_data.student_count = len(session_data.student_ids)

    return ResponseBase(
        data=session_data,
        message="课程更新成功"
    )


@router.delete("/{session_id}", response_model=ResponseBase)
async def delete_session(
    session_id: int,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """删除课程实例"""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, session.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    session.status = SessionStatus.CANCELLED
    db.commit()

    return ResponseBase(message="课程已取消")


@router.post("/check-conflict", response_model=ConflictResponse)
async def check_conflict(
    request: ConflictCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查排课冲突"""
    # 需要至少指定一个资源
    if not request.teacher_id and not request.classroom_id:
        raise HTTPException(status_code=400, detail="需要指定教师或教室")

    conflicts = []

    # 检查教师冲突
    if request.teacher_id:
        query = db.query(ClassSession).filter(
            ClassSession.session_date == request.session_date,
            ClassSession.time_slot_id == request.time_slot_id,
            ClassSession.teacher_id == request.teacher_id,
            ClassSession.status != SessionStatus.CANCELLED
        )
        if request.exclude_session_id:
            query = query.filter(ClassSession.id != request.exclude_session_id)

        existing = query.first()
        if existing:
            conflicts.append(ConflictInfo(
                type="teacher",
                description=f"教师在该时间段已有课程安排",
                conflicting_session_id=existing.id
            ))

    # 检查教室冲突
    if request.classroom_id:
        query = db.query(ClassSession).filter(
            ClassSession.session_date == request.session_date,
            ClassSession.time_slot_id == request.time_slot_id,
            ClassSession.classroom_id == request.classroom_id,
            ClassSession.status != SessionStatus.CANCELLED
        )
        if request.exclude_session_id:
            query = query.filter(ClassSession.id != request.exclude_session_id)

        existing = query.first()
        if existing:
            conflicts.append(ConflictInfo(
                type="classroom",
                description=f"教室在该时间段已有课程安排",
                conflicting_session_id=existing.id
            ))

    return ConflictResponse(
        has_conflict=len(conflicts) > 0,
        conflicts=conflicts
    )


@router.post("/batch-create", response_model=ResponseBase)
async def batch_create_sessions(
    request: BatchSessionCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """批量创建课程实例"""
    from app.models.course import Course
    from datetime import timedelta

    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    org_id = course.org_id
    if not check_org_access(current_user, org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    created_count = 0
    conflict_count = 0
    errors = []

    current_date = request.start_date
    while current_date <= request.end_date:
        # 检查是否在指定的星期几
        if request.days_of_week and current_date.weekday() not in [d - 1 if d > 0 else 6 for d in request.days_of_week]:
            current_date += timedelta(days=1)
            continue

        for time_slot_id in request.time_slot_ids:
            # 检查冲突
            conflicts = check_session_conflicts(
                db=db,
                org_id=org_id,
                teacher_id=request.teacher_id,
                classroom_id=request.classroom_id,
                session_date=current_date,
                time_slot_id=time_slot_id
            )

            if conflicts:
                conflict_count += 1
                errors.append({
                    "date": str(current_date),
                    "time_slot_id": time_slot_id,
                    "conflicts": [c.model_dump() for c in conflicts]
                })
                continue

            # 创建课程
            session = ClassSession(
                org_id=org_id,
                course_id=request.course_id,
                teacher_id=request.teacher_id,
                classroom_id=request.classroom_id,
                cycle_id=request.cycle_id,
                session_date=current_date,
                time_slot_id=time_slot_id,
                notes=request.notes
            )
            db.add(session)
            db.flush()  # 获取 session.id

            # 添加学生
            if request.student_ids:
                for student_id in request.student_ids:
                    session_student = SessionStudent(
                        session_id=session.id,
                        student_id=student_id
                    )
                    db.add(session_student)

            created_count += 1

        current_date += timedelta(days=1)

    db.commit()

    return ResponseBase(
        data={
            "created_count": created_count,
            "conflict_count": conflict_count,
            "errors": errors
        },
        message=f"批量创建完成，成功 {created_count} 个，冲突 {conflict_count} 个"
    )