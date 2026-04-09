"""
排课周期模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, TIMESTAMP, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SchedulingCycle(Base):
    __tablename__ = "scheduling_cycles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    name = Column(String(100), nullable=False, comment="周期名称")
    cycle_days = Column(Integer, nullable=False, comment="周期天数")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    description = Column(Text, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="cycles")
    cycle_dates = relationship("CycleDate", back_populates="cycle")
    sessions = relationship("ClassSession", back_populates="cycle")


class CycleDate(Base):
    __tablename__ = "cycle_dates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cycle_id = Column(BigInteger, ForeignKey("scheduling_cycles.id", ondelete="CASCADE"), nullable=False)
    cycle_day = Column(Integer, nullable=False, comment="周期中的第几天")
    actual_date = Column(Date, nullable=False, comment="实际日期")

    # 关联关系
    cycle = relationship("SchedulingCycle", back_populates="cycle_dates")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False, comment="所属机构ID")
    name = Column(String(50), nullable=False, comment="时间段名称")
    start_time = Column(String(10), nullable=False, comment="开始时间 HH:MM")
    end_time = Column(String(10), nullable=False, comment="结束时间 HH:MM")
    display_order = Column(Integer, nullable=False, default=1, comment="显示顺序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关联关系
    organization = relationship("Organization", back_populates="time_slots")
    sessions = relationship("ClassSession", back_populates="time_slot")