"""
补习班排课表系统 - 后端主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import auth, organizations, users, classrooms, teachers, students, courses, cycles, schedule, exports, checkins
from app.routers.views import calendar, teacher_view, student_view, classroom_view


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时清理资源


app = FastAPI(
    title="补习班排课表系统 API",
    description="基于 FastAPI 的排课管理后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["机构管理"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(classrooms.router, prefix="/api/v1/classrooms", tags=["教室管理"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["教师管理"])
app.include_router(students.router, prefix="/api/v1/students", tags=["学生管理"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["课程管理"])
app.include_router(cycles.router, prefix="/api/v1/cycles", tags=["排课周期"])
app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["课表调度"])
app.include_router(exports.router, prefix="/api/v1/exports", tags=["课表导出"])
app.include_router(checkins.router, prefix="/api/v1/checkins", tags=["课程盘点"])

# 视图路由
app.include_router(calendar.router, prefix="/api/v1/views/calendar", tags=["日历视图"])
app.include_router(teacher_view.router, prefix="/api/v1/views/teacher", tags=["教师视图"])
app.include_router(student_view.router, prefix="/api/v1/views/student", tags=["学生视图"])
app.include_router(classroom_view.router, prefix="/api/v1/views/classroom", tags=["教室视图"])


@app.get("/")
async def root():
    return {"message": "补习班排课表系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}