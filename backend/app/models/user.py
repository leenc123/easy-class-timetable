"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"      # 超级管理员（系统级）
    ORG_ADMIN = "org_admin"          # 机构管理员
    TEACHER = "teacher"              # 教师
    STUDENT_PARENT = "student_parent" # 学生/家长


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=True, comment="所属机构ID（超管为空）")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(100), nullable=False, comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.TEACHER, comment="角色")
    avatar_url = Column(String(500), comment="头像URL")
    is_active = Column(Boolean, default=True, comment="是否启用")
    last_login_at = Column(TIMESTAMP, comment="最后登录时间")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="users")
    teacher_profile = relationship("Teacher", uselist=False, back_populates="user")
    student_profiles = relationship("Student", back_populates="user")