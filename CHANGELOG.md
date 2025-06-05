# 更改日志

本文档记录Django与FastAPI共享Redis Session认证项目的所有重要变更。

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 初始项目结构
- Django应用与Redis session配置
- FastAPI应用与Redis session配置
- 共享鉴权机制和测试用例
- Docker和GitHub Workflow配置
- 项目文档

## [0.1.0] - 2025-06-05

### 新增
- 初始版本发布
- Django应用基础功能
  - 用户注册和登录
  - 个人资料页面
  - Redis session存储
- FastAPI应用基础功能
  - 用户API
  - Session API
  - 健康检查API
- 共享认证机制
  - Django session解析
  - 共享cookie配置
- 测试套件
  - 单元测试
  - 集成测试
  - 端到端测试
- Docker配置
  - Django Dockerfile
  - FastAPI Dockerfile
  - 测试 Dockerfile
  - docker-compose.yml
- GitHub Actions工作流
  - 自动测试
  - 构建Docker镜像
  - 发布到GHCR
- 项目文档
  - README.md
  - DESIGN.md
  - USAGE.md
  - CONTRIBUTING.md
  - CHANGELOG.md

