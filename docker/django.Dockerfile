FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

# 复制entrypoint脚本
COPY docker/django-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 复制应用代码
COPY django_app/ .

# 设置静态文件目录
RUN mkdir -p staticfiles

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

