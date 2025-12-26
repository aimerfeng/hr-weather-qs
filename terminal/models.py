"""
终端版本 - 核心数据模型

定义天气、职业规划和配置相关的数据模型。
使用 Pydantic 进行数据验证和序列化。

Requirements: 1.2, 2.1, 3.4, 4.1
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class Intent(str, Enum):
    """用户意图枚举"""
    WEATHER = "weather"
    CAREER = "career"
    GENERAL = "general"


class Message(BaseModel):
    """对话消息"""
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WeatherData(BaseModel):
    """
    天气数据模型
    
    Requirements 1.2: 包含城市名、温度、湿度、风速、天气状况描述
    """
    city: str
    country: str = ""
    temperature: float  # 摄氏度
    feels_like: float = 0.0
    humidity: int  # 百分比
    wind_speed: float  # km/h
    condition: str  # 天气状况描述
    icon: str = ""  # 天气图标代码
    updated_at: datetime = Field(default_factory=datetime.now)


class ForecastDay(BaseModel):
    """
    单日预报模型
    
    Requirements 3.4: 包含日期、星期、温度范围、湿度、天气图标
    """
    date: datetime
    day_of_week: str
    temp_min: float
    temp_max: float
    humidity: int
    condition: str
    icon: str = ""
    is_good_weather: bool = True  # 用于颜色区分


class WeatherHistoryEntry(BaseModel):
    """
    天气查询历史条目
    
    Requirements 2.1: 保存城市名、查询时间戳、天气快照
    """
    city: str
    last_query_time: datetime
    query_count: int = 1
    last_weather: WeatherData


class WeatherHistory(BaseModel):
    """
    天气历史记录管理
    
    Requirements 2.1, 2.4, 2.5, 2.6, 2.7:
    - 保存查询历史
    - JSON 文件持久化
    - 最多 10 条记录
    - 重复查询更新位置
    - 识别最常查询城市
    """
    entries: List[WeatherHistoryEntry] = Field(default_factory=list)
    max_entries: int = 10
    
    def add_entry(self, city: str, weather: WeatherData) -> None:
        """
        添加或更新历史记录
        
        如果城市已存在，更新其位置到最前面并增加查询次数
        如果是新城市，添加到最前面，超出限制则移除最旧的
        """
        city_lower = city.lower()
        
        # 查找是否已存在
        existing_index = None
        for i, entry in enumerate(self.entries):
            if entry.city.lower() == city_lower:
                existing_index = i
                break
        
        if existing_index is not None:
            # 更新现有条目
            existing = self.entries.pop(existing_index)
            existing.last_query_time = datetime.now()
            existing.query_count += 1
            existing.last_weather = weather
            self.entries.insert(0, existing)
        else:
            # 添加新条目
            new_entry = WeatherHistoryEntry(
                city=city,
                last_query_time=datetime.now(),
                query_count=1,
                last_weather=weather
            )
            self.entries.insert(0, new_entry)
            
            # 限制数量
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[:self.max_entries]
    
    def get_most_frequent_city(self) -> Optional[str]:
        """获取查询次数最多的城市"""
        if not self.entries:
            return None
        
        most_frequent = max(self.entries, key=lambda e: e.query_count)
        return most_frequent.city
    
    def get_entries_sorted_by_time(self) -> List[WeatherHistoryEntry]:
        """按最近查询时间排序返回历史记录"""
        return sorted(self.entries, key=lambda e: e.last_query_time, reverse=True)
    
    def to_json(self) -> str:
        """序列化为 JSON 字符串"""
        return self.model_dump_json(indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "WeatherHistory":
        """从 JSON 字符串反序列化"""
        return cls.model_validate_json(json_str)
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "WeatherHistory":
        """从文件加载"""
        path = Path(filepath)
        if not path.exists():
            return cls()
        
        json_str = path.read_text(encoding="utf-8")
        return cls.from_json(json_str)


class APIConfig(BaseModel):
    """
    API 配置模型
    
    Requirements 8.2, 8.3, 8.4: 支持自定义 API 配置
    """
    provider: str = "openai"  # "openai" | "deepseek" | "qwen" | "custom"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    
    def to_json(self) -> str:
        """序列化为 JSON 字符串"""
        return self.model_dump_json(indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "APIConfig":
        """从 JSON 字符串反序列化"""
        return cls.model_validate_json(json_str)
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "APIConfig":
        """从文件加载"""
        path = Path(filepath)
        if not path.exists():
            return cls()
        
        json_str = path.read_text(encoding="utf-8")
        return cls.from_json(json_str)


class ValidationResult(BaseModel):
    """配置验证结果"""
    is_valid: bool
    error_message: Optional[str] = None


class CareerContext(BaseModel):
    """
    职业规划上下文
    
    Requirements 4.1, 4.2: 收集用户职业规划信息
    按顺序收集: 基本信息 → 兴趣 → 技能 → 经验 → 目标 → 偏好
    """
    basic_info: Optional[str] = None      # 基本信息
    interests: Optional[str] = None       # 兴趣爱好
    skills: Optional[str] = None          # 技能水平
    experience: Optional[str] = None      # 工作经验
    goals: Optional[str] = None           # 职业目标
    preferences: Optional[str] = None     # 工作偏好
    
    def get_completed_stages(self) -> List[str]:
        """获取已完成的阶段列表"""
        stages = []
        if self.basic_info:
            stages.append("basic_info")
        if self.interests:
            stages.append("interests")
        if self.skills:
            stages.append("skills")
        if self.experience:
            stages.append("experience")
        if self.goals:
            stages.append("goals")
        if self.preferences:
            stages.append("preferences")
        return stages
    
    def get_progress(self) -> float:
        """获取进度 (0.0 - 1.0)"""
        total_stages = 6
        completed = len(self.get_completed_stages())
        return completed / total_stages
    
    def is_complete(self) -> bool:
        """检查是否所有信息都已收集"""
        return self.get_progress() >= 1.0


class CareerDirection(BaseModel):
    """
    职业方向推荐
    
    Requirements 4.6: 包含职位、行业、薪资范围、需求水平
    """
    position: str
    industry: str
    salary_range: str
    demand_level: str  # "高" | "中" | "低"
    description: str
    requirements: List[str] = Field(default_factory=list)


class LearningResource(BaseModel):
    """
    学习资源
    
    Requirements 4.9: 分类为免费和付费资源
    """
    name: str
    type: str  # "课程" | "书籍" | "认证" | "项目"
    url: Optional[str] = None
    estimated_time: str
    priority: str  # "必学" | "推荐" | "可选"


class LearningPath(BaseModel):
    """
    学习路径
    
    Requirements 4.9: 包含免费和付费资源分类
    """
    free_resources: List[LearningResource] = Field(default_factory=list)
    paid_resources: List[LearningResource] = Field(default_factory=list)


class TechRecommendation(BaseModel):
    """
    技术栈推荐
    
    Requirements 4.8: 包含学习时间估计
    """
    category: str  # "编程语言" | "框架" | "工具" | "平台"
    name: str
    reason: str
    learning_time: str


class Milestone(BaseModel):
    """里程碑"""
    goal: str
    timeframe: str
    key_actions: List[str] = Field(default_factory=list)


class Timeline(BaseModel):
    """
    时间线规划
    
    Requirements 5.8: 包含短期、中期、长期目标
    """
    short_term: List[Milestone] = Field(default_factory=list)   # 0-6个月
    mid_term: List[Milestone] = Field(default_factory=list)     # 6-18个月
    long_term: List[Milestone] = Field(default_factory=list)    # 18个月以上


class ActionItem(BaseModel):
    """
    行动项
    
    Requirements 5.9: 优先级排序的下一步行动
    """
    priority: int  # 1-5
    action: str
    deadline: str
    expected_outcome: str


class CareerReport(BaseModel):
    """
    职业规划报告结构
    
    Requirements 5.1-5.9: 包含所有必需章节
    """
    executive_summary: str = ""                                    # 5.1 执行摘要
    personal_profile: str = ""                                     # 5.2 个人档案分析
    career_directions: List[CareerDirection] = Field(default_factory=list)  # 5.3 职业方向推荐
    industry_analysis: str = ""                                    # 5.4 行业分析
    skill_gap_analysis: str = ""                                   # 5.5 技能差距分析
    learning_path: LearningPath = Field(default_factory=LearningPath)       # 5.6 学习路径
    tech_stack: List[TechRecommendation] = Field(default_factory=list)      # 5.7 技术栈推荐
    timeline: Timeline = Field(default_factory=Timeline)           # 5.8 时间线和里程碑
    action_items: List[ActionItem] = Field(default_factory=list)   # 5.9 行动项
    
    def is_complete(self) -> bool:
        """检查报告是否包含所有必需章节"""
        return (
            bool(self.executive_summary) and
            bool(self.personal_profile) and
            len(self.career_directions) >= 3 and
            bool(self.industry_analysis) and
            bool(self.skill_gap_analysis) and
            (len(self.learning_path.free_resources) > 0 or 
             len(self.learning_path.paid_resources) > 0) and
            len(self.tech_stack) > 0 and
            (len(self.timeline.short_term) > 0 or 
             len(self.timeline.mid_term) > 0 or 
             len(self.timeline.long_term) > 0) and
            len(self.action_items) > 0
        )
