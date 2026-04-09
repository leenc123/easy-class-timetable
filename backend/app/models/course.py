"""
课程模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CourseStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class Course(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    name = Column(String(200), nullable=False, comment="课程名称")
    code = Column(String(50), comment="课程编码")
    subject = Column(String(50), nullable=False, comment="科目")
    duration_minutes = Column(Integer, nullable=False, default=60, comment="单次课时长")
    min_students = Column(Integer, default=1, comment="最少学生数")
    max_students = Column(Integer, default=30, comment="最多学生数")
    required_equipment = Column(JSON, comment="所需设备")
    description = Column(String(500), comment="描述")
    status = Column(SQLEnum(CourseStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]), default=CourseStatus.ACTIVE, comment="状态")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="courses")
    course_teachers = relationship("CourseTeacher", back_populates="course")
    course_students = relationship("CourseStudent", back_populates="course")
    sessions = relationship("ClassSession", back_populates="course")


class CourseTeacher(Base):
    __tablename__ = "course_teachers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False, comment="是否主教")

    # 关联关系
    course = relationship("Course", back_populates="course_teachers")
    teacher = relationship("Teacher", back_populates="course_teachers")


class CourseStudent(Base):
    __tablename__ = "course_students"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(TIMESTAMP, server_default=func.now(), comment="报名时间")
    status = Column(String(20), default="enrolled", comment="状态: enrolled/completed/dropped")

    # 关联关系
    course = relationship("Course", back_populates="course_students")
    student = relationship("Student", back_populates="course_students")