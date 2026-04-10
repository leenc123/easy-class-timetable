"""
冲突检测服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.schedule import ClassSession, SessionStatus, SessionStudent
from app.schemas.schedule import ConflictInfo


def check_session_conflicts(
    db: Session,
    org_id: int,
    teacher_id: Optional[int],
    classroom_id: Optional[int],
    session_date: date,
    time_slot_id: int,
    student_ids: Optional[List[int]] = None,
    exclude_session_id: Optional[int] = None
) -> List[ConflictInfo]:
    """检查课程实例是否存在冲突"""
    conflicts = []

    # 检查教师冲突
    if teacher_id:
        query = db.query(ClassSession).filter(
            ClassSession.org_id == org_id,
            ClassSession.session_date == session_date,
            ClassSession.time_slot_id == time_slot_id,
            ClassSession.teacher_id == teacher_id,
            ClassSession.status != SessionStatus.CANCELLED
        )
        if exclude_session_id:
            query = query.filter(ClassSession.id != exclude_session_id)

        existing = query.first()
        if existing:
            conflicts.append(ConflictInfo(
                type="teacher",
                description=f"教师在该时间段已有课程：{existing.course.name if existing.course else '未知课程'}",
                conflicting_session_id=existing.id,
                conflicting_resource_name=existing.teacher.name if existing.teacher else None
            ))

    # 检查教室冲突
    if classroom_id:
        query = db.query(ClassSession).filter(
            ClassSession.org_id == org_id,
            ClassSession.session_date == session_date,
            ClassSession.time_slot_id == time_slot_id,
            ClassSession.classroom_id == classroom_id,
            ClassSession.status != SessionStatus.CANCELLED
        )
        if exclude_session_id:
            query = query.filter(ClassSession.id != exclude_session_id)

        existing = query.first()
        if existing:
            conflicts.append(ConflictInfo(
                type="classroom",
                description=f"教室在该时间段已被占用：{existing.course.name if existing.course else '未知课程'}",
                conflicting_session_id=existing.id,
                conflicting_resource_name=existing.classroom.name if existing.classroom else None
            ))

    # 检查学生冲突
    if student_ids:
        for student_id in student_ids:
            # 查询该学生在该时间段是否有其他课程
            query = db.query(ClassSession).join(
                SessionStudent, ClassSession.id == SessionStudent.session_id
            ).filter(
                ClassSession.org_id == org_id,
                ClassSession.session_date == session_date,
                ClassSession.time_slot_id == time_slot_id,
                SessionStudent.student_id == student_id,
                ClassSession.status != SessionStatus.CANCELLED
            )
            if exclude_session_id:
                query = query.filter(ClassSession.id != exclude_session_id)

            existing = query.first()
            if existing:
                # 获取学生姓名
                from app.models.student import Student
                student = db.query(Student).filter(Student.id == student_id).first()
                student_name = student.name if student else f"学生ID:{student_id}"

                conflicts.append(ConflictInfo(
                    type="student",
                    description=f"学生 {student_name} 在该时间段已有课程：{existing.course.name if existing.course else '未知课程'}",
                    conflicting_session_id=existing.id,
                    conflicting_resource_name=student_name
                ))

    return conflicts


def get_resource_schedule(
    db: Session,
    org_id: int,
    resource_type: str,
    resource_id: int,
    start_date: date,
    end_date: date
) -> List[ClassSession]:
    """获取资源的课程安排"""
    query = db.query(ClassSession).filter(
        ClassSession.org_id == org_id,
        ClassSession.session_date >= start_date,
        ClassSession.session_date <= end_date,
        ClassSession.status != SessionStatus.CANCELLED
    )

    if resource_type == "teacher":
        query = query.filter(ClassSession.teacher_id == resource_id)
    elif resource_type == "classroom":
        query = query.filter(ClassSession.classroom_id == resource_id)
    elif resource_type == "course":
        query = query.filter(ClassSession.course_id == resource_id)

    return query.order_by(ClassSession.session_date, ClassSession.time_slot_id).all()