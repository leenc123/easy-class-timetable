"""
教室模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    name = Column(String(100), nullable=False, comment="教室名称")
    code = Column(String(50), comment="教室编码")
    capacity = Column(Integer, nullable=False, default=30, comment="容量")
    location = Column(String(200), comment="位置")
    equipment = Column(JSON, comment="设备列表")
    description = Column(Text, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="classrooms")
    sessions = relationship("ClassSession", back_populates="classroom")