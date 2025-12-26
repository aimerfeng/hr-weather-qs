"""
Web API 包

包含所有 API 端点的路由模块。
"""

# 使用相对导入以支持 Vercel 部署
try:
    from . import chat, weather, config, index
except ImportError:
    # 本地开发时的导入方式
    from web.api import chat, weather, config, index

__all__ = ["chat", "weather", "config", "index"]
