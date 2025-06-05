import os
import base64
import pickle
import logging
from typing import Optional, Dict, Any

import redis
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="FastAPI Shared Auth Demo")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置Redis
redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url, decode_responses=False)
session_cookie_name = "shared_session_id"
session_prefix = "shared_session:"

# 配置数据库
database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/shared_auth_db")
database = Database(database_url)

# 用户模型
class User(BaseModel):
    id: int
    username: str
    email: str
    session_id: Optional[str] = None
    auth_backend: str = "fastapi"


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def get_django_session_data(session_key: str) -> Optional[Dict[str, Any]]:
    """从Redis获取Django session数据"""
    try:
        # 获取原始session数据
        session_data = redis_client.get(f"{session_prefix}{session_key}")
        if not session_data:
            return None
        
        # Django使用base64编码和pickle序列化
        decoded = base64.b64decode(session_data)
        session_dict = pickle.loads(decoded)
        return session_dict
    except Exception as e:
        logger.error(f"Failed to decode Django session: {e}")
        return None


async def get_current_user(request: Request) -> Optional[User]:
    """从session获取当前用户"""
    session_key = request.cookies.get(session_cookie_name)
    if not session_key:
        return None
    
    session_data = get_django_session_data(session_key)
    if not session_data or '_auth_user_id' not in session_data:
        return None
    
    user_id = session_data.get('_auth_user_id')
    
    # 从数据库获取用户信息
    try:
        query = "SELECT id, username, email FROM auth_user WHERE id = :user_id"
        user_data = await database.fetch_one(query=query, values={"user_id": user_id})
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                session_id=session_key,
                auth_backend="django"
            )
    except Exception as e:
        logger.error(f"Error fetching user from database: {e}")
    
    # 如果数据库查询失败，尝试从session获取用户信息
    if '_auth_user_username' in session_data and '_auth_user_email' in session_data:
        return User(
            id=int(user_id),
            username=session_data.get('_auth_user_username'),
            email=session_data.get('_auth_user_email'),
            session_id=session_key,
            auth_backend="django_session"
        )
    
    return None


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "FastAPI Shared Auth Demo API",
        "docs_url": "/docs",
        "django_url": "http://localhost:8000"
    }


@app.get("/api/user", response_model=User)
async def get_user(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/api/session")
async def get_session(request: Request):
    """获取session信息"""
    session_key = request.cookies.get(session_cookie_name)
    if not session_key:
        return {"session": None}
    
    session_data = get_django_session_data(session_key)
    if not session_data:
        return {"session": None}
    
    # 过滤敏感信息
    filtered_data = {k: v for k, v in session_data.items() if not k.startswith('_password')}
    return {"session_id": session_key, "session_data": filtered_data}


@app.get("/health")
async def health_check():
    """健康检查"""
    redis_status = "ok"
    db_status = "ok"
    
    # 检查Redis连接
    try:
        redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    # 检查数据库连接
    try:
        await database.fetch_one("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if redis_status == "ok" and db_status == "ok" else "unhealthy",
        "redis": redis_status,
        "database": db_status
    }

