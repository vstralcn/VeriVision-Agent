# 项目结构文档

```
deepfake-detection-platform/
├── README_CN.md                       # 主文档（中文）
├── docker-compose.yml                 # Docker 编排配置
│
├── backend/                           # FastAPI 后端
│   ├── Dockerfile                     # 后端容器镜像
│   ├── requirements.txt               # Python 依赖
│   ├── alembic.ini                    # Alembic 配置
│   │
│   ├── alembic/                       # 数据库迁移
│   │   ├── env.py                     # 迁移环境
│   │   ├── script.py.mako             # 迁移模板
│   │   └── versions/                  # 迁移版本
│   │
│   ├── app/                           # 应用程序代码
│   │   ├── main.py                    # FastAPI 应用入口
│   │   │
│   │   ├── api/                       # API 端点
│   │   │   ├── dependencies.py        # 认证依赖
│   │   │   ├── auth.py                # 认证端点
│   │   │   ├── detection.py           # 检测端点
│   │   │   ├── admin.py               # 管理员端点
│   │   │   └── user.py                # 用户端点
│   │   │
│   │   ├── core/                      # 核心配置
│   │   │   ├── config.py              # 设置
│   │   │   ├── database.py            # 数据库连接
│   │   │   └── security.py            # JWT 和密码哈希
│   │   │
│   │   ├── models/                    # 数据库模型
│   │   │   └── models.py              # SQLAlchemy 模型
│   │   │
│   │   ├── schemas/                   # Pydantic 模式
│   │   │   └── schemas.py             # 请求/响应模式
│   │   │
│   │   ├── services/                  # 业务逻辑
│   │   │   └── detection_service.py   # 检测服务
│   │   │
│   │   └── utils/                     # 工具函数
│   │
│   └── uploads/                       # 上传的文件
│       ├── images/                    # 原始图片
│       └── heatmaps/                  # 生成的热力图
│
├── frontend/                          # Vue 3 前端
│   ├── index.html                     # HTML 入口
│   ├── package.json                   # Node 依赖
│   ├── vite.config.js                 # Vite 配置
│   │
│   └── src/                           # 源代码
│       ├── main.js                    # Vue 应用入口
│       ├── App.vue                    # 根组件
│       │
│       ├── api/                       # API 客户端
│       │   ├── axios.js               # Axios 配置
│       │   └── index.js               # API 方法
│       │
│       ├── stores/                    # Pinia 状态管理
│       │   └── auth.js                # 认证状态
│       │
│       ├── router/                    # Vue Router
│       │   └── index.js               # 路由定义
│       │
│       ├── views/                     # 页面组件
│       │   ├── Login.vue              # 登录页面
│       │   ├── Layout.vue             # 用户布局
│       │   │
│       │   ├── user/                  # 用户页面
│       │   │   ├── Dashboard.vue      # 用户仪表盘
│       │   │   ├── Detection.vue      # 检测工作台
│       │   │   ├── Traceability.vue   # 溯源档案
│       │   │   └── Profile.vue        # 用户资料
│       │   │
│       │   └── admin/                 # 管理员页面
│       │       ├── AdminLayout.vue    # 管理员布局
│       │       ├── Dashboard.vue      # 管理员仪表盘
│       │       ├── Users.vue          # 用户管理
│       │       └── Audit.vue          # 审计日志
│       │
│       ├── components/                # 可复用组件
│       └── assets/                    # 静态资源
│
└── docs/                              # 文档
    ├── QUICKSTART_CN.md               # 快速开始指南
    ├── MODEL_DEPLOY_CN.md             # 模型部署指南
    ├── DEPLOYMENT_CN.md               # 部署指南
    ├── API_CN.md                      # API 文档
    └── PROJECT_STRUCTURE_CN.md        # 本文件
```

## 文件统计摘要

- **后端 Python 文件**：18 个
- **前端 Vue/JS 文件**：15 个
- **配置文件**：12 个
- **文档文件**：9 个

**总计**：54 个文件

## 已实现的关键功能

### 后端（FastAPI）
✅ 使用 JWT 的用户认证
✅ 基于角色的访问控制（用户/管理员）
✅ 图片上传和检测
✅ 模拟检测服务（可插拔真实模型）
✅ 热力图生成
✅ 带加密签名的可信认证
✅ 图片指纹识别（SHA256、pHash）
✅ 溯源记录
✅ 审计日志
✅ 管理员仪表盘统计
✅ 用户管理
✅ 使用 Alembic 的数据库迁移

### 前端（Vue 3 + Element Plus）
✅ 带默认账号的登录页面
✅ 用户仪表盘和最近检测
✅ 带上传和可视化的检测工作台
✅ 热力图显示
✅ 智能分析报告
✅ 可信认证显示和验证
✅ 带时间线的溯源档案
✅ 用户资料管理
✅ 带统计的管理员仪表盘
✅ 用户管理界面
✅ 带筛选的审计日志查看器
✅ 使用 Element Plus 的响应式设计

### 基础设施
✅ Docker Compose 设置
✅ PostgreSQL 数据库
✅ 自动数据库初始化
✅ 默认用户创建
✅ CORS 配置
✅ 文件上传处理

### 文档
✅ 带部署说明的综合 README
✅ 模型部署指南
✅ API 文档（通过 FastAPI /docs）
✅ 项目结构文档
