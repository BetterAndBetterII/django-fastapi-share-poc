# 技术设计方案

## 概述

本文档详细说明Django和FastAPI应用如何共享Redis存储的session数据，实现统一的用户认证机制。

## 技术挑战

Django和FastAPI是两个不同的Web框架，它们处理session和认证的方式有所不同：

1. **序列化格式差异**：Django使用自己的序列化格式存储session，而FastAPI通常使用JSON
2. **Cookie处理方式**：两个框架处理cookies的方式不同
3. **认证机制**：Django有内置的认证系统，而FastAPI需要自定义认证逻辑

## 解决方案

### 1. 共享Redis配置

两个应用将使用相同的Redis实例，并配置相同的键前缀和序列化方式：

```python
# Django配置
SESSION_ENGINE = "django.contrib.sessions.backends.redis"
SESSION_REDIS = {
    'host': 'redis',
    'port': 6379,
    'db': 0,
    'prefix': 'shared_session:',
    'socket_timeout': 1
}
SESSION_COOKIE_NAME = "shared_session_id"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_DOMAIN = None  # 在生产环境中设置为共享域名
SESSION_COOKIE_SECURE = False  # 在生产环境中设置为True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

```python
# FastAPI配置
redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)
session_cookie_name = "shared_session_id"
session_prefix = "shared_session:"
```

### 2. 统一Session序列化格式

为了确保两个框架可以正确解析对方的session数据，我们将使用统一的序列化格式。有两种方案：

#### 方案A：使用Django的序列化格式（推荐）

FastAPI将使用Django的session序列化格式，这样可以直接读取Django创建的session：

```python
# FastAPI中解析Django session
def get_django_session_data(session_key):
    session_data = redis_client.get(f"{session_prefix}{session_key}")
    if not session_data:
        return None
    
    # Django使用base64编码和pickle序列化
    try:
        decoded = base64.b64decode(session_data)
        session_dict = pickle.loads(decoded)
        return session_dict
    except Exception as e:
        logger.error(f"Failed to decode Django session: {e}")
        return None
```

#### 方案B：使用JSON序列化

两个框架都使用JSON序列化格式，这需要修改Django的默认行为：

```python
# Django自定义session序列化
class JSONSerializer:
    def dumps(self, obj):
        return json.dumps(obj).encode('utf-8')
    
    def loads(self, data):
        return json.loads(data.decode('utf-8'))

# 在Django设置中
SESSION_SERIALIZER = 'path.to.JSONSerializer'
```

### 3. 共享认证机制

我们将实现一个共享的认证机制，确保两个框架可以验证对方创建的session：

```python
# Django中验证session
def validate_session(request):
    session_key = request.COOKIES.get(SESSION_COOKIE_NAME)
    if not session_key:
        return None
    
    # 验证session并获取用户
    session = SessionStore(session_key)
    user_id = session.get('_auth_user_id')
    if not user_id:
        return None
    
    return get_user_model().objects.get(pk=user_id)
```

```python
# FastAPI中验证session
async def validate_session(request: Request):
    session_key = request.cookies.get(session_cookie_name)
    if not session_key:
        return None
    
    session_data = get_django_session_data(session_key)
    if not session_data or '_auth_user_id' not in session_data:
        return None
    
    # 这里需要实现获取用户的逻辑
    user_id = session_data['_auth_user_id']
    return await get_user_by_id(user_id)
```

### 4. 共享用户数据

两个应用需要访问相同的用户数据。有两种方案：

#### 方案A：共享数据库（推荐）

两个应用使用相同的数据库，FastAPI直接访问Django的用户表：

```python
# FastAPI中访问Django用户表
async def get_user_by_id(user_id: int):
    async with database.transaction():
        query = "SELECT id, username, email FROM auth_user WHERE id = :user_id"
        user = await database.fetch_one(query=query, values={"user_id": user_id})
        return user
```

#### 方案B：用户信息存储在Session中

将必要的用户信息直接存储在session中，避免FastAPI访问Django的数据库：

```python
# Django登录时存储用户信息
def login_user(request, user):
    request.session['_auth_user_id'] = str(user.id)
    request.session['_auth_user_username'] = user.username
    request.session['_auth_user_email'] = user.email
    # 其他需要的用户信息
```

```python
# FastAPI中获取用户信息
async def get_current_user(request: Request):
    session_key = request.cookies.get(session_cookie_name)
    if not session_key:
        return None
    
    session_data = get_django_session_data(session_key)
    if not session_data:
        return None
    
    return {
        "id": session_data.get('_auth_user_id'),
        "username": session_data.get('_auth_user_username'),
        "email": session_data.get('_auth_user_email')
    }
```

## 测试策略

我们将实现以下测试用例：

1. **单元测试**：测试各个组件的功能
   - Django session存储和读取
   - FastAPI session解析和验证
   - 用户认证逻辑

2. **集成测试**：测试组件之间的交互
   - Django创建session后，FastAPI能否正确读取
   - FastAPI创建session后，Django能否正确读取

3. **端到端测试**：模拟真实用户场景
   - 用户在Django应用登录后，访问FastAPI应用
   - 用户在FastAPI应用登录后，访问Django应用

## Docker配置

我们将使用Docker Compose配置以下服务：

1. **Django应用**：运行Django Web服务
2. **FastAPI应用**：运行FastAPI API服务
3. **Redis**：共享的session存储
4. **测试服务**：运行测试套件

## GitHub Actions工作流

我们将配置GitHub Actions工作流，实现以下功能：

1. **自动测试**：运行测试套件，确保代码质量
2. **构建Docker镜像**：构建应用的Docker镜像
3. **发布到GHCR**：将Docker镜像发布到GitHub Container Registry

## 安全考虑

1. **Session密钥**：确保两个应用使用相同的密钥加密session数据
2. **Cookie安全**：在生产环境中启用secure和httponly标志
3. **CSRF保护**：确保两个应用都实现了CSRF保护
4. **数据验证**：验证从session中读取的数据，防止注入攻击

## 结论

通过以上设计，我们可以实现Django和FastAPI应用共享Redis存储的session数据，从而实现统一的用户认证机制。这种方案既保留了两个框架各自的优势，又实现了无缝的用户体验。

