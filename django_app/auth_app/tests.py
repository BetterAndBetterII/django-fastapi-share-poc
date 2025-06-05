from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_login(self):
        """测试登录功能"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('home'))
        
        # 验证用户已登录
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_session_data(self):
        """测试session数据存储"""
        self.client.login(username='testuser', password='testpassword')
        
        # 访问个人资料页面，触发session数据存储
        self.client.get(reverse('profile'))
        
        # 获取session
        session = self.client.session
        
        # 验证session中包含用户ID
        self.assertIn('_auth_user_id', session)
        self.assertEqual(int(session['_auth_user_id']), self.user.id)
    
    def test_logout(self):
        """测试登出功能"""
        self.client.login(username='testuser', password='testpassword')
        
        # 验证用户已登录
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # 登出
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        
        # 验证用户已登出
        response = self.client.get(reverse('profile'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_user_api(self):
        """测试用户API"""
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['auth_backend'], 'django')

