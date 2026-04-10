"""
学生学科课时模型
"""
from sqlalchemy import Column, BigInteger, Float, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudentSubjectHours(Base):
    """学生学科课时配置"""
    __tablename__ = "student_subject_hours"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, comment="学生ID")
    subject = Column(String(50), nullable=False, comment="学科名称")
    total_lessons = Column(Float, nullable=False, default=0, comment="总课时（1课时=120分钟）")
    remaining_lessons = Column(Float, nullable=False, default=0, comment="剩余课时")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    student = relationship("Student", back_populates="subject_hours")