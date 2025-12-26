"""
Web API - 主入口

FastAPI 应用主入口，整合所有 API 路由。
适配 Vercel Serverless 部署。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from web.api import chat, weather, config

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Assistant Agent API",
    description="智能助手 API - 提供天气查询和职业规划功能",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(config.router, prefix="/api/config", tags=["config"])

# 挂载静态文件（仅在本地开发时）
if os.path.exists("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/")
async def root():
    """
    根路径 - 返回主页面
    
    Returns:
        FileResponse: HTML 主页面
    """
    static_path = "web/static/index.html"
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        return {
            "message": "AI Assistant Agent API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }


@app.get("/health")
async def health_check():
    """
    全局健康检查
    
    Returns:
        dict: 健康状态
    """
    return {
        "status": "healthy",
        "service": "ai-assistant-agent",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "weather": "/api/weather",
            "forecast": "/api/forecast",
            "history": "/api/history",
            "config_test": "/api/config/test",
            "config_presets": "/api/config/presets"
        }
    }


# Vercel Serverless 入口
# Vercel 会自动识别这个变量
handler = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
