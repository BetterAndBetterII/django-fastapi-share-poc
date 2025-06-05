import pytest
import base64
import pickle
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app, get_django_session_data


client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """测试健康检查"""
    with patch('main.redis_client') as mock_redis, \
         patch('main.database') as mock_db:
        mock_redis.ping.return_value = True
        mock_db.fetch_one.return_value = [1]
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_get_user_unauthenticated():
    """测试未认证用户访问用户API"""
    response = client.get("/api/user")
    assert response.status_code == 401


def test_get_user_authenticated():
    """测试已认证用户访问用户API"""
    # 创建模拟session数据
    session_data = {
        '_auth_user_id': '1',
        '_auth_user_username': 'testuser',
        '_auth_user_email': 'test@example.com'
    }
    
    # 序列化并编码session数据
    pickled = pickle.dumps(session_data)
    encoded = base64.b64encode(pickled)
    
    # 模拟Redis返回session数据
    with patch('main.redis_client.get', return_value=encoded), \
         patch('main.database.fetch_one', return_value={"id": 1, "username": "testuser", "email": "test@example.com"}):
        
        response = client.get("/api/user", cookies={
            "shared_session_id": "fake_session_id"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"


def test_get_django_session_data():
    """测试解析Django session数据"""
    # 创建模拟session数据
    session_data = {
        '_auth_user_id': '1',
        '_auth_user_username': 'testuser',
        '_auth_user_email': 'test@example.com'
    }
    
    # 序列化并编码session数据
    pickled = pickle.dumps(session_data)
    encoded = base64.b64encode(pickled)
    
    # 模拟Redis返回session数据
    with patch('main.redis_client.get', return_value=encoded):
        result = get_django_session_data("fake_session_id")
        
        assert result is not None
        assert result['_auth_user_id'] == '1'
        assert result['_auth_user_username'] == 'testuser'
        assert result['_auth_user_email'] == 'test@example.com'


def test_get_session():
    """测试获取session信息"""
    # 创建模拟session数据
    session_data = {
        '_auth_user_id': '1',
        '_auth_user_username': 'testuser',
        '_auth_user_email': 'test@example.com'
    }
    
    # 序列化并编码session数据
    pickled = pickle.dumps(session_data)
    encoded = base64.b64encode(pickled)
    
    # 模拟Redis返回session数据
    with patch('main.redis_client.get', return_value=encoded):
        response = client.get("/api/session", cookies={
            "shared_session_id": "fake_session_id"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "session_data" in data
        assert data["session_data"]["_auth_user_id"] == '1'

