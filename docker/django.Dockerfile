FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

# 复制应用代码
COPY django_app/ .

# 运行应用
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

