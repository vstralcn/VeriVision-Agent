# 快速开始指南

## 🚀 一键启动

```bash
./start.sh
```

此脚本将：
1. 使用 Docker 启动后端和数据库
2. 等待服务就绪
3. 可选择安装并启动前端

## 📋 手动设置

### 后端 + 数据库

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查状态
docker-compose ps
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 🌐 访问应用程序

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 👤 默认登录凭据

### 管理员账号
- 邮箱：`admin@example.com`
- 密码：`admin123`

### 普通用户账号
- 邮箱：`user@example.com`
- 密码：`user123`

## 🛠️ 开发命令

使用 `dev.sh` 辅助脚本：

```bash
./dev.sh help           # 显示所有命令
./dev.sh start          # 启动服务
./dev.sh stop           # 停止服务
./dev.sh logs           # 查看后端日志
./dev.sh shell          # 打开后端 shell
./dev.sh db-shell       # 打开数据库 shell
./dev.sh status         # 显示服务状态
```

## 🧪 测试平台

1. **登录**：使用管理员或用户凭据
2. **上传图片**：进入检测工作台
3. **查看结果**：查看热力图、分析报告和认证
4. **检查溯源**：查看图片的审计追踪
5. **管理员面板**：以管理员身份登录访问管理功能

## 🐛 故障排除

### 后端无法启动
```bash
docker-compose logs backend
```

### 数据库连接问题
```bash
docker-compose ps
docker-compose restart postgres
```

### 重置所有内容
```bash
docker-compose down -v
docker-compose up -d
```

## 📚 更多信息

- 查看 [README.md](../README_CN.md) 获取完整文档
- 查看 [MODEL_DEPLOY.md](MODEL_DEPLOY_CN.md) 了解模型集成
- 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE_CN.md) 了解架构详情
