"""
AI Assistant Agent - Terminal Version

智能助手终端版本，提供天气查询、职业规划和通用问答功能。

使用方法:
    python -m terminal.main

或者:
    from terminal.main import run
    run()
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from terminal.main import run, main

__all__ = ["run", "main"]
