#!/bin/bash
set -e

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "等待PostgreSQL连接..."
    while ! nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do
        echo "PostgreSQL还未准备好，等待中..."
        sleep 2
    done
    echo "PostgreSQL已连接！"
}

# Function to wait for Redis
wait_for_redis() {
    echo "等待Redis连接..."
    redis_host=$(echo ${REDIS_URL:-redis://redis:6379/0} | sed 's|redis://||' | sed 's|/.*||' | sed 's|:.*||')
    redis_port=$(echo ${REDIS_URL:-redis://redis:6379/0} | sed 's|.*:||' | sed 's|/.*||')
    
    while ! nc -z ${redis_host} ${redis_port}; do
        echo "Redis还未准备好，等待中..."
        sleep 2
    done
    echo "Redis已连接！"
}

# Wait for services
wait_for_postgres
wait_for_redis

# Run Django migrations
echo "运行Django迁移..."
python manage.py migrate --noinput

# Collect static files
echo "收集静态文件..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "检查并创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户已创建：admin/admin123')
else:
    print('超级用户已存在')
"

# Execute the main command
echo "启动Django应用..."
exec "$@" 