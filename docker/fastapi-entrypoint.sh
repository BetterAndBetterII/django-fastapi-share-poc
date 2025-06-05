#!/bin/bash
set -e

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

# Wait for Redis
wait_for_redis

# Execute the main command
echo "启动FastAPI应用..."
exec "$@" 