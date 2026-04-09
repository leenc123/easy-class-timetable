"""
教师模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, ForeignKey, JSON, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, comment="关联用户ID")
    name = Column(String(100), nullable=False, comment="教师姓名")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    subjects = Column(JSON, comment="可教授科目")
    max_hours_per_week = Column(Integer, default=20, comment="每周最大课时")
    bio = Column(String(500), comment="简介")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="teachers")
    user = relationship("User", back_populates="teacher_profile")
    availabilities = relationship("TeacherAvailability", back_populates="teacher")
    course_teachers = relationship("CourseTeacher", back_populates="teacher")
    sessions = relationship("ClassSession", back_populates="teacher")


class TeacherAvailability(Base):
    __tablename__ = "teacher_availability"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(BigInteger, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, comment="教师ID")
    day_of_week = Column(Integer, nullable=False, comment="星期几 0-6")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    is_recurring = Column(Boolean, default=True, comment="是否每周重复")
    specific_date = Column(Date, comment="具体日期（非重复时）")
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关联关系
    teacher = relationship("Teacher", back_populates="availabilities")