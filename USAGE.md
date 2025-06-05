# 使用说明

本文档详细说明如何安装、配置和使用Django与FastAPI共享Redis Session认证系统。

## 目录

1. [安装](#安装)
2. [配置](#配置)
3. [使用方法](#使用方法)
4. [测试](#测试)
5. [常见问题](#常见问题)
6. [故障排除](#故障排除)

## 安装

### 前提条件

- Docker 19.03+
- Docker Compose 1.27+
- Git

### 步骤

1. 克隆仓库

```bash
git clone https://github.com/BetterAndBetterII/SimpleRAG.git
cd SimpleRAG
```

2. 创建环境变量文件

```bash
cp .env.example .env
```

3. 构建Docker镜像

```bash
docker-compose build
```

4. 启动服务

```bash
docker-compose up -d
```

5. 运行数据库迁移

```bash
docker-compose exec django_app python manage.py migrate
```

6. 创建超级用户（可选）

```bash
docker-compose exec django_app python manage.py createsuperuser
```

## 配置

### 环境变量

项目使用环境变量进行配置。以下是可用的环境变量及其默认值：

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| DEBUG | 1 | 调试模式（1=开启，0=关闭） |
| DJANGO_SECRET_KEY | django_secret_key_for_development | Django密钥 |
| FASTAPI_SECRET_KEY | fastapi_secret_key_for_development | FastAPI密钥 |
| POSTGRES_USER | postgres | PostgreSQL用户名 |
| POSTGRES_PASSWORD | postgres | PostgreSQL密码 |
| POSTGRES_DB | shared_auth_db | PostgreSQL数据库名 |
| POSTGRES_HOST | postgres | PostgreSQL主机 |
| POSTGRES_PORT | 5432 | PostgreSQL端口 |
| REDIS_HOST | redis | Redis主机 |
| REDIS_PORT | 6379 | Redis端口 |
| REDIS_DB | 0 | Redis数据库索引 |
| DOCKER_REGISTRY | ghcr.io | Docker镜像仓库 |
| DOCKER_NAMESPACE | betterandbetterii/simplerag | Docker命名空间 |
| TAG | latest | Docker镜像标签 |

### Django配置

Django应用的主要配置在`django_app/shared_auth_project/settings.py`文件中。以下是与共享认证相关的关键配置：

```python
# Redis Session配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Redis缓存配置
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PREFIX": "shared_session:",
        }
    }
}

# Session配置
SESSION_COOKIE_NAME = "shared_session_id"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_DOMAIN = None  # 在生产环境中设置为共享域名
SESSION_COOKIE_SECURE = False  # 在生产环境中设置为True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### FastAPI配置

FastAPI应用的主要配置在`fastapi_app/main.py`文件中。以下是与共享认证相关的关键配置：

```python
# 配置Redis
redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url, decode_responses=False)
session_cookie_name = "shared_session_id"
session_prefix = "shared_session:"
```

## 使用方法

### Django应用

1. 访问Django应用：http://localhost:8000
2. 注册新用户：http://localhost:8000/register/
3. 登录：http://localhost:8000/login/
4. 查看个人资料：http://localhost:8000/profile/
5. 登出：http://localhost:8000/logout/

### FastAPI应用

1. 访问FastAPI应用：http://localhost:8001
2. 查看API文档：http://localhost:8001/docs
3. 获取用户数据：http://localhost:8001/api/user
4. 获取session数据：http://localhost:8001/api/session
5. 健康检查：http://localhost:8001/health

### 共享认证流程

1. 在Django应用中注册并登录
2. 访问FastAPI的用户API：http://localhost:8001/api/user
3. 如果认证成功，将看到用户数据
4. 在Django应用中登出
5. 再次访问FastAPI的用户API，将收到401未授权错误

## 测试

### 运行测试

```bash
# 运行所有测试
docker-compose run --rm tests

# 运行特定测试文件
docker-compose run --rm tests pytest -xvs integration/test_shared_auth.py

# 运行特定测试函数
docker-compose run --rm tests pytest -xvs integration/test_shared_auth.py::test_django_login_fastapi_access
```

### 测试覆盖范围

1. **单元测试**
   - Django应用：`django_app/auth_app/tests.py`
   - FastAPI应用：`fastapi_app/test_main.py`

2. **集成测试**
   - 共享认证：`tests/integration/test_shared_auth.py`
   - 端到端流程：`tests/integration/test_e2e.py`

## 常见问题

### 1. 为什么选择Redis作为session存储？

Redis是一个高性能的内存数据库，适合存储session数据。它支持数据持久化，可以在服务重启后恢复session数据。此外，Redis可以轻松地在多个服务之间共享，这对于实现共享认证至关重要。

### 2. Django和FastAPI如何共享session数据？

Django使用pickle序列化和base64编码存储session数据。FastAPI应用使用相同的方法解码session数据，从而实现共享认证。

### 3. 如何在生产环境中部署？

对于生产环境，建议：
- 使用安全的密钥
- 启用HTTPS
- 设置SESSION_COOKIE_SECURE=True
- 设置共享的SESSION_COOKIE_DOMAIN
- 使用环境变量管理敏感信息

### 4. 如何添加更多的服务？

要添加更多服务，需要：
1. 确保新服务可以访问相同的Redis实例
2. 实现相同的session解析逻辑
3. 使用相同的cookie名称（shared_session_id）

## 故障排除

### 无法连接到Redis

**症状**：服务启动失败，出现Redis连接错误。

**解决方案**：
1. 确保Redis服务正在运行：`docker-compose ps`
2. 检查Redis配置：`docker-compose exec redis redis-cli ping`
3. 验证环境变量：`docker-compose config`

### 认证失败

**症状**：在一个服务中登录后，无法在另一个服务中访问受保护的资源。

**解决方案**：
1. 检查cookie是否正确设置：使用浏览器开发者工具查看cookie
2. 验证Redis中的session数据：`docker-compose exec redis redis-cli keys "shared_session:*"`
3. 检查session解析逻辑：查看FastAPI的`get_django_session_data`函数

### 数据库迁移失败

**症状**：Django数据库迁移失败。

**解决方案**：
1. 检查数据库连接：`docker-compose exec django_app python manage.py dbshell`
2. 重置迁移：
   ```bash
   docker-compose exec django_app python manage.py migrate auth zero
   docker-compose exec django_app python manage.py migrate
   ```

