FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

# 复制应用代码
COPY fastapi_app/ .

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

