# 补习班排课表系统

基于 Vue3 + Element Plus + FastAPI + MySQL 的补习班排课管理系统。

## 功能特性

- ✅ 多机构支持与数据隔离
- ✅ 用户认证与权限控制（超管/机构管理员/教师/学生家长）
- ✅ 教室/教师/学生/课程资源管理
- ✅ 自定义排课周期（7天/10天/14天等）
- ✅ 拖拽式排课（规划中）
- ✅ 冲突自动检测
- ✅ 课程人数盘点
- ✅ 课表导出（PDF/Excel）
- ✅ 移动端适配

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Element Plus + Pinia + Vue Router |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.0 |
| 部署 | Docker Compose |

## 项目结构

```
easy-class-timetable/
├── frontend/              # Vue3 前端项目
│   ├── src/
│   │   ├── api/          # API 客户端
│   │   ├── components/   # 通用组件
│   │   ├── layouts/      # 布局组件
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── styles/       # 样式文件
│   │   └── views/        # 页面视图
│   ├── Dockerfile
│   └── nginx.conf
├── backend/               # FastAPI 后端项目
│   ├── app/
│   │   ├── models/       # 数据模型
│   │   ├── routers/      # API 路由
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/     # 业务逻辑
│   ├── migrations/       # 数据库迁移
│   ├── Dockerfile
│   └── main.py
├── docker-compose.yml
└── README.md
```

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone <repo-url>
cd easy-class-timetable

# 复制环境变量
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 app/config.py 中的 DATABASE_URL

# 运行
uvicorn main:app --reload --port 8000
```

#### 数据库
```bash
#完全重置（删除数据卷）

# 停止所有容器
docker-compose down

# 删除数据库数据卷
docker volume rm easy-class-timetable_mysql_data

# 重新启动（会自动初始化数据库）
docker-compose up -d
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建
npm run build
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 机构管理员 | org_admin | org123 |

## API 接口

### 认证
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 资源管理
- `GET/POST/PUT/DELETE /api/v1/classrooms` - 教室管理
- `GET/POST/PUT/DELETE /api/v1/teachers` - 教师管理
- `GET/POST/PUT/DELETE /api/v1/students` - 学生管理
- `GET/POST/PUT/DELETE /api/v1/courses` - 课程管理

### 排课
- `GET/POST /api/v1/cycles` - 排课周期
- `GET/POST /api/v1/schedule` - 课表管理
- `POST /api/v1/schedule/check-conflict` - 冲突检测

### 其他
- `GET /api/v1/exports/pdf` - 导出 PDF
- `GET /api/v1/exports/excel` - 导出 Excel
- `POST /api/v1/checkins` - 课程盘点

完整 API 文档请访问 `/docs` 端点。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库连接 | mysql+pymysql://timetable:timetable123@mysql:3306/timetable |
| JWT_SECRET | JWT 密钥 | dev-secret-key-2024 |
| JWT_EXPIRE_HOURS | Token 过期时间 | 24 |

## 许可证

MIT License