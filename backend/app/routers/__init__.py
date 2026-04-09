"""
路由初始化
"""
from app.routers import auth, organizations, users, classrooms, teachers, students, courses, cycles, schedule, exports, checkins

__all__ = [
    "auth", "organizations", "users", "classrooms", "teachers",
    "students", "courses", "cycles", "schedule", "exports", "checkins"
]