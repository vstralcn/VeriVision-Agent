# Deepfake 图像检测溯源平台

融合大模型智能体与可信计算的 AI 图片鉴伪与溯源系统

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 18+ (用于前端开发)
- Python 3.10+ (用于后端开发)

### 一键部署

```bash  
# 克隆仓库
cd deepfake-detection-platform

# 使用 Docker 启动后端和数据库
docker-compose up -d

# 安装并启动前端
cd frontend
npm install
npm run dev
```

应用程序将在以下地址可用：
- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📋 默认账号

### 管理员账号
- **邮箱**: admin@example.com
- **密码**: admin123
- **权限**: 完整系统访问权限，包括管理员面板

### 普通用户账号
- **邮箱**: user@example.com
- **密码**: user123
- **权限**: 标准用户功能

## 🏗️ 项目结构

```
deepfake-detection-platform/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 端点
│   │   │   ├── auth.py        # 认证
│   │   │   ├── detection.py   # 检测操作
│   │   │   ├── admin.py       # 管理员操作
│   │   │   └── user.py        # 用户操作
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 设置
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── security.py    # JWT 和密码哈希
│   │   ├── models/            # SQLAlchemy 模型
│   │   │   └── models.py      # 数据库模型
│   │   ├── schemas/           # Pydantic 模式
│   │   │   └── schemas.py     # 请求/响应模式
│   │   ├── services/          # 业务逻辑
│   │   │   └── detection_service.py  # 检测服务
│   │   └── main.py            # FastAPI 应用程序
│   ├── alembic/               # 数据库迁移
│   ├── uploads/               # 上传的文件
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile            # 后端 Docker 镜像
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── api/              # API 客户端
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── router/           # Vue Router
│   │   ├── views/            # 页面组件
│   │   │   ├── user/         # 用户页面
│   │   │   └── admin/        # 管理员页面
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 入口点
│   ├── package.json          # Node 依赖
│   └── vite.config.js        # Vite 配置
├── docker-compose.yml        # Docker Compose 配置
└── README.md                 # 本文件
```

## 🔧 详细设置

### 后端设置

#### 使用 Docker（推荐）

```bash
# 启动 PostgreSQL 和后端
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

#### 手动设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL="postgresql://deepfake_user:deepfake_pass@localhost:5432/deepfake_db"
export SECRET_KEY="your-secret-key-change-in-production"

# 运行数据库迁移
alembic upgrade head

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🎯 功能特性

### 用户功能

1. **仪表盘**
   - 系统概览
   - 最近检测历史
   - 快速访问检测工作台

2. **检测工作台**
   - 图片上传（拖放或文件选择）
   - 实时 Deepfake 检测
   - 可视化热力图显示操纵区域
   - 智能分析报告包含：
     - 判定结果（伪造/真实）
     - 置信度分数
     - 风险等级评估
     - 详细分析指标
     - 建议
   - 可信认证包含：
     - 唯一认证 ID
     - SHA256 哈希
     - 感知哈希（pHash）
     - 加密签名
     - 签名验证

3. **溯源档案**
   - 查看图片指纹历史
   - 操作时间线
   - 认证验证
   - 完整审计追踪

4. **个人中心**
   - 个人资料管理
   - 检测历史
   - 统计概览

### 管理员功能

1. **管理员仪表盘**
   - 今日检测数量
   - 伪造检测比率
   - 用户统计
   - 系统概览

2. **用户管理**
   - 查看所有用户
   - 启用/禁用用户账户
   - 查看用户检测统计

3. **审计日志**
   - 完整系统审计追踪
   - 按操作、状态、日期范围筛选
   - 详细日志检查
   - 合规监控

## 🔌 API 端点

### 认证
- `POST /api/auth/register` - 注册新用户
- `POST /api/auth/login` - 登录并获取 JWT 令牌
- `GET /api/auth/me` - 获取当前用户信息

### 检测
- `POST /api/detection/upload` - 上传并检测图片
- `GET /api/detection/history` - 获取检测历史
- `GET /api/detection/recent` - 获取最近检测
- `GET /api/detection/{id}` - 获取检测详情
- `GET /api/detection/{id}/trace` - 获取追踪记录
- `POST /api/detection/{id}/verify` - 验证认证

### 用户
- `GET /api/user/me` - 获取用户资料
- `PUT /api/user/me` - 更新用户资料

### 管理员（需要管理员角色）
- `GET /api/admin/dashboard/stats` - 获取仪表盘统计
- `GET /api/admin/users` - 获取所有用户
- `PUT /api/admin/users/{id}/toggle-active` - 启用/禁用用户
- `GET /api/admin/audit-logs` - 获取审计日志（带筛选）
- `GET /api/admin/audit-logs/{id}` - 获取审计日志详情

## 🗄️ 数据库架构

### 用户表（Users）
- 用户认证和个人资料信息
- 基于角色的访问控制（用户/管理员）
- 账户状态管理

### 检测表（Detections）
- 检测结果和元数据
- 图片和热力图路径
- 分析报告
- 可信认证数据
- 图片指纹（SHA256、pHash）

### 追踪记录表（Trace Records）
- 每次检测的完整审计追踪
- 操作历史（上传、检测、验证）
- 每个操作的元数据

### 审计日志表（Audit Logs）
- 系统级审计日志
- 用户操作追踪
- 安全和合规监控

## 🔐 安全特性

1. **JWT 认证**
   - 安全的基于令牌的认证
   - 可配置的令牌过期时间

2. **密码哈希**
   - Bcrypt 密码哈希
   - 安全的密码存储

3. **基于角色的访问控制**
   - 用户和管理员角色
   - 受保护的管理员端点

4. **可信认证**
   - 加密签名
   - 图片指纹（SHA256、pHash）
   - 签名验证

5. **审计日志**
   - 完整的操作追踪
   - 安全事件监控

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行测试（实现后）
pytest

# 检查代码覆盖率
pytest --cov=app
```

### 前端测试

```bash
cd frontend

# 运行单元测试（实现后）
npm run test

# 运行端到端测试
npm run test:e2e
```

## 🐳 Docker 命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 重建镜像
docker-compose build

# 删除卷（警告：删除数据库）
docker-compose down -v
```

## 🔧 环境变量

### 后端（.env）

```env
DATABASE_URL=postgresql://deepfake_user:deepfake_pass@postgres:5432/deepfake_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端

前端使用 `vite.config.js` 中的 Vite 代理配置连接到后端。

## 📊 数据库初始化

数据库在首次启动时自动初始化：

1. 使用 SQLAlchemy 模型创建表
2. 创建默认管理员和用户账户
3. 应用 Alembic 迁移

重置数据库：

```bash
# 停止服务
docker-compose down -v

# 启动服务（将重新初始化）
docker-compose up -d
```

## 🚨 故障排除

### 后端无法启动

1. 检查 PostgreSQL 是否运行：
   ```bash
   docker-compose ps
   ```

2. 检查后端日志：
   ```bash
   docker-compose logs backend
   ```

3. 验证数据库连接：
   ```bash
   docker-compose exec postgres psql -U deepfake_user -d deepfake_db
   ```

### 前端无法连接到后端

1. 验证后端在 8000 端口运行
2. 检查 `vite.config.js` 中的 Vite 代理配置
3. 检查浏览器控制台的 CORS 错误

### 数据库迁移问题

```bash
# 重置迁移
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

## 📝 开发说明

### 模拟检测服务

当前实现使用**模拟检测服务**生成随机结果。这是为了 MVP 演示目的而设计的。

要集成真实的 Deepfake 检测模型：
1. 查看 [MODEL_DEPLOY.md](docs/MODEL_DEPLOY.md) 获取详细说明
2. 替换 `backend/app/services/detection_service.py` 中的模拟实现
3. 服务接口设计为可插拔的

### 添加新功能

1. **后端**：在 `backend/app/api/` 中添加新端点
2. **前端**：在 `frontend/src/views/` 中添加新页面
3. **数据库**：为架构更改创建 Alembic 迁移

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 提交拉取请求

## 📄 许可证

本项目用于教育和演示目的。

## 🔗 相关文档

- [MODEL_DEPLOY.md](docs/MODEL_DEPLOY.md) - 模型部署指南
- [API 文档](http://localhost:8000/docs) - 交互式 API 文档（运行时）

## 📞 支持

如有问题和疑问：
- 查看上面的故障排除部分
- 查看 `/docs` 的 API 文档
- 检查 Docker 日志以获取错误消息

---

**使用 FastAPI、Vue 3 和 Element Plus 构建 ❤️**
