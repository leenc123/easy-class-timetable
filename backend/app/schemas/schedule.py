"""
排课周期与课表相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ============ 排课周期 ============
class CycleCreate(BaseModel):
    org_id: Optional[int] = None  # 超管创建时指定机构
    name: str = Field(..., max_length=100)
    cycle_days: int = Field(..., ge=1, le=365)
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


class CycleUpdate(BaseModel):
    name: Optional[str] = None
    cycle_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CycleResponse(BaseModel):
    id: int
    org_id: int
    name: str
    cycle_days: int
    start_date: date
    end_date: Optional[date]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CycleDateResponse(BaseModel):
    id: int
    cycle_id: int
    cycle_day: int
    actual_date: date

    class Config:
        from_attributes = True


# ============ 时间段 ============
class TimeSlotCreate(BaseModel):
    org_id: Optional[int] = None  # 超管创建时指定机构
    name: str = Field(..., max_length=50)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    display_order: int = Field(default=1, ge=1)


class TimeSlotUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class TimeSlotResponse(BaseModel):
    id: int
    org_id: int
    name: str
    start_time: str
    end_time: str
    display_order: int
    is_active: bool

    class Config:
        from_attributes = True


# ============ 课程实例 ============
class SessionCreate(BaseModel):
    course_id: int
    teacher_id: int
    classroom_id: int
    cycle_id: Optional[int] = None
    cycle_day: Optional[int] = None
    session_date: date
    time_slot_id: int
    student_ids: Optional[List[int]] = None
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    session_date: Optional[date] = None
    time_slot_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    org_id: int
    course_id: int
    course_name: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    classroom_id: int
    classroom_name: Optional[str] = None
    cycle_id: Optional[int]
    cycle_day: Optional[int]
    session_date: date
    time_slot_id: int
    time_slot_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str
    notes: Optional[str]
    student_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchSessionCreate(BaseModel):
    course_id: int
    teacher_id: int
    classroom_id: int
    cycle_id: Optional[int] = None
    start_date: date
    end_date: date
    time_slot_ids: List[int]
    days_of_week: Optional[List[int]] = None  # 0-6, 空则每天
    student_ids: Optional[List[int]] = None
    notes: Optional[str] = None


class ConflictCheckRequest(BaseModel):
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    session_date: date
    time_slot_id: int
    exclude_session_id: Optional[int] = None


class ConflictInfo(BaseModel):
    type: str
    description: str
    conflicting_session_id: Optional[int] = None
    conflicting_resource_name: Optional[str] = None


class ConflictResponse(BaseModel):
    has_conflict: bool
    conflicts: List[ConflictInfo] = []


# ============ 课程盘点 ============
class CheckinCreate(BaseModel):
    session_id: int
    expected_count: int = Field(..., ge=0)
    actual_count: int = Field(..., ge=0)
    notes: Optional[str] = None


class CheckinResponse(BaseModel):
    id: int
    session_id: int
    teacher_id: int
    teacher_name: Optional[str] = None
    expected_count: int
    actual_count: int
    notes: Optional[str]
    checkin_time: datetime

    class Config:
        from_attributes = True