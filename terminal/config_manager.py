"""
终端版本 - 配置管理器

实现 API 配置的加载、保存、验证和连接测试。
支持预设提供商（OpenAI, DeepSeek, Qwen）和自定义配置。

Requirements: 8.2, 8.4, 8.5, 8.6, 8.7, 8.8
"""

import re
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from terminal.models import APIConfig, ValidationResult
except ImportError:
    from models import APIConfig, ValidationResult


@dataclass
class ProviderPreset:
    """提供商预设配置"""
    name: str
    display_name: str
    base_url: str
    models: List[str]
    default_model: str


class ConfigManager:
    """
    配置管理器
    
    负责 API 配置的加载、验证和持久化。
    支持多种 AI 提供商的预设配置。
    
    Requirements:
    - 8.2: 允许用户输入自定义 API base URL 并验证
    - 8.4: 允许用户选择预设提供商或输入自定义模型名称
    - 8.5: 保存配置前验证连接
    - 8.6: 本地持久化配置
    - 8.7: 无效配置时显示具体错误信息
    - 8.8: 提供测试连接按钮
    """
    
    CONFIG_FILE = "data/config.json"
    
    # 预设提供商配置
    PRESETS: Dict[str, ProviderPreset] = {
        "openai": ProviderPreset(
            name="openai",
            display_name="OpenAI",
            base_url="https://api.openai.com/v1",
            models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
            default_model="gpt-3.5-turbo"
        ),
        "deepseek": ProviderPreset(
            name="deepseek",
            display_name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            models=["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
            default_model="deepseek-chat"
        ),
        "qwen": ProviderPreset(
            name="qwen",
            display_name="通义千问 (Qwen)",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            models=["qwen-turbo", "qwen-plus", "qwen-max", "qwen-long"],
            default_model="qwen-turbo"
        ),
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为 data/config.json
        """
        self.config_file = config_file or self.CONFIG_FILE
        self.config: Optional[APIConfig] = None
        self._load_config()
    
    def get_config(self) -> APIConfig:
        """
        获取当前配置
        
        Returns:
            APIConfig: 当前 API 配置，如果没有则返回默认配置
        """
        if self.config is None:
            self.config = APIConfig()
        return self.config
    
    def update_config(self, config: APIConfig) -> None:
        """
        更新配置并持久化
        
        Args:
            config: 新的 API 配置
        """
        self.config = config
        self._persist_config()

    def validate_config(self, config: APIConfig) -> ValidationResult:
        """
        验证配置是否有效
        
        检查项目:
        - API Key 是否为空
        - Base URL 格式是否正确
        - Model 名称是否为空
        
        Args:
            config: 待验证的配置
            
        Returns:
            ValidationResult: 验证结果，包含是否有效和错误信息
            
        Requirements 8.7: 无效配置时显示具体错误信息
        """
        # 检查 API Key
        if not config.api_key or not config.api_key.strip():
            return ValidationResult(
                is_valid=False,
                error_message="API Key 不能为空，请输入有效的 API Key"
            )
        
        # 检查 Base URL 格式
        url_validation = self._validate_url(config.base_url)
        if not url_validation.is_valid:
            return url_validation
        
        # 检查 Model 名称
        if not config.model or not config.model.strip():
            return ValidationResult(
                is_valid=False,
                error_message="模型名称不能为空，请选择或输入模型名称"
            )
        
        # 检查 Provider
        if not config.provider or not config.provider.strip():
            return ValidationResult(
                is_valid=False,
                error_message="提供商不能为空，请选择提供商"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_url(self, url: str) -> ValidationResult:
        """
        验证 URL 格式
        
        Requirements 8.2: 验证自定义 API base URL
        
        Args:
            url: 待验证的 URL
            
        Returns:
            ValidationResult: 验证结果
        """
        if not url or not url.strip():
            return ValidationResult(
                is_valid=False,
                error_message="API Base URL 不能为空"
            )
        
        # 检查是否为有效的 HTTPS URL
        url_pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
            r'(?::\d+)?'  # 可选端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(url):
            return ValidationResult(
                is_valid=False,
                error_message=f"无效的 URL 格式: {url}，请输入有效的 HTTP/HTTPS URL"
            )
        
        return ValidationResult(is_valid=True)
    
    async def test_connection(self, config: APIConfig) -> ValidationResult:
        """
        测试 API 连接
        
        通过发送一个简单的请求来验证 API 配置是否有效。
        
        Args:
            config: 待测试的配置
            
        Returns:
            ValidationResult: 测试结果
            
        Requirements 8.5, 8.8: 验证连接和测试连接按钮
        """
        # 首先进行基本验证
        basic_validation = self.validate_config(config)
        if not basic_validation.is_valid:
            return basic_validation
        
        try:
            # 动态导入 openai，避免在没有安装时报错
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
            
            # 发送一个简单的测试请求
            response = await client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            if response and response.choices:
                return ValidationResult(is_valid=True)
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message="API 响应异常，请检查配置"
                )
                
        except ImportError:
            return ValidationResult(
                is_valid=False,
                error_message="未安装 openai 库，请运行: pip install openai"
            )
        except Exception as e:
            error_msg = str(e)
            
            # 解析常见错误类型
            if "401" in error_msg or "Unauthorized" in error_msg.lower():
                return ValidationResult(
                    is_valid=False,
                    error_message="API Key 无效或已过期，请检查 API Key"
                )
            elif "404" in error_msg or "not found" in error_msg.lower():
                return ValidationResult(
                    is_valid=False,
                    error_message=f"模型 '{config.model}' 不存在或不可用，请检查模型名称"
                )
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return ValidationResult(
                    is_valid=False,
                    error_message="API 请求频率超限，请稍后重试"
                )
            elif "timeout" in error_msg.lower():
                return ValidationResult(
                    is_valid=False,
                    error_message="连接超时，请检查网络或 API 地址"
                )
            elif "connection" in error_msg.lower():
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无法连接到 {config.base_url}，请检查网络或 API 地址"
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"连接测试失败: {error_msg}"
                )

    def get_presets(self) -> Dict[str, ProviderPreset]:
        """
        获取预设提供商列表
        
        Returns:
            Dict[str, ProviderPreset]: 预设提供商字典
            
        Requirements 8.4: 允许用户选择预设提供商
        """
        return self.PRESETS.copy()
    
    def get_preset(self, provider: str) -> Optional[ProviderPreset]:
        """
        获取指定提供商的预设配置
        
        Args:
            provider: 提供商名称
            
        Returns:
            ProviderPreset: 预设配置，如果不存在则返回 None
        """
        return self.PRESETS.get(provider.lower())
    
    def create_config_from_preset(self, provider: str, api_key: str, model: Optional[str] = None) -> APIConfig:
        """
        从预设创建配置
        
        Args:
            provider: 提供商名称
            api_key: API Key
            model: 模型名称，如果不指定则使用默认模型
            
        Returns:
            APIConfig: 创建的配置
            
        Raises:
            ValueError: 如果提供商不存在
        """
        preset = self.get_preset(provider)
        if preset is None:
            raise ValueError(f"未知的提供商: {provider}，可选: {', '.join(self.PRESETS.keys())}")
        
        return APIConfig(
            provider=preset.name,
            base_url=preset.base_url,
            api_key=api_key,
            model=model or preset.default_model
        )
    
    def create_custom_config(self, base_url: str, api_key: str, model: str) -> APIConfig:
        """
        创建自定义配置
        
        Args:
            base_url: API Base URL
            api_key: API Key
            model: 模型名称
            
        Returns:
            APIConfig: 创建的配置
        """
        return APIConfig(
            provider="custom",
            base_url=base_url,
            api_key=api_key,
            model=model
        )
    
    def _load_config(self) -> None:
        """
        从文件加载配置
        
        Requirements 8.6: 本地持久化配置
        """
        try:
            path = Path(self.config_file)
            if path.exists():
                self.config = APIConfig.load_from_file(self.config_file)
            else:
                self.config = None
        except Exception:
            # 加载失败时使用默认配置
            self.config = None
    
    def _persist_config(self) -> None:
        """
        持久化配置到文件
        
        Requirements 8.6: 本地持久化配置
        """
        if self.config is not None:
            self.config.save_to_file(self.config_file)
    
    def has_valid_config(self) -> bool:
        """
        检查是否有有效的配置
        
        Returns:
            bool: 是否有有效配置
        """
        if self.config is None:
            return False
        
        validation = self.validate_config(self.config)
        return validation.is_valid
    
    def get_masked_api_key(self) -> str:
        """
        获取掩码后的 API Key（用于显示）
        
        Returns:
            str: 掩码后的 API Key，如 "sk-****1234"
            
        Requirements 8.3: API Key 掩码显示
        """
        if self.config is None or not self.config.api_key:
            return ""
        
        key = self.config.api_key
        if len(key) <= 8:
            return "*" * len(key)
        
        # 显示前4位和后4位
        return f"{key[:4]}****{key[-4:]}"
    
    def clear_config(self) -> None:
        """清除配置"""
        self.config = None
        path = Path(self.config_file)
        if path.exists():
            path.unlink()


class InteractiveConfigSetup:
    """
    交互式配置设置
    
    在终端中引导用户完成 API 配置。
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化交互式配置设置
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
    
    def run(self) -> Optional[APIConfig]:
        """
        运行交互式配置流程
        
        Returns:
            APIConfig: 配置成功返回配置，取消返回 None
        """
        print("\n" + "=" * 50)
        print("🔧 AI API 配置向导")
        print("=" * 50)
        
        # 选择提供商
        provider = self._select_provider()
        if provider is None:
            return None
        
        # 输入 API Key
        api_key = self._input_api_key()
        if api_key is None:
            return None
        
        # 选择或输入模型
        if provider == "custom":
            base_url = self._input_base_url()
            if base_url is None:
                return None
            model = self._input_model()
            if model is None:
                return None
            config = self.config_manager.create_custom_config(base_url, api_key, model)
        else:
            model = self._select_model(provider)
            if model is None:
                return None
            config = self.config_manager.create_config_from_preset(provider, api_key, model)
        
        # 验证配置
        validation = self.config_manager.validate_config(config)
        if not validation.is_valid:
            print(f"\n❌ 配置验证失败: {validation.error_message}")
            return None
        
        # 询问是否测试连接
        if self._confirm_test_connection():
            print("\n⏳ 正在测试连接...")
            result = asyncio.run(self.config_manager.test_connection(config))
            if result.is_valid:
                print("✅ 连接测试成功！")
            else:
                print(f"❌ 连接测试失败: {result.error_message}")
                if not self._confirm_save_anyway():
                    return None
        
        # 保存配置
        self.config_manager.update_config(config)
        print("\n✅ 配置已保存！")
        
        return config

    def _select_provider(self) -> Optional[str]:
        """选择提供商"""
        print("\n请选择 AI 提供商:")
        presets = self.config_manager.get_presets()
        
        options = list(presets.keys()) + ["custom"]
        for i, key in enumerate(options, 1):
            if key == "custom":
                print(f"  {i}. 自定义 (Custom)")
            else:
                preset = presets[key]
                print(f"  {i}. {preset.display_name}")
        
        print("  0. 取消")
        
        while True:
            try:
                choice = input("\n请输入选项编号: ").strip()
                if choice == "0":
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                else:
                    print("❌ 无效选项，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def _input_api_key(self) -> Optional[str]:
        """输入 API Key"""
        print("\n请输入 API Key:")
        print("(输入 0 取消)")
        
        while True:
            api_key = input("API Key: ").strip()
            if api_key == "0":
                return None
            if api_key:
                return api_key
            print("❌ API Key 不能为空")
    
    def _input_base_url(self) -> Optional[str]:
        """输入自定义 Base URL"""
        print("\n请输入 API Base URL:")
        print("(例如: https://api.example.com/v1)")
        print("(输入 0 取消)")
        
        while True:
            url = input("Base URL: ").strip()
            if url == "0":
                return None
            
            validation = self.config_manager._validate_url(url)
            if validation.is_valid:
                return url
            print(f"❌ {validation.error_message}")
    
    def _input_model(self) -> Optional[str]:
        """输入自定义模型名称"""
        print("\n请输入模型名称:")
        print("(例如: gpt-3.5-turbo)")
        print("(输入 0 取消)")
        
        while True:
            model = input("模型名称: ").strip()
            if model == "0":
                return None
            if model:
                return model
            print("❌ 模型名称不能为空")
    
    def _select_model(self, provider: str) -> Optional[str]:
        """选择模型"""
        preset = self.config_manager.get_preset(provider)
        if preset is None:
            return self._input_model()
        
        print(f"\n请选择 {preset.display_name} 模型:")
        for i, model in enumerate(preset.models, 1):
            default_mark = " (默认)" if model == preset.default_model else ""
            print(f"  {i}. {model}{default_mark}")
        
        print(f"  {len(preset.models) + 1}. 自定义模型名称")
        print("  0. 取消")
        
        while True:
            try:
                choice = input("\n请输入选项编号 (直接回车使用默认): ").strip()
                
                if choice == "":
                    return preset.default_model
                if choice == "0":
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(preset.models):
                    return preset.models[idx]
                elif idx == len(preset.models):
                    return self._input_model()
                else:
                    print("❌ 无效选项，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def _confirm_test_connection(self) -> bool:
        """确认是否测试连接"""
        while True:
            choice = input("\n是否测试连接? (y/n, 默认 y): ").strip().lower()
            if choice in ["", "y", "yes", "是"]:
                return True
            if choice in ["n", "no", "否"]:
                return False
            print("❌ 请输入 y 或 n")
    
    def _confirm_save_anyway(self) -> bool:
        """确认是否仍然保存"""
        while True:
            choice = input("\n连接测试失败，是否仍然保存配置? (y/n): ").strip().lower()
            if choice in ["y", "yes", "是"]:
                return True
            if choice in ["n", "no", "否"]:
                return False
            print("❌ 请输入 y 或 n")


def setup_config_interactive() -> Optional[APIConfig]:
    """
    便捷函数：运行交互式配置设置
    
    Returns:
        APIConfig: 配置成功返回配置，取消返回 None
    """
    manager = ConfigManager()
    setup = InteractiveConfigSetup(manager)
    return setup.run()


def get_or_setup_config() -> Optional[APIConfig]:
    """
    获取配置，如果没有则引导用户设置
    
    Returns:
        APIConfig: 配置对象，如果用户取消则返回 None
    """
    manager = ConfigManager()
    
    if manager.has_valid_config():
        config = manager.get_config()
        print(f"\n当前配置: {config.provider} - {config.model}")
        print(f"API Key: {manager.get_masked_api_key()}")
        
        while True:
            choice = input("\n使用当前配置? (y/n, 默认 y): ").strip().lower()
            if choice in ["", "y", "yes", "是"]:
                return config
            if choice in ["n", "no", "否"]:
                break
            print("❌ 请输入 y 或 n")
    
    return setup_config_interactive()


# 命令行入口
if __name__ == "__main__":
    config = get_or_setup_config()
    if config:
        print(f"\n配置完成:")
        print(f"  提供商: {config.provider}")
        print(f"  Base URL: {config.base_url}")
        print(f"  模型: {config.model}")
    else:
        print("\n配置已取消")
