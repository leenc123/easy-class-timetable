"""
教师视图路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import ClassSession
from app.schemas.base import ResponseBase
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/{teacher_id}", response_model=ResponseBase)
async def get_teacher_schedule(
    teacher_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取教师课表"""
    query = db.query(ClassSession).filter(
        ClassSession.teacher_id == teacher_id,
        ClassSession.session_date >= start_date,
        ClassSession.session_date <= end_date
    )

    # 权限过滤
    if current_user.role != UserRole.SUPER_ADMIN:
        query = query.filter(ClassSession.org_id == current_user.org_id)

    # 如果是教师角色，只能查看自己的课表
    if current_user.role == UserRole.TEACHER:
        if current_user.teacher_profile and current_user.teacher_profile.id != teacher_id:
            return ResponseBase(data={}, message="只能查看自己的课表")

    sessions = query.order_by(ClassSession.session_date, ClassSession.time_slot_id).all()

    # 按日期分组
    schedule_data = {}
    for session in sessions:
        date_str = str(session.session_date)
        if date_str not in schedule_data:
            schedule_data[date_str] = []

        schedule_data[date_str].append({
            "id": session.id,
            "course_name": session.course.name if session.course else None,
            "classroom_name": session.classroom.name if session.classroom else None,
            "time_slot_name": session.time_slot.name if session.time_slot else None,
            "start_time": session.time_slot.start_time if session.time_slot else None,
            "end_time": session.time_slot.end_time if session.time_slot else None,
            "status": session.status.value,
            "student_count": len(session.student_attendances) if session.student_attendances else 0
        })

    return ResponseBase(data=schedule_data)