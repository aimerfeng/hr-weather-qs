"""
Web API - 配置端点

提供 API 配置测试和验证功能。

Requirements: 8.5, 8.8
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from web.lib.config_manager import ConfigManager
from web.lib.models import APIConfig, ValidationResult

router = APIRouter()


class TestConfigRequest(BaseModel):
    """测试配置请求模型"""
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"


class TestConfigResponse(BaseModel):
    """测试配置响应模型"""
    success: bool
    is_valid: bool
    error_message: Optional[str] = None
    message: Optional[str] = None


@router.post("/test")
async def test_config(request: TestConfigRequest):
    """
    测试 API 配置连接
    
    Requirements:
    - 8.5: 保存配置前验证连接
    - 8.8: 提供测试连接按钮
    
    Args:
        request: 测试配置请求
        
    Returns:
        TestConfigResponse: 测试结果
    """
    try:
        # 创建配置对象
        config = APIConfig(
            provider=request.provider,
            base_url=request.base_url,
            api_key=request.api_key,
            model=request.model
        )
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 基本验证
        basic_validation = config_manager.validate_config(config)
        if not basic_validation.is_valid:
            return TestConfigResponse(
                success=True,
                is_valid=False,
                error_message=basic_validation.error_message
            )
        
        # 连接测试
        connection_test = await config_manager.test_connection(config)
        
        if connection_test.is_valid:
            return TestConfigResponse(
                success=True,
                is_valid=True,
                message="连接测试成功！API 配置有效。"
            )
        else:
            return TestConfigResponse(
                success=True,
                is_valid=False,
                error_message=connection_test.error_message
            )
        
    except Exception as e:
        return TestConfigResponse(
            success=False,
            is_valid=False,
            error_message=f"测试配置时出错: {str(e)}"
        )


@router.get("/presets")
async def get_presets():
    """
    获取预设提供商列表
    
    Returns:
        dict: 预设提供商信息
    """
    try:
        config_manager = ConfigManager()
        presets = config_manager.get_presets()
        
        # 转换为字典格式
        presets_dict = {}
        for key, preset in presets.items():
            presets_dict[key] = {
                "name": preset.name,
                "display_name": preset.display_name,
                "base_url": preset.base_url,
                "models": preset.models,
                "default_model": preset.default_model
            }
        
        return {
            "success": True,
            "data": presets_dict
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取预设列表失败: {str(e)}"
        }


@router.post("/validate")
async def validate_config(request: TestConfigRequest):
    """
    验证配置（不测试连接）
    
    仅进行基本的格式验证，不发送实际请求。
    
    Args:
        request: 配置请求
        
    Returns:
        dict: 验证结果
    """
    try:
        config = APIConfig(
            provider=request.provider,
            base_url=request.base_url,
            api_key=request.api_key,
            model=request.model
        )
        
        config_manager = ConfigManager()
        validation = config_manager.validate_config(config)
        
        return {
            "success": True,
            "is_valid": validation.is_valid,
            "error_message": validation.error_message
        }
        
    except Exception as e:
        return {
            "success": False,
            "is_valid": False,
            "error_message": f"验证配置时出错: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 健康状态
    """
    return {
        "status": "healthy",
        "service": "config-api",
        "version": "1.0.0"
    }
