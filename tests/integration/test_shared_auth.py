import pytest
import time
import uuid
import json


def test_django_login_fastapi_access(django_client, fastapi_client):
    """测试在Django登录后，可以通过FastAPI访问用户数据"""
    # 生成唯一的用户名，避免测试冲突
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    # 注册新用户
    register_response = django_client.register(username, email, password)
    assert register_response.status_code in [200, 302], "注册失败"
    
    # 登录用户
    login_response = django_client.login(username, password)
    assert login_response.status_code in [200, 302], "登录失败"
    
    # 获取Django用户数据
    django_user_response = django_client.get_user_data()
    assert django_user_response.status_code == 200, "获取Django用户数据失败"
    
    try:
        django_user_data = django_user_response.json()
    except json.JSONDecodeError:
        # 如果不是JSON响应，可能是HTML页面
        django_user_data = {"username": username}
    
    # 确认用户已登录
    assert username in django_user_response.text, "Django响应中未找到用户名"
    
    # 等待session数据同步到Redis
    time.sleep(1)
    
    # 使用相同的session访问FastAPI
    cookies = django_client.session.cookies.get_dict()
    session_id = cookies.get("shared_session_id")
    assert session_id, "未找到session ID"
    
    # 将Django的cookies复制到FastAPI客户端
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 获取FastAPI用户数据
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 200, "获取FastAPI用户数据失败"
    
    fastapi_user_data = fastapi_user_response.json()
    assert fastapi_user_data["username"] == username, "FastAPI返回的用户名不匹配"
    assert fastapi_user_data["email"] == email, "FastAPI返回的邮箱不匹配"
    
    # 获取FastAPI session数据
    session_response = fastapi_client.get_session_data()
    assert session_response.status_code == 200, "获取session数据失败"
    
    session_data = session_response.json()
    assert session_data["session_id"] == session_id, "Session ID不匹配"
    assert "_auth_user_id" in session_data["session_data"], "Session数据中未找到用户ID"


def test_django_logout_fastapi_access(django_client, fastapi_client):
    """测试在Django登出后，无法通过FastAPI访问用户数据"""
    # 生成唯一的用户名，避免测试冲突
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    # 注册新用户
    register_response = django_client.register(username, email, password)
    assert register_response.status_code in [200, 302], "注册失败"
    
    # 登录用户
    login_response = django_client.login(username, password)
    assert login_response.status_code in [200, 302], "登录失败"
    
    # 将Django的cookies复制到FastAPI客户端
    cookies = django_client.session.cookies.get_dict()
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 确认可以访问FastAPI用户数据
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 200, "获取FastAPI用户数据失败"
    
    # 登出用户
    logout_response = django_client.logout()
    assert logout_response.status_code in [200, 302], "登出失败"
    
    # 将Django的cookies复制到FastAPI客户端
    cookies = django_client.session.cookies.get_dict()
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 尝试访问FastAPI用户数据，应该失败
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 401, "登出后仍能访问FastAPI用户数据"

