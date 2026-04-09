"""
课表导出路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import io

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import ClassSession
from app.services.auth import require_role, get_current_user, check_org_access
from app.services.export_pdf import generate_schedule_pdf
from app.services.export_excel import generate_schedule_excel

router = APIRouter()


@router.get("/pdf")
async def export_pdf(
    start_date: date,
    end_date: date,
    teacher_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
    course_id: Optional[int] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """导出课表为 PDF"""
    # 权限过滤
    target_org_id = org_id if current_user.role == UserRole.SUPER_ADMIN else current_user.org_id
    if not target_org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    # 查询课程
    query = db.query(ClassSession).filter(
        ClassSession.org_id == target_org_id,
        ClassSession.session_date >= start_date,
        ClassSession.session_date <= end_date
    )

    if teacher_id:
        query = query.filter(ClassSession.teacher_id == teacher_id)
    if classroom_id:
        query = query.filter(ClassSession.classroom_id == classroom_id)
    if course_id:
        query = query.filter(ClassSession.course_id == course_id)

    sessions = query.order_by(ClassSession.session_date, ClassSession.time_slot_id).all()

    # 生成 PDF
    pdf_bytes = generate_schedule_pdf(sessions, start_date, end_date)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=schedule_{start_date}_{end_date}.pdf"
        }
    )


@router.get("/excel")
async def export_excel(
    start_date: date,
    end_date: date,
    teacher_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
    course_id: Optional[int] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """导出课表为 Excel"""
    # 权限过滤
    target_org_id = org_id if current_user.role == UserRole.SUPER_ADMIN else current_user.org_id
    if not target_org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    # 查询课程
    query = db.query(ClassSession).filter(
        ClassSession.org_id == target_org_id,
        ClassSession.session_date >= start_date,
        ClassSession.session_date <= end_date
    )

    if teacher_id:
        query = query.filter(ClassSession.teacher_id == teacher_id)
    if classroom_id:
        query = query.filter(ClassSession.classroom_id == classroom_id)
    if course_id:
        query = query.filter(ClassSession.course_id == course_id)

    sessions = query.order_by(ClassSession.session_date, ClassSession.time_slot_id).all()

    # 生成 Excel
    excel_bytes = generate_schedule_excel(sessions)

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=schedule_{start_date}_{end_date}.xlsx"
        }
    )