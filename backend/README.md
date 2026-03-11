# DIP Studio Backend

DIP 数字员工运营平台后端服务，基于 FastAPI，采用六边形架构。

## 环境要求

- Python 3.10+
- pip

## 安装依赖

在 `backend` 目录下执行：

```bash
# 仅运行时依赖
pip install -e .

# 含开发与测试依赖
pip install -e ".[dev]"
```

## 运行服务

### 开发模式

```bash
# 在 backend 目录下
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

或使用入口脚本：

```bash
python -m src.main
```

安装后也可使用命令行：

```bash
dip-studio
```

### Docker

镜像使用 `requirements.txt` 安装依赖，无需安装整个项目。

```bash
# 在 backend 目录下构建
docker build -t dip-studio:latest .

# 运行（映射 8000 端口）
docker run -p 8000:8000 dip-studio:latest
```

健康检查已内置（`HEALTHCHECK` 请求 `/api/dip-studio/v1/healthz`）。可通过环境变量覆盖配置，例如 `-e DIP_STUDIO_PORT=8080`。

### 配置

通过环境变量配置，前缀为 `DIP_STUDIO_`。也可在 `backend` 目录下创建 `.env` 文件。

常用配置示例：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DIP_STUDIO_APP_NAME | 应用名称 | DIP Studio |
| DIP_STUDIO_HOST | 监听地址 | 0.0.0.0 |
| DIP_STUDIO_PORT | 监听端口 | 8000 |
| DIP_STUDIO_API_PREFIX | API 前缀 | /api/dip-studio/v1 |
| DIP_STUDIO_DEBUG | 调试模式 | false |
| DIP_STUDIO_LOG_LEVEL | 日志级别 | INFO |

## 健康检查

服务提供 Kubernetes 风格的健康检查端点（无需认证）：

- **存活检查 (Liveness)**：`GET {api_prefix}/healthz`  
  用于判断进程是否存活，返回 200 表示健康。

- **就绪检查 (Readiness)**：`GET {api_prefix}/readyz`  
  用于判断服务是否已初始化完成、可接受流量；未就绪时返回 503。

默认地址示例：

- http://localhost:8000/api/dip-studio/v1/healthz
- http://localhost:8000/api/dip-studio/v1/readyz

响应体为空，仅通过 HTTP 状态码表示结果（200 正常，503 不可用）。

## API 文档

启动服务后访问：

- Swagger UI: http://localhost:8000/api/dip-studio/v1/docs
- ReDoc: http://localhost:8000/api/dip-studio/v1/redoc

## 测试

```bash
# 在 backend 目录下
pytest
```

## 项目结构

```
backend/
├── src/
│   ├── main.py              # 应用入口
│   ├── domains/             # 领域模型
│   ├── ports/               # 端口接口
│   ├── adapters/            # 适配器实现
│   ├── application/        # 应用服务
│   ├── routers/             # API 路由
│   └── infrastructure/     # 配置、容器、日志、异常
├── tests/
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── README.md
```
