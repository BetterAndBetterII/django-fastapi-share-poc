import os
import pytest
import requests
import time
import re
from urllib.parse import urljoin


# 服务URL
DJANGO_URL = os.environ.get("DJANGO_URL", "http://localhost:8000")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8001")


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
            print(f"Debug: Making GET request to: {url}")
            try:
                response = self.session.get(url, **kwargs)
                print(f"Debug: Response status: {response.status_code}")
                return response
            except Exception as e:
                print(f"Debug: Request failed with error: {e}")
                raise
        
        def post(self, path, **kwargs):
            url = urljoin(self.base_url, path)
            return self.session.post(url, **kwargs)
        
        def _extract_csrf_token(self, html_content):
            """从HTML内容中提取CSRF令牌"""
            # 查找CSRF令牌的正则表达式
            csrf_pattern = r'<input[^>]*name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)
            
            # 备用方法：从cookie中获取
            for cookie in self.session.cookies:
                if cookie.name == "csrftoken":
                    return cookie.value
            
            return None
        
        def register(self, username, email, password):
            """注册新用户"""
            # 先测试基本连接
            health_response = self.get("/")
            print(f"Debug: Home page status code: {health_response.status_code}")
            
            csrf_response = self.get("/register/")
            print(f"Debug: Register page status code: {csrf_response.status_code}")
            print(f"Debug: Register page content length: {len(csrf_response.text)}")
            print(f"Debug: Register page content preview: {csrf_response.text[:500]}")
            
            csrf_token = self._extract_csrf_token(csrf_response.text)
            
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
            csrf_token = self._extract_csrf_token(csrf_response.text)
            
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

