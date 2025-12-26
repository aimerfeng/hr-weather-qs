"""
Vercel 入口点 - 简化版本
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Assistant Agent API",
    description="智能助手 API",
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

# 读取 HTML 文件内容
html_content = None
try:
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
except Exception as e:
    print(f"Could not load HTML: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回主页面"""
    if html_content:
        return HTMLResponse(content=html_content)
    
    # 如果没有 HTML，返回简单的欢迎页面
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Assistant Agent</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>AI Assistant Agent API</h1>
        <p>API is running successfully!</p>
        <ul>
            <li><a href="/docs">API Documentation</a></li>
            <li><a href="/health">Health Check</a></li>
        </ul>
    </body>
    </html>
    """)

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
