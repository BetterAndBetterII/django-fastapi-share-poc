.PHONY: up down build test django-shell fastapi-shell migrate create-superuser clean help

# 默认目标
help:
	@echo "可用命令:"
	@echo "  make up              启动所有服务"
	@echo "  make down            停止所有服务"
	@echo "  make build           构建所有服务"
	@echo "  make test            运行测试"
	@echo "  make django-shell    进入Django应用的shell"
	@echo "  make fastapi-shell   进入FastAPI应用的shell"
	@echo "  make migrate         运行Django数据库迁移"
	@echo "  make create-superuser 创建Django超级用户"
	@echo "  make clean           清理临时文件和缓存"

# 启动所有服务
up:
	docker-compose up -d

# 停止所有服务
down:
	docker-compose down

# 构建所有服务
build:
	docker-compose build

# 运行测试
test:
	docker-compose run --rm tests

# 进入Django应用的shell
django-shell:
	docker-compose exec django_app python manage.py shell

# 进入FastAPI应用的shell
fastapi-shell:
	docker-compose exec fastapi_app /bin/bash

# 运行Django数据库迁移
migrate:
	docker-compose exec django_app python manage.py migrate

# 创建Django超级用户
create-superuser:
	docker-compose exec django_app python manage.py createsuperuser

# 清理临时文件和缓存
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type f -name *.pyc -delete

