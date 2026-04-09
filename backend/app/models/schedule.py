"""
课程实例与盘点模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"      # 已安排
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消
    RESCHEDULED = "rescheduled"  # 已调课


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    course_id = Column(BigInteger, ForeignKey("courses.id"), nullable=False, comment="课程ID")
    teacher_id = Column(BigInteger, ForeignKey("teachers.id"), nullable=False, comment="教师ID")
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id"), nullable=False, comment="教室ID")
    cycle_id = Column(BigInteger, ForeignKey("scheduling_cycles.id"), comment="周期ID")
    cycle_day = Column(Integer, comment="周期中的第几天")
    session_date = Column(Date, nullable=False, comment="上课日期")
    time_slot_id = Column(BigInteger, ForeignKey("time_slots.id"), nullable=False, comment="时间段ID")
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.SCHEDULED, comment="状态")
    notes = Column(Text, comment="备注")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization")
    course = relationship("Course", back_populates="sessions")
    teacher = relationship("Teacher", back_populates="sessions")
    classroom = relationship("Classroom", back_populates="sessions")
    cycle = relationship("SchedulingCycle", back_populates="sessions")
    time_slot = relationship("TimeSlot", back_populates="sessions")
    student_attendances = relationship("StudentAttendance", back_populates="session")
    checkin = relationship("SessionCheckin", uselist=False, back_populates="session")


class StudentAttendance(Base):
    __tablename__ = "student_attendances"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    attendance_status = Column(String(20), default="present", comment="出勤状态: present/absent/late/excused")

    # 关联关系
    session = relationship("ClassSession", back_populates="student_attendances")
    student = relationship("Student", back_populates="session_attendances")


class SessionCheckin(Base):
    """课程人数盘点（任课老师课后填写）"""
    __tablename__ = "session_checkins"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("class_sessions.id"), unique=True, nullable=False, comment="课程实例ID")
    teacher_id = Column(BigInteger, ForeignKey("teachers.id"), nullable=False, comment="填写教师ID")
    expected_count = Column(Integer, nullable=False, comment="应到人数")
    actual_count = Column(Integer, nullable=False, comment="实到人数")
    notes = Column(Text, comment="备注")
    checkin_time = Column(TIMESTAMP, server_default=func.now(), comment="盘点时间")

    # 关联关系
    session = relationship("ClassSession", back_populates="checkin")
    teacher = relationship("Teacher")