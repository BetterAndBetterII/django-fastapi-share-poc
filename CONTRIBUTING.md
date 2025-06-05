# 贡献指南

感谢您考虑为Django与FastAPI共享Redis Session认证项目做贡献！本文档提供了贡献代码、报告问题和提交功能请求的指南。

## 目录

1. [行为准则](#行为准则)
2. [报告问题](#报告问题)
3. [提交功能请求](#提交功能请求)
4. [开发流程](#开发流程)
5. [提交Pull Request](#提交pull-request)
6. [代码风格](#代码风格)
7. [测试](#测试)

## 行为准则

请尊重所有项目参与者，保持专业和包容的态度。我们希望创建一个友好和协作的环境。

## 报告问题

如果您发现了bug或问题，请通过GitHub Issues报告。报告问题时，请包含以下信息：

1. 问题的简要描述
2. 重现问题的步骤
3. 预期行为
4. 实际行为
5. 环境信息（操作系统、Docker版本等）
6. 相关的日志或错误信息

## 提交功能请求

如果您有新功能的想法，请通过GitHub Issues提交功能请求。请包含以下信息：

1. 功能的简要描述
2. 功能的用例
3. 功能的实现建议（可选）

## 开发流程

### 设置开发环境

1. Fork项目仓库
2. 克隆您的Fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/SimpleRAG.git
   cd SimpleRAG
   ```
3. 添加上游仓库
   ```bash
   git remote add upstream https://github.com/BetterAndBetterII/SimpleRAG.git
   ```
4. 创建环境变量文件
   ```bash
   cp .env.example .env
   ```
5. 启动开发环境
   ```bash
   docker-compose up -d
   ```

### 分支策略

- `main`: 主分支，包含稳定的代码
- `develop`: 开发分支，包含最新的开发代码
- 功能分支: 从`develop`分支创建，命名为`feature/your-feature-name`
- 修复分支: 从`main`分支创建，命名为`fix/your-fix-name`

### 开发工作流

1. 从最新的`develop`分支创建功能分支
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/your-feature-name
   ```
2. 进行开发和测试
3. 提交更改
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```
4. 推送到您的Fork
   ```bash
   git push origin feature/your-feature-name
   ```
5. 创建Pull Request

## 提交Pull Request

1. 确保您的代码通过所有测试
2. 更新文档（如果需要）
3. 在GitHub上创建Pull Request
4. 在Pull Request描述中包含以下信息：
   - 更改的简要描述
   - 解决的问题或实现的功能
   - 测试方法
   - 相关的Issue（如果有）

## 代码风格

### Python代码风格

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)风格指南
- 使用4个空格缩进
- 最大行长度为88个字符
- 使用docstring记录函数和类

### Django代码风格

- 遵循[Django编码风格](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- 使用类视图而不是函数视图
- 使用模型管理器封装数据库操作

### FastAPI代码风格

- 使用类型注解
- 使用Pydantic模型定义请求和响应
- 使用依赖注入管理依赖关系

## 测试

### 测试要求

- 所有新功能必须包含测试
- 所有bug修复必须包含测试，以防止回归
- 测试覆盖率应保持在80%以上

### 运行测试

```bash
# 运行所有测试
docker-compose run --rm tests

# 运行特定测试文件
docker-compose run --rm tests pytest -xvs integration/test_shared_auth.py

# 运行特定测试函数
docker-compose run --rm tests pytest -xvs integration/test_shared_auth.py::test_django_login_fastapi_access
```

### 测试覆盖率

```bash
docker-compose run --rm tests pytest --cov=django_app --cov=fastapi_app --cov-report=term-missing
```

---

再次感谢您的贡献！如果您有任何问题，请随时在GitHub Issues中提问。

