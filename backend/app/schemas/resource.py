"""
资源相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time, date


# ============ 教室 ============
class ClassroomCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: Optional[str] = None
    capacity: int = Field(default=30, ge=1)
    location: Optional[str] = None
    equipment: Optional[List[str]] = None
    description: Optional[str] = None


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    equipment: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClassroomResponse(BaseModel):
    id: int
    org_id: int
    name: str
    code: Optional[str]
    capacity: int
    location: Optional[str]
    equipment: Optional[List[str]]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 教师 ============
class TeacherCreate(BaseModel):
    name: str = Field(..., max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    subjects: Optional[List[str]] = None
    max_hours_per_week: int = Field(default=20, ge=1)
    bio: Optional[str] = None
    create_user_account: bool = False  # 是否同时创建用户账号


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    subjects: Optional[List[str]] = None
    max_hours_per_week: Optional[int] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherResponse(BaseModel):
    id: int
    org_id: int
    user_id: Optional[int]
    name: str
    phone: Optional[str]
    email: Optional[str]
    subjects: Optional[List[str]]
    max_hours_per_week: int
    bio: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    is_recurring: bool = True
    specific_date: Optional[date] = None


class AvailabilityResponse(BaseModel):
    id: int
    teacher_id: int
    day_of_week: int
    start_time: str
    end_time: str
    is_recurring: bool
    specific_date: Optional[date]

    class Config:
        from_attributes = True


# ============ 学生 ============
class StudentCreate(BaseModel):
    name: str = Field(..., max_length=100)
    grade: Optional[str] = None
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    notes: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(BaseModel):
    id: int
    org_id: int
    user_id: Optional[int]
    name: str
    grade: Optional[str]
    phone: Optional[str]
    parent_name: Optional[str]
    parent_phone: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 课程 ============
class CourseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: Optional[str] = None
    subject: str = Field(..., max_length=50)
    duration_minutes: int = Field(default=60, ge=15)
    min_students: int = Field(default=1, ge=1)
    max_students: int = Field(default=30, ge=1)
    required_equipment: Optional[List[str]] = None
    description: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    subject: Optional[str] = None
    duration_minutes: Optional[int] = None
    min_students: Optional[int] = None
    max_students: Optional[int] = None
    required_equipment: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    org_id: int
    name: str
    code: Optional[str]
    subject: str
    duration_minutes: int
    min_students: int
    max_students: int
    required_equipment: Optional[List[str]]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    teachers: Optional[List[int]] = None  # 教师ID列表
    students: Optional[List[int]] = None  # 学生ID列表

    class Config:
        from_attributes = True


class CourseTeacherAssign(BaseModel):
    teacher_ids: List[int]
    primary_teacher_id: Optional[int] = None


class CourseStudentAssign(BaseModel):
    student_ids: List[int]