"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:root123@localhost:3306/timetable"

    # JWT 配置
    JWT_SECRET: str = "dev-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5175", "http://localhost:80", "http://localhost", "http://127.0.0.1:5175"]

    # 应用配置
    APP_NAME: str = "补习班排课表系统"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()