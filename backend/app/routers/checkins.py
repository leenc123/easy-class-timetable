"""
课程盘点路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import ClassSession, SessionCheckin, StudentAttendance, SessionStatus
from app.models.student_subject_hours import StudentSubjectHours
from app.schemas.schedule import CheckinCreate, CheckinResponse
from app.schemas.base import ResponseBase
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


def deduct_student_hours(db: Session, session: ClassSession):
    """扣除学生的课时（1课时=120分钟）"""
    import logging
    logger = logging.getLogger(__name__)

    # 获取课程的时长和学科
    course = session.course
    if not course:
        logger.warning(f"Session {session.id} has no course")
        return

    duration_minutes = course.duration_minutes
    subject = course.subject

    # 将分钟转换为课时（1课时=120分钟，向下取整，不足120分钟算0.5课时）
    if duration_minutes >= 120:
        lessons_to_deduct = duration_minutes // 120
    else:
        lessons_to_deduct = 0.5  # 不足120分钟按0.5课时扣除

    logger.info(f"Deducting lessons: session={session.id}, course={course.name}, subject={subject}, duration={duration_minutes}min, lessons={lessons_to_deduct}")

    # 获取该课程的学生
    attendances = db.query(StudentAttendance).filter(
        StudentAttendance.session_id == session.id
    ).all()

    logger.info(f"Found {len(attendances)} student attendances for session {session.id}")

    for attendance in attendances:
        # 查找学生对该学科的课时配置
        subject_hours = db.query(StudentSubjectHours).filter(
            StudentSubjectHours.student_id == attendance.student_id,
            StudentSubjectHours.subject == subject
        ).first()

        if subject_hours:
            logger.info(f"Student {attendance.student_id}: subject={subject}, remaining={subject_hours.remaining_lessons}, deducting={lessons_to_deduct}")
            if subject_hours.remaining_lessons > 0:
                subject_hours.remaining_lessons -= lessons_to_deduct
                if subject_hours.remaining_lessons < 0:
                    subject_hours.remaining_lessons = 0
                logger.info(f"Student {attendance.student_id}: new remaining={subject_hours.remaining_lessons}")
            else:
                logger.warning(f"Student {attendance.student_id}: no remaining lessons")
        else:
            logger.warning(f"Student {attendance.student_id}: no subject_hours config for subject={subject}")


@router.post("", response_model=ResponseBase[CheckinResponse])
async def create_checkin(
    request: CheckinCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """创建课程盘点（人数统计）"""
    session = db.query(ClassSession).filter(ClassSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, session.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 检查是否已有盘点记录
    existing = db.query(SessionCheckin).filter(
        SessionCheckin.session_id == request.session_id
    ).first()

    if existing:
        # 更新现有记录
        existing.expected_count = request.expected_count
        existing.actual_count = request.actual_count
        existing.notes = request.notes
        checkin = existing
    else:
        # 创建新记录
        teacher_id = session.teacher_id
        # 如果是教师登录，使用当前教师ID
        if current_user.role == UserRole.TEACHER and current_user.teacher_profile:
            teacher_id = current_user.teacher_profile.id

        checkin = SessionCheckin(
            session_id=request.session_id,
            teacher_id=teacher_id,
            expected_count=request.expected_count,
            actual_count=request.actual_count,
            notes=request.notes
        )
        db.add(checkin)

    # 如果有实际到场人数，标记课程完成并扣除学时
    if request.actual_count > 0:
        session.status = SessionStatus.COMPLETED
        deduct_student_hours(db, session)

    # 统一提交所有修改
    db.commit()
    db.refresh(checkin)

    response = CheckinResponse.model_validate(checkin)
    response.teacher_name = checkin.teacher.name if checkin.teacher else None

    return ResponseBase(
        data=response,
        message="盘点记录创建成功"
    )


@router.get("/session/{session_id}", response_model=ResponseBase[CheckinResponse])
async def get_session_checkin(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取课程的盘点记录"""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not check_org_access(current_user, session.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    checkin = db.query(SessionCheckin).filter(
        SessionCheckin.session_id == session_id
    ).first()

    if not checkin:
        return ResponseBase(
            success=False,
            data=None,
            message="暂无盘点记录"
        )

    response = CheckinResponse.model_validate(checkin)
    response.teacher_name = checkin.teacher.name if checkin.teacher else None

    return ResponseBase(data=response)