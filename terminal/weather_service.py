"""
终端版本 - 天气服务

提供天气查询和历史记录管理功能。
使用 wttr.in 免费 API 获取天气数据。

Requirements: 1.1, 1.2, 2.1, 2.2, 2.4, 2.5, 2.6, 2.7, 3.1, 3.4, 3.6
"""

import requests
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from terminal.models import WeatherData, ForecastDay, WeatherHistory


class WeatherAPIError(Exception):
    """天气 API 调用错误"""
    pass


class CityNotFoundError(Exception):
    """城市未找到错误"""
    pass


class WeatherService:
    """
    天气查询服务
    
    Requirements:
    - 1.1: 调用外部天气 API 获取天气数据
    - 1.2: 返回城市名、温度、湿度、风速、天气状况
    - 3.1: 获取未来 5 天预报
    - 3.4: 预报包含日期、星期、温度范围、湿度、图标
    - 3.6: 区分好天气和坏天气
    """
    
    WTTR_API_URL = "https://wttr.in"
    HISTORY_FILE = "data/weather_history.json"
    MAX_HISTORY = 10
    
    # 好天气条件关键词
    GOOD_WEATHER_CONDITIONS = [
        "sunny", "clear", "partly cloudy", "晴", "多云", "少云",
        "fair", "fine", "bright"
    ]
    
    # 坏天气条件关键词
    BAD_WEATHER_CONDITIONS = [
        "rain", "storm", "snow", "thunder", "雨", "雪", "雷",
        "sleet", "hail", "fog", "mist", "drizzle", "shower",
        "overcast", "cloudy", "阴"
    ]
    
    def __init__(self, history_file: Optional[str] = None):
        """
        初始化天气服务
        
        Args:
            history_file: 历史记录文件路径，默认为 data/weather_history.json
        """
        self.history_file = history_file or self.HISTORY_FILE
        self.history = self._load_history()
    
    def get_weather(self, city: str) -> WeatherData:
        """
        获取指定城市的当前天气
        
        Requirements 1.1, 1.2: 调用外部 API 获取天气数据
        
        Args:
            city: 城市名称
            
        Returns:
            WeatherData: 天气数据对象
            
        Raises:
            WeatherAPIError: API 调用失败
            CityNotFoundError: 城市未找到
        """
        try:
            # 使用 wttr.in API 获取天气数据
            url = f"{self.WTTR_API_URL}/{city}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                raise CityNotFoundError(f"未找到城市: {city}")
            
            response.raise_for_status()
            data = response.json()
            
            # 解析当前天气数据
            current = data.get("current_condition", [{}])[0]
            nearest_area = data.get("nearest_area", [{}])[0]
            
            weather = WeatherData(
                city=city,
                country=nearest_area.get("country", [{}])[0].get("value", ""),
                temperature=float(current.get("temp_C", 0)),
                feels_like=float(current.get("FeelsLikeC", 0)),
                humidity=int(current.get("humidity", 0)),
                wind_speed=float(current.get("windspeedKmph", 0)),
                condition=current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                icon=current.get("weatherCode", ""),
                updated_at=datetime.now()
            )
            
            # 保存到历史记录
            self._save_to_history(city, weather)
            
            return weather
            
        except requests.exceptions.Timeout:
            raise WeatherAPIError("天气服务响应超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"获取天气信息失败: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise WeatherAPIError(f"解析天气数据失败: {str(e)}")

    
    def get_forecast(self, city: str, days: int = 5) -> List[ForecastDay]:
        """
        获取未来几天的天气预报
        
        Requirements 3.1, 3.4, 3.6:
        - 获取未来 5 天预报
        - 包含日期、星期、温度范围、湿度、图标
        - 区分好天气和坏天气
        
        Args:
            city: 城市名称
            days: 预报天数，默认 5 天
            
        Returns:
            List[ForecastDay]: 预报数据列表
            
        Raises:
            WeatherAPIError: API 调用失败
            CityNotFoundError: 城市未找到
        """
        try:
            url = f"{self.WTTR_API_URL}/{city}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                raise CityNotFoundError(f"未找到城市: {city}")
            
            response.raise_for_status()
            data = response.json()
            
            weather_data = data.get("weather", [])
            forecasts = []
            
            # 星期映射
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            for i, day_data in enumerate(weather_data[:days]):
                date_str = day_data.get("date", "")
                date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
                
                # 获取天气状况
                hourly = day_data.get("hourly", [{}])
                # 取中午时段的天气作为当天代表
                mid_day = hourly[len(hourly) // 2] if hourly else {}
                condition = mid_day.get("weatherDesc", [{}])[0].get("value", "Unknown")
                
                forecast = ForecastDay(
                    date=date,
                    day_of_week=weekday_names[date.weekday()],
                    temp_min=float(day_data.get("mintempC", 0)),
                    temp_max=float(day_data.get("maxtempC", 0)),
                    humidity=int(day_data.get("avgHumidity", 0) if day_data.get("avgHumidity") else 
                                mid_day.get("humidity", 0)),
                    condition=condition,
                    icon=mid_day.get("weatherCode", ""),
                    is_good_weather=self._is_good_weather(condition)
                )
                forecasts.append(forecast)
            
            return forecasts
            
        except requests.exceptions.Timeout:
            raise WeatherAPIError("天气服务响应超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"获取天气预报失败: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise WeatherAPIError(f"解析天气预报数据失败: {str(e)}")
    
    def _is_good_weather(self, condition: str) -> bool:
        """
        判断天气是否为好天气
        
        Requirements 3.6: 区分好天气和坏天气
        - 好天气: sunny, clear, partly cloudy
        - 坏天气: rain, storm, snow
        
        Args:
            condition: 天气状况描述
            
        Returns:
            bool: True 表示好天气，False 表示坏天气
        """
        condition_lower = condition.lower()
        
        # 先检查是否为好天气（优先检查多词条件如 "partly cloudy"）
        # 按长度降序排列，确保更具体的条件先匹配
        sorted_good = sorted(self.GOOD_WEATHER_CONDITIONS, key=len, reverse=True)
        for good in sorted_good:
            if good in condition_lower:
                return True
        
        # 再检查是否为坏天气
        for bad in self.BAD_WEATHER_CONDITIONS:
            if bad in condition_lower:
                return False
        
        # 默认为好天气
        return True
    
    # ==================== 历史记录管理 ====================
    
    def get_history(self) -> List:
        """
        获取查询历史，按最近查询时间排序
        
        Requirements 2.2: 显示历史查询城市列表
        
        Returns:
            List[WeatherHistoryEntry]: 历史记录列表
        """
        return self.history.get_entries_sorted_by_time()
    
    def get_most_frequent_city(self) -> Optional[str]:
        """
        获取查询次数最多的城市
        
        Requirements 2.7: 识别最常查询城市
        
        Returns:
            Optional[str]: 最常查询的城市名，无历史记录时返回 None
        """
        return self.history.get_most_frequent_city()
    
    def _save_to_history(self, city: str, weather: WeatherData) -> None:
        """
        保存查询到历史记录
        
        Requirements 2.1, 2.5, 2.6:
        - 保存城市名、时间戳、天气快照
        - 最多 10 条记录
        - 重复查询更新位置
        
        Args:
            city: 城市名称
            weather: 天气数据
        """
        self.history.add_entry(city, weather)
        self._persist_history()
    
    def _load_history(self) -> WeatherHistory:
        """
        从文件加载历史记录
        
        Requirements 2.4: JSON 文件持久化
        
        Returns:
            WeatherHistory: 历史记录对象
        """
        return WeatherHistory.load_from_file(self.history_file)
    
    def _persist_history(self) -> None:
        """
        持久化历史记录到文件
        
        Requirements 2.4: JSON 文件持久化
        """
        self.history.save_to_file(self.history_file)
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history = WeatherHistory()
        self._persist_history()
