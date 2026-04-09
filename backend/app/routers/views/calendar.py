"""
日历视图路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import ClassSession
from app.schemas.base import ResponseBase
from app.services.auth import get_current_user

router = APIRouter()


@router.get("", response_model=ResponseBase)
async def get_calendar_view(
    start_date: date = Query(...),
    end_date: date = Query(...),
    view_type: str = Query("week", regex="^(day|week|month|cycle)$"),
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日历视图课表"""
    query = db.query(ClassSession).filter(
        ClassSession.session_date >= start_date,
        ClassSession.session_date <= end_date
    )

    # 权限过滤
    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(ClassSession.org_id == org_id)
    else:
        query = query.filter(ClassSession.org_id == current_user.org_id)

    sessions = query.order_by(ClassSession.session_date, ClassSession.time_slot_id).all()

    # 构建日历数据结构
    calendar_data = {}
    for session in sessions:
        date_str = str(session.session_date)
        if date_str not in calendar_data:
            calendar_data[date_str] = []

        calendar_data[date_str].append({
            "id": session.id,
            "course_id": session.course_id,
            "course_name": session.course.name if session.course else None,
            "teacher_id": session.teacher_id,
            "teacher_name": session.teacher.name if session.teacher else None,
            "classroom_id": session.classroom_id,
            "classroom_name": session.classroom.name if session.classroom else None,
            "time_slot_id": session.time_slot_id,
            "time_slot_name": session.time_slot.name if session.time_slot else None,
            "start_time": session.time_slot.start_time if session.time_slot else None,
            "end_time": session.time_slot.end_time if session.time_slot else None,
            "status": session.status.value,
            "student_count": len(session.student_attendances) if session.student_attendances else 0
        })

    return ResponseBase(data=calendar_data)