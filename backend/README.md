# 后端本地开发指南

## 环境要求

- Python 3.11+
- MySQL 8.0

## 快速启动

### Windows

```bash
# 双击运行 start.bat
# 或在命令行执行：
start.bat
```

### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

## 手动启动步骤

### 1. 创建虚拟环境

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `.env` 文件，修改数据库连接信息：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/timetable
```

### 4. 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE timetable CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入初始数据
USE timetable;
SOURCE migrations/init.sql;
```

### 5. 启动服务

```bash
uvicorn main:app --reload --port 8000
```

## 访问地址

| 地址 | 说明 |
|------|------|
| http://localhost:8000 | API 根路径 |
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/redoc | ReDoc API 文档 |

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 机构管理员 | org_admin | org123 |

## 常见问题

### 数据库连接失败

1. 确认 MySQL 服务已启动
2. 检查 `.env` 中的数据库连接信息
3. 确认数据库用户有足够权限

### 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 清除缓存重新安装
pip install -r requirements.txt --no-cache-dir
```