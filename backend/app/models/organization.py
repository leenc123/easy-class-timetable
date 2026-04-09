"""
机构模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="机构名称")
    code = Column(String(50), unique=True, nullable=False, comment="机构编码")
    address = Column(String(500), comment="地址")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    logo_url = Column(String(500), comment="Logo URL")
    description = Column(Text, comment="机构描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    users = relationship("User", back_populates="organization")
    classrooms = relationship("Classroom", back_populates="organization")
    teachers = relationship("Teacher", back_populates="organization")
    students = relationship("Student", back_populates="organization")
    courses = relationship("Course", back_populates="organization")
    cycles = relationship("SchedulingCycle", back_populates="organization")
    time_slots = relationship("TimeSlot", back_populates="organization")