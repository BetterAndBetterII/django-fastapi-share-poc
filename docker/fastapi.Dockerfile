FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

# 复制entrypoint脚本
COPY docker/fastapi-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 复制应用代码
COPY fastapi_app/ .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

