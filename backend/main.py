"""
补习班排课表系统 - 后端主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import bcrypt
import time

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, organizations, users, classrooms, teachers, students, courses, cycles, schedule, exports, checkins
from app.routers.views import calendar, teacher_view, student_view, classroom_view
from app.models.user import User, UserRole
from app.models.organization import Organization


def wait_for_db(max_retries=30, retry_interval=2):
    """等待数据库就绪"""
    import pymysql
    from urllib.parse import urlparse

    # 解析数据库连接
    parsed = urlparse(settings.DATABASE_URL.replace("mysql+pymysql://", "mysql://"))
    host = parsed.hostname or "localhost"
    port = parsed.port or 3306

    for i in range(max_retries):
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=parsed.username,
                password=parsed.password,
                connect_timeout=5
            )
            conn.close()
            print(f"数据库连接成功: {host}:{port}")
            return True
        except Exception as e:
            print(f"等待数据库就绪... ({i+1}/{max_retries}): {e}")
            time.sleep(retry_interval)

    raise Exception("数据库连接超时")


def init_default_data():
    """初始化默认数据"""
    db = SessionLocal()
    try:
        # 检查是否已有超级管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建默认机构
            org = db.query(Organization).filter(Organization.code == "DEMO001").first()
            if not org:
                org = Organization(
                    name="示范培训机构",
                    code="DEMO001",
                    description="系统演示机构"
                )
                db.add(org)
                db.commit()
                db.refresh(org)

            # 创建超级管理员
            admin_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username="admin",
                password_hash=admin_hash,
                real_name="系统管理员",
                role=UserRole.SUPER_ADMIN
            )
            db.add(admin)

            # 创建机构管理员
            org_admin_hash = bcrypt.hashpw("org123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            org_admin = User(
                org_id=org.id,
                username="org_admin",
                password_hash=org_admin_hash,
                real_name="机构管理员",
                role=UserRole.ORG_ADMIN
            )
            db.add(org_admin)

            db.commit()
            print("默认用户创建完成: admin/admin123, org_admin/org123")
    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 等待数据库就绪
    wait_for_db()
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    # 初始化默认数据
    init_default_data()
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