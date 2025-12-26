"""
Vercel 入口点 - FastAPI 应用
"""

import sys
import os

# 添加必要的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'api'))
sys.path.insert(0, os.path.join(current_dir, 'lib'))

# 直接在这里创建 FastAPI 应用，而不是导入
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Assistant Agent API",
    description="智能助手 API - 提供天气查询和职业规划功能",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 尝试注册路由
try:
    # 导入路由模块
    import chat
    import weather
    import config as config_module
    
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(weather.router, prefix="/api", tags=["weather"])
    app.include_router(config_module.router, prefix="/api/config", tags=["config"])
except Exception as e:
    print(f"Warning: Could not import routes: {e}")
    # 即使路由导入失败，app 也已经创建

# 静态文件处理
static_dir = os.path.join(current_dir, "static")
if os.path.exists(static_dir):
    try:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")

@app.get("/")
async def root():
    """根路径 - 返回主页面"""
    # 尝试返回 HTML 文件
    index_path = os.path.join(current_dir, "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # 如果没有 HTML 文件，返回 API 信息
    return {
        "message": "AI Assistant Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/api/chat",
            "weather": "/api/weather",
            "config": "/api/config"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-assistant-agent",
        "version": "1.0.0"
    }

# 导出 app
__all__ = ["app"]
