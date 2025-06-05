import pytest
import time
import uuid
import json
import requests


def test_full_auth_flow(django_client, fastapi_client):
    """测试完整的认证流程"""
    # 生成唯一的用户名，避免测试冲突
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    # 1. 注册新用户
    register_response = django_client.register(username, email, password)
    assert register_response.status_code in [200, 302], "注册失败"
    
    # 2. 登录用户
    login_response = django_client.login(username, password)
    assert login_response.status_code in [200, 302], "登录失败"
    
    # 3. 获取Django用户数据
    django_user_response = django_client.get_user_data()
    assert django_user_response.status_code == 200, "获取Django用户数据失败"
    
    # 4. 将Django的cookies复制到FastAPI客户端
    cookies = django_client.session.cookies.get_dict()
    session_id = cookies.get("shared_session_id")
    assert session_id, "未找到session ID"
    
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 5. 获取FastAPI用户数据
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 200, "获取FastAPI用户数据失败"
    
    fastapi_user_data = fastapi_user_response.json()
    assert fastapi_user_data["username"] == username, "FastAPI返回的用户名不匹配"
    
    # 6. 登出用户
    logout_response = django_client.logout()
    assert logout_response.status_code in [200, 302], "登出失败"
    
    # 7. 更新cookies
    cookies = django_client.session.cookies.get_dict()
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 8. 尝试访问FastAPI用户数据，应该失败
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 401, "登出后仍能访问FastAPI用户数据"
    
    # 9. 再次登录
    login_response = django_client.login(username, password)
    assert login_response.status_code in [200, 302], "再次登录失败"
    
    # 10. 更新cookies
    cookies = django_client.session.cookies.get_dict()
    for name, value in cookies.items():
        fastapi_client.session.cookies.set(name, value)
    
    # 11. 再次获取FastAPI用户数据
    fastapi_user_response = fastapi_client.get_user_data()
    assert fastapi_user_response.status_code == 200, "再次登录后获取FastAPI用户数据失败"


def test_session_persistence(django_client, fastapi_client):
    """测试session持久性"""
    # 生成唯一的用户名，避免测试冲突
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    # 注册并登录用户
    django_client.register(username, email, password)
    django_client.login(username, password)
    
    # 获取session ID
    cookies = django_client.session.cookies.get_dict()
    session_id = cookies.get("shared_session_id")
    assert session_id, "未找到session ID"
    
    # 创建新的客户端，模拟新的浏览器会话
    new_django_client = requests.Session()
    new_fastapi_client = requests.Session()
    
    # 设置相同的session ID
    new_django_client.cookies.set("shared_session_id", session_id)
    new_fastapi_client.cookies.set("shared_session_id", session_id)
    
    # 尝试访问Django用户数据
    django_response = new_django_client.get(f"{django_client.base_url}/profile/")
    assert django_response.status_code == 200, "使用相同session ID无法访问Django用户数据"
    assert username in django_response.text, "Django响应中未找到用户名"
    
    # 尝试访问FastAPI用户数据
    fastapi_response = new_fastapi_client.get(f"{fastapi_client.base_url}/api/user")
    assert fastapi_response.status_code == 200, "使用相同session ID无法访问FastAPI用户数据"
    
    fastapi_data = fastapi_response.json()
    assert fastapi_data["username"] == username, "FastAPI返回的用户名不匹配"

