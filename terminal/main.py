#!/usr/bin/env python3
"""
终端版本 - 主程序

实现命令行聊天界面，支持流式输出和彩色显示。
使用 rich 库提供美观的终端界面。

Requirements: 7.1, 7.4, 7.5, 7.6
"""

import asyncio
import sys
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.style import Style
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.prompt import Prompt
except ImportError:
    print("错误: 未安装 rich 库，请运行: pip install rich")
    sys.exit(1)

from terminal.agent import AgentCore, ConfigurationError, AgentError
from terminal.config_manager import ConfigManager, InteractiveConfigSetup


class OutputFormatter:
    """
    输出格式管理器
    
    管理 AI 输出的格式化，确保输出完整详细且不暴露 AI 身份。
    """
    
    # 需要过滤的 AI 身份相关词汇
    AI_IDENTITY_PATTERNS = [
        "作为一个AI", "作为AI", "作为人工智能", "我是AI", "我是人工智能",
        "作为语言模型", "我是语言模型", "作为大语言模型", "我是大语言模型",
        "作为一个语言模型", "作为一个大语言模型",
        "As an AI", "I am an AI", "As a language model", "I'm an AI",
        "as an artificial intelligence", "I am a language model",
        "作为机器人", "我是机器人", "作为聊天机器人",
    ]
    
    @classmethod
    def filter_ai_identity(cls, text: str) -> str:
        """
        过滤文本中的 AI 身份相关表述
        
        Args:
            text: 原始文本
            
        Returns:
            str: 过滤后的文本
        """
        result = text
        for pattern in cls.AI_IDENTITY_PATTERNS:
            if pattern.lower() in result.lower():
                # 使用更自然的替换
                result = result.replace(pattern, "作为您的助手")
                result = result.replace(pattern.lower(), "作为您的助手")
        return result
    
    @staticmethod
    def format_response(text: str) -> str:
        """
        格式化响应文本
        
        确保输出完整、详细、格式良好。
        
        Args:
            text: 原始响应文本
            
        Returns:
            str: 格式化后的文本
        """
        # 过滤 AI 身份
        text = OutputFormatter.filter_ai_identity(text)
        return text


class TerminalChat:
    """
    终端聊天界面
    
    提供命令行交互式聊天功能，支持：
    - 流式输出显示
    - 彩色美化界面
    - 退出命令
    - 配置管理
    
    Requirements:
    - 7.1: 显示欢迎信息和快速开始建议
    - 7.4: 发送消息后禁用输入直到响应开始
    - 7.5: 提供退出命令
    - 7.6: 保持对话上下文
    """
    
    # 退出命令
    EXIT_COMMANDS = ['exit', 'quit', '退出', 'bye', '再见', 'q']
    
    # 特殊命令
    SPECIAL_COMMANDS = {
        '/help': '显示帮助信息',
        '/clear': '清空对话历史',
        '/config': '重新配置 API',
        '/history': '显示天气查询历史',
        '/cancel': '取消当前职业规划面试',
    }
    
    def __init__(self):
        """初始化终端聊天界面"""
        self.console = Console()
        self.config_manager = ConfigManager()
        self.agent: Optional[AgentCore] = None
        self.running = True
        self.formatter = OutputFormatter()
    
    async def run(self):
        """运行聊天循环"""
        self._print_welcome()
        
        # 检查并设置配置
        if not await self._ensure_config():
            return
        
        # 初始化代理
        if not await self._initialize_agent():
            return
        
        # 主聊天循环
        while self.running:
            try:
                user_input = self._get_input()
                
                if not user_input:
                    continue
                
                # 检查退出命令
                if user_input.lower() in self.EXIT_COMMANDS:
                    self._print_goodbye()
                    self.running = False
                    continue
                
                # 检查特殊命令
                if user_input.startswith('/'):
                    await self._handle_special_command(user_input)
                    continue
                
                # 处理普通消息
                await self._process_and_display(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n")
                self._print_goodbye()
                self.running = False
            except Exception as e:
                self.console.print(f"\n[red]发生错误: {str(e)}[/red]")
    
    def _print_welcome(self):
        """打印欢迎信息"""
        welcome_text = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                    🌟 智能助手 - 小助 🌟                      ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]

[green]欢迎使用智能助手！我是小助，您的个人助手。[/green]

[yellow]我可以帮您：[/yellow]
  🌤️  查询任何城市的天气和未来预报
  🎯  提供深度职业规划建议和报告
  💬  回答各种问题，提供信息和建议

[dim]快速开始：[/dim]
  • 输入 "北京天气" 查询天气
  • 输入 "职业规划" 开始职业规划
  • 输入 /help 查看所有命令
  • 输入 exit 或 退出 结束对话
"""
        self.console.print(welcome_text)
    
    def _print_goodbye(self):
        """打印告别信息"""
        self.console.print("\n[cyan]感谢使用智能助手！再见！👋[/cyan]\n")
    
    def _print_help(self):
        """打印帮助信息"""
        help_text = """
[bold cyan]📖 帮助信息[/bold cyan]

