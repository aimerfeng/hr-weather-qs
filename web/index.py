"""
Vercel 入口点

这个文件确保 Vercel 能找到 FastAPI 应用。
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.index import app
except ImportError:
    # 如果导入失败，创建一个基本的 FastAPI 应用
    from fastapi import FastAPI
    app = FastAPI(title="AI Assistant Agent API")
    
    @app.get("/")
    def root():
        return {"message": "API is running", "error": "Could not load full application"}

# 导出 app 供 Vercel 使用
__all__ = ["app"]
