# Django与FastAPI共享Redis Session认证

这个项目是一个概念验证（Proof of Concept），用于验证Django和FastAPI应用可以通过共享Redis存储的session数据来实现统一的用户认证机制。

## 项目目标

- 验证Django和FastAPI可以共享同一个Redis存储的session数据
- 实现用户在任一服务登录后，可以无缝访问另一个服务
- 确保两个框架可以正确解析和验证对方创建的认证信息
- 提供完整的测试套件，验证共享认证机制的可靠性
- 通过Docker容器化应用，便于部署和测试
- 配置GitHub Actions自动化测试和发布Docker镜像到GHCR

## 项目结构

```
.
├── django_app/            # Django应用
│   ├── auth_app/          # Django认证应用
│   ├── shared_auth_project/ # Django项目配置
│   └── templates/         # Django模板
├── fastapi_app/           # FastAPI应用
│   ├── main.py            # FastAPI主应用
│   └── test_main.py       # FastAPI测试
├── tests/                 # 集成测试
│   ├── conftest.py        # 测试配置
│   └── integration/       # 集成测试用例
├── docker/                # Docker相关配置
│   ├── django.Dockerfile  # Django Docker配置
│   ├── fastapi.Dockerfile # FastAPI Docker配置
│   └── tests.Dockerfile   # 测试 Docker配置
├── .github/workflows/     # GitHub Actions工作流配置
│   └── ci-cd.yml          # CI/CD工作流
├── .env.example           # 环境变量示例
├── docker-compose.yml     # Docker Compose配置
├── Makefile               # 常用命令快捷方式
├── DESIGN.md              # 技术设计文档
└── README.md              # 项目说明文档
```

## 技术栈

- **Django 4.2.10**: Web框架，用于构建传统的服务端渲染应用
- **FastAPI 0.104.1**: 现代化的API框架，用于构建高性能API
- **Redis 7.2**: 用于存储共享的session数据
- **PostgreSQL 15**: 数据库，用于存储用户数据
- **Docker & Docker Compose**: 容器化应用，便于部署和测试
- **GitHub Actions**: 自动化测试和构建流程
- **GHCR (GitHub Container Registry)**: 存储Docker镜像

## 快速开始

### 前提条件

- Docker 和 Docker Compose
- Git

### 本地开发

1. 克隆仓库
```bash
git clone https://github.com/BetterAndBetterII/SimpleRAG.git
cd SimpleRAG
```

2. 创建环境变量文件
```bash
cp .env.example .env
# 根据需要编辑.env文件
```

3. 使用Docker Compose启动服务
```bash
docker-compose up -d
```

4. 创建超级用户（可选）
```bash
make create-superuser
# 或者
docker-compose exec django_app python manage.py createsuperuser
```

5. 访问服务
   - Django应用: http://localhost:8000
   - Django管理界面: http://localhost:8000/admin/
   - FastAPI应用: http://localhost:8001
   - FastAPI文档: http://localhost:8001/docs

### 使用Makefile

项目提供了Makefile来简化常用命令：

```bash
# 启动所有服务
make up

# 停止所有服务
make down

# 构建所有服务
make build

# 运行测试
make test

# 进入Django应用的shell
make django-shell

# 进入FastAPI应用的shell
make fastapi-shell

# 运行Django数据库迁移
make migrate

# 创建Django超级用户
make create-superuser

# 清理临时文件和缓存
make clean
```

### 测试

运行测试套件：
```bash
docker-compose run --rm tests
# 或者
make test
```

## 工作原理

### 共享认证机制

1. **共享Redis存储**: 两个应用使用相同的Redis实例和相同的键前缀
2. **统一Session格式**: FastAPI应用能够解析Django创建的session数据
3. **共享Cookie**: 两个应用使用相同的cookie名称（shared_session_id）
4. **共享用户数据**: FastAPI可以访问Django的用户数据库

### 认证流程

1. 用户在Django应用中登录
2. Django将认证信息存储在Redis中，并设置cookie
3. 用户访问FastAPI应用时，FastAPI读取相同的cookie
4. FastAPI从Redis中获取session数据，并验证用户身份
5. 如果验证成功，FastAPI允许用户访问受保护的资源

### 关键技术点

- **Django Session序列化**: Django使用pickle序列化和base64编码存储session数据
- **FastAPI解析Django Session**: FastAPI使用相同的方法解码session数据
- **共享数据库**: 两个应用访问相同的PostgreSQL数据库，共享用户数据

## 部署

### 使用Docker Compose

对于生产环境，建议修改环境变量：

1. 编辑`.env`文件，设置安全的密钥和生产环境配置
2. 启动服务：`docker-compose up -d`

### 使用GitHub Actions和GHCR

项目配置了GitHub Actions工作流，可以自动测试和发布Docker镜像到GHCR：

1. 推送代码到GitHub仓库的main分支
2. GitHub Actions会自动运行测试
3. 如果测试通过，会构建Docker镜像并发布到GHCR
4. 可以使用以下命令拉取镜像：
   ```bash
   docker pull ghcr.io/betterandbetterii/simplerag/django-app:latest
   docker pull ghcr.io/betterandbetterii/simplerag/fastapi-app:latest
   ```

## 安全考虑

- 在生产环境中，请确保使用安全的密钥
- 启用HTTPS，并将cookie设置为secure
- 考虑设置共享的cookie域，以便在不同子域之间共享认证
- 定期轮换密钥和凭据

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT

