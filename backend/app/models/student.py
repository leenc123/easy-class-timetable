"""
学生模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), comment="关联用户ID（家长账号）")
    name = Column(String(100), nullable=False, comment="学生姓名")
    grade = Column(String(20), comment="年级")
    phone = Column(String(20), comment="联系电话")
    parent_name = Column(String(100), comment="家长姓名")
    parent_phone = Column(String(20), comment="家长电话")
    notes = Column(String(500), comment="备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="students")
    user = relationship("User", back_populates="student_profiles")
    course_students = relationship("CourseStudent", back_populates="student")
    session_attendances = relationship("StudentAttendance", back_populates="student")
    subject_hours = relationship("StudentSubjectHours", back_populates="student", cascade="all, delete-orphan")