"""
学生学科学时模型
"""
from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudentSubjectHours(Base):
    """学生学科学时配置"""
    __tablename__ = "student_subject_hours"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, comment="学生ID")
    subject = Column(String(50), nullable=False, comment="学科名称")
    total_hours = Column(Integer, nullable=False, default=0, comment="总学时（分钟）")
    remaining_hours = Column(Integer, nullable=False, default=0, comment="剩余学时（分钟）")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    student = relationship("Student", back_populates="subject_hours")