FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update && apt-get install -y --no-install-recommends redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000 8001

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["django"]
