"""
Web API - 天气端点

提供天气查询、预报和历史记录的 API 端点。

Requirements: 1.1, 2.2, 3.1
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

# 添加父目录到路径以支持导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lib.weather_service import WeatherService, WeatherAPIError, CityNotFoundError
    from lib.models import WeatherData, ForecastDay, WeatherHistoryEntry
except ImportError:
    from web.lib.weather_service import WeatherService, WeatherAPIError, CityNotFoundError
    from web.lib.models import WeatherData, ForecastDay, WeatherHistoryEntry

router = APIRouter()

# 全局天气服务实例（在 Serverless 环境中每个请求都会创建新实例）
weather_service = WeatherService()


class WeatherResponse(BaseModel):
    """天气响应模型"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class ForecastResponse(BaseModel):
    """预报响应模型"""
    success: bool
    data: Optional[List[dict]] = None
    error: Optional[str] = None


class HistoryResponse(BaseModel):
    """历史记录响应模型"""
    success: bool
    data: Optional[List[dict]] = None
    most_frequent_city: Optional[str] = None
    error: Optional[str] = None


@router.get("/weather/{city}")
async def get_weather(city: str):
    """
    获取指定城市的当前天气
    
    Requirements 1.1: 调用外部天气 API 获取天气数据
    
    Args:
        city: 城市名称
        
    Returns:
        WeatherResponse: 天气数据响应
    """
    try:
        weather = weather_service.get_weather(city)
        
        # 转换为字典格式
        weather_dict = weather.model_dump()
        weather_dict["updated_at"] = weather.updated_at.isoformat()
        
        return WeatherResponse(
            success=True,
            data=weather_dict
        )
        
    except CityNotFoundError as e:
        return WeatherResponse(
            success=False,
            error=f"未找到城市: {city}"
        )
        
    except WeatherAPIError as e:
        return WeatherResponse(
            success=False,
            error=str(e)
        )
        
    except Exception as e:
        return WeatherResponse(
            success=False,
            error=f"获取天气信息失败: {str(e)}"
        )


@router.get("/forecast/{city}")
async def get_forecast(city: str, days: int = 5):
    """
    获取指定城市的天气预报
    
    Requirements 3.1: 获取未来 5 天预报
    
    Args:
        city: 城市名称
        days: 预报天数，默认 5 天
        
    Returns:
        ForecastResponse: 预报数据响应
    """
    try:
        # 限制天数范围
        days = max(1, min(days, 7))
        
        forecast = weather_service.get_forecast(city, days)
        
        # 转换为字典格式
        forecast_list = []
        for day in forecast:
            day_dict = day.model_dump()
            day_dict["date"] = day.date.isoformat()
            forecast_list.append(day_dict)
        
        return ForecastResponse(
            success=True,
            data=forecast_list
        )
        
    except CityNotFoundError as e:
        return ForecastResponse(
            success=False,
            error=f"未找到城市: {city}"
        )
        
    except WeatherAPIError as e:
        return ForecastResponse(
            success=False,
            error=str(e)
        )
        
    except Exception as e:
        return ForecastResponse(
            success=False,
            error=f"获取天气预报失败: {str(e)}"
        )


@router.get("/history")
async def get_history():
    """
    获取天气查询历史记录
    
    Requirements 2.2: 显示历史查询城市列表
    
    Returns:
        HistoryResponse: 历史记录响应
    """
    try:
        history = weather_service.get_history()
        most_frequent = weather_service.get_most_frequent_city()
        
        # 转换为字典格式
        history_list = []
        for entry in history:
            entry_dict = {
                "city": entry.city,
                "last_query_time": entry.last_query_time.isoformat(),
                "query_count": entry.query_count,
                "last_weather": {
                    "temperature": entry.last_weather.temperature,
                    "condition": entry.last_weather.condition,
                    "icon": entry.last_weather.icon
                }
            }
            history_list.append(entry_dict)
        
        return HistoryResponse(
            success=True,
            data=history_list,
            most_frequent_city=most_frequent
        )
        
    except Exception as e:
        return HistoryResponse(
            success=False,
            error=f"获取历史记录失败: {str(e)}"
        )


@router.delete("/history")
async def clear_history():
    """
    清空天气查询历史记录
    
    Returns:
        dict: 操作结果
    """
    try:
        weather_service.clear_history()
        return {
            "success": True,
            "message": "历史记录已清空"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"清空历史记录失败: {str(e)}"
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
        "service": "weather-api",
        "version": "1.0.0"
    }
