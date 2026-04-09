@echo off
echo ====================================
echo 补习班排课表系统 - 后端启动脚本
echo ====================================
echo.

cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成!
) else (
    echo [1/3] 虚拟环境已存在，跳过创建
)

echo.
echo [2/3] 激活虚拟环境并安装依赖...
call venv\Scripts\activate
pip install -r requirements.txt -q

echo.
echo [3/3] 启动后端服务...
echo.
echo 数据库连接: %DATABASE_URL%
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000