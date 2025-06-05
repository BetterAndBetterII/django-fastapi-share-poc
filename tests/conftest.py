import os
import pytest
import requests
import time
from urllib.parse import urljoin


# 服务URL
DJANGO_URL = os.environ.get("DJANGO_URL", "http://django_app:8000")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://fastapi_app:8001")


@pytest.fixture(scope="session")
def wait_for_services():
    """等待所有服务启动"""
    services = [
        {"name": "Django", "url": f"{DJANGO_URL}/admin/login/"},
        {"name": "FastAPI", "url": f"{FASTAPI_URL}/health"}
    ]
    
    max_retries = 30
    retry_interval = 2
    
    for service in services:
        for i in range(max_retries):
            try:
                response = requests.get(service["url"], timeout=5)
                if response.status_code < 500:
                    print(f"{service['name']} is ready!")
                    break
            except requests.RequestException:
                pass
            
            print(f"Waiting for {service['name']}... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
        else:
            pytest.fail(f"{service['name']} did not become ready in time")


@pytest.fixture(scope="session")
def django_client(wait_for_services):
    """Django客户端"""
    class DjangoClient:
        def __init__(self):
            self.base_url = DJANGO_URL
            self.session = requests.Session()
        
        def get(self, path, **kwargs):
            url = urljoin(self.base_url, path)
            return self.session.get(url, **kwargs)
        
        def post(self, path, **kwargs):
            url = urljoin(self.base_url, path)
            return self.session.post(url, **kwargs)
        
        def register(self, username, email, password):
            """注册新用户"""
            csrf_response = self.get("/register/")
            csrf_token = None
            
            # 从响应中提取CSRF令牌
            for cookie in self.session.cookies:
                if cookie.name == "csrftoken":
                    csrf_token = cookie.value
                    break
            
            if not csrf_token:
                raise ValueError("Could not extract CSRF token")
            
            data = {
                "username": username,
                "email": email,
                "password1": password,
                "password2": password,
                "csrfmiddlewaretoken": csrf_token
            }
            
            headers = {
                "Referer": f"{self.base_url}/register/"
            }
            
            return self.post("/register/", data=data, headers=headers)
        
        def login(self, username, password):
            """登录用户"""
            csrf_response = self.get("/login/")
            csrf_token = None
            
            # 从响应中提取CSRF令牌
            for cookie in self.session.cookies:
                if cookie.name == "csrftoken":
                    csrf_token = cookie.value
                    break
            
            if not csrf_token:
                raise ValueError("Could not extract CSRF token")
            
            data = {
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": csrf_token
            }
            
            headers = {
                "Referer": f"{self.base_url}/login/"
            }
            
            return self.post("/login/", data=data, headers=headers)
        
        def logout(self):
            """登出用户"""
            return self.get("/logout/")
        
        def get_user_data(self):
            """获取用户数据"""
            return self.get("/api/user/")
    
    return DjangoClient()


@pytest.fixture(scope="session")
def fastapi_client(wait_for_services):
    """FastAPI客户端"""
    class FastAPIClient:
        def __init__(self):
            self.base_url = FASTAPI_URL
            self.session = requests.Session()
        
        def get(self, path, **kwargs):
            url = urljoin(self.base_url, path)
            return self.session.get(url, **kwargs)
        
        def post(self, path, **kwargs):
            url = urljoin(self.base_url, path)
            return self.session.post(url, **kwargs)
        
        def get_user_data(self):
            """获取用户数据"""
            return self.get("/api/user")
        
        def get_session_data(self):
            """获取session数据"""
            return self.get("/api/session")
    
    return FastAPIClient()

