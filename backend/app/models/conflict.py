"""
排课冲突日志模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ConflictType(str, enum.Enum):
    CLASSROOM = "classroom"  # 教室冲突
    TEACHER = "teacher"      # 教师冲突
    STUDENT = "student"      # 学生冲突
    TIME = "time"            # 时间冲突


class SchedulingConflict(Base):
    __tablename__ = "scheduling_conflicts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("class_sessions.id"), comment="课程实例ID")
    conflict_type = Column(SQLEnum(ConflictType), nullable=False, comment="冲突类型")
    conflicting_resource_type = Column(String(50), nullable=False, comment="冲突资源类型")
    conflicting_resource_id = Column(BigInteger, nullable=False, comment="冲突资源ID")
    conflicting_session_id = Column(BigInteger, comment="冲突的课程实例ID")
    description = Column(Text, nullable=False, comment="冲突描述")
    resolved = Column(Boolean, default=False, comment="是否已解决")
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关联关系
    organization = relationship("Organization")
    session = relationship("ClassSession")