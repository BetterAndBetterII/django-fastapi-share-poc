FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements-tests.txt .
RUN pip install --no-cache-dir -r requirements-tests.txt

# 复制测试代码
COPY tests/ ./tests/

# 设置工作目录
WORKDIR /app/tests

# 运行测试
CMD ["pytest", "-xvs", "integration/"]