[yellow]可用命令：[/yellow]
"""
        for cmd, desc in self.SPECIAL_COMMANDS.items():
            help_text += f"  [green]{cmd}[/green] - {desc}\n"
        
        help_text += f"""
[yellow]退出命令：[/yellow]
  [green]exit / quit / 退出 / bye / q[/green] - 结束对话

[yellow]功能说明：[/yellow]
  [cyan]天气查询[/cyan] - 输入包含城市名和"天气"的句子
    例如: "北京天气怎么样" "上海明天天气"
  
  [cyan]职业规划[/cyan] - 输入包含"职业"或"规划"的句子
    例如: "我想做职业规划" "帮我规划职业发展"
  
  [cyan]通用问答[/cyan] - 直接输入您的问题
    例如: "Python 怎么学习" "推荐一些好书"
"""
        self.console.print(help_text)
    
    async def _ensure_config(self) -> bool:
        """确保有有效的配置"""
        if self.config_manager.has_valid_config():
            config = self.config_manager.get_config()
            self.console.print(f"\n[dim]当前配置: {config.provider} - {config.model}[/dim]")
            return True
        
        self.console.print("\n[yellow]首次使用需要配置 AI API[/yellow]")
        
        setup = InteractiveConfigSetup(self.config_manager)
        config = setup.run()
        
        if config is None:
            self.console.print("[red]配置已取消，程序退出[/red]")
            return False
        
        return True
    
    async def _initialize_agent(self) -> bool:
        """初始化代理"""
        try:
            self.agent = AgentCore(config_manager=self.config_manager)
            await self.agent.initialize()
            self.console.print("[green]✓ 助手已准备就绪[/green]\n")
            return True
        except ConfigurationError as e:
            self.console.print(f"[red]配置错误: {str(e)}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]初始化失败: {str(e)}[/red]")
            return False
    
    def _get_input(self) -> str:
        """获取用户输入"""
        try:
            # 使用 rich 的样式化输入提示
            self.console.print("[bold green]您:[/bold green] ", end="")
            user_input = input().strip()
            return user_input
        except EOFError:
            return "exit"
    
    async def _handle_special_command(self, command: str):
        """处理特殊命令"""
        cmd = command.lower().split()[0]
        
        if cmd == '/help':
            self._print_help()
        
        elif cmd == '/clear':
            if self.agent:
                self.agent.clear_conversation()
            self.console.print("[green]✓ 对话历史已清空[/green]\n")
        
        elif cmd == '/config':
            setup = InteractiveConfigSetup(self.config_manager)
            config = setup.run()
            if config:
                # 重新初始化代理
                await self._initialize_agent()
        
        elif cmd == '/history':
            self._show_weather_history()
        
        elif cmd == '/cancel':
            if self.agent and self.agent.is_in_career_interview():
                msg = self.agent.cancel_career_interview()
                self.console.print(f"[yellow]{msg}[/yellow]\n")
            else:
                self.console.print("[dim]当前没有进行中的职业规划面试[/dim]\n")
        
        else:
            self.console.print(f"[red]未知命令: {cmd}[/red]")
            self.console.print("[dim]输入 /help 查看可用命令[/dim]\n")
    
    def _show_weather_history(self):
        """显示天气查询历史"""
        if not self.agent:
            self.console.print("[red]助手未初始化[/red]\n")
            return
        
        history = self.agent.weather_service.get_history()
        
        if not history:
            self.console.print("[dim]暂无天气查询历史[/dim]\n")
            return
        
        self.console.print("\n[bold cyan]🌤️ 天气查询历史[/bold cyan]\n")
        
        most_frequent = self.agent.weather_service.get_most_frequent_city()
        
        for entry in history:
            is_frequent = entry.city.lower() == (most_frequent or "").lower()
            star = "⭐ " if is_frequent else "   "
            time_str = entry.last_query_time.strftime("%m-%d %H:%M")
            
            self.console.print(
                f"{star}[cyan]{entry.city}[/cyan] - "
                f"{entry.last_weather.temperature}°C, {entry.last_weather.condition} "
                f"[dim]({time_str}, 查询{entry.query_count}次)[/dim]"
            )
        
        self.console.print()
    
    async def _process_and_display(self, message: str):
        """处理消息并流式显示响应"""
        if not self.agent:
            self.console.print("[red]助手未初始化[/red]\n")
            return
        
        # 显示助手标签
        self.console.print("[bold blue]小助:[/bold blue] ", end="")
        
        try:
            response_text = ""
            chunk_buffer = ""
            
            async for chunk in self.agent.process_message(message):
                # 过滤 AI 身份相关内容
                filtered_chunk = self.formatter.filter_ai_identity(chunk)
                chunk_buffer += filtered_chunk
                
                # 实时输出每个字符块
                self.console.print(filtered_chunk, end="")
                response_text += filtered_chunk
            
            # 输出换行
            self.console.print("\n")
            
        except Exception as e:
            self.console.print(f"\n[red]处理消息时出错: {str(e)}[/red]\n")


async def main():
    """主函数"""
    chat = TerminalChat()
    await chat.run()


def run():
    """入口函数"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n再见！")


if __name__ == "__main__":
    run()
