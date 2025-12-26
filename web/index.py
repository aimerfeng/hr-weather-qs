"""
Vercel 入口点

这个文件确保 Vercel 能找到 FastAPI 应用。
"""

from api.index import app

# 导出 app 供 Vercel 使用
__all__ = ["app"]
