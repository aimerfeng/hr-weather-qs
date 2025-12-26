"""
Web API 包

包含所有 API 端点的路由模块。
"""

from web.api import chat, weather, config, index

__all__ = ["chat", "weather", "config", "index"]
