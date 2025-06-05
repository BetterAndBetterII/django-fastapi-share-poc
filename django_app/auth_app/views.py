from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


def home_view(request):
    """主页视图"""
    return render(request, 'auth_app/home.html')


def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # 在session中存储额外的用户信息，以便FastAPI可以访问
            request.session['_auth_user_username'] = user.username
            request.session['_auth_user_email'] = user.email
            
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth_app/login.html')


def register_view(request):
    """注册视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth_app/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth_app/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, f'Account created for {username}. You can now login.')
        return redirect('login')
    
    return render(request, 'auth_app/register.html')


def logout_view(request):
    """登出视图"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """个人资料视图"""
    session_id = request.COOKIES.get('shared_session_id', 'Not found')
    return render(request, 'auth_app/profile.html', {'session_id': session_id})


@login_required
def user_api_view(request):
    """用户API视图，返回JSON格式的用户数据"""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'session_id': request.COOKIES.get('shared_session_id', 'Not found'),
        'auth_backend': 'django'
    }
    return JsonResponse(data)

