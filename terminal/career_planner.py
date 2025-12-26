"""
终端版本 - 职业规划服务

提供职业规划面试流程和报告生成功能。
实现结构化面试、进度跟踪和报告模板。

Requirements: 4.1, 4.2, 4.3, 4.4, 5.1-5.9
"""

from typing import Dict, Any, List, Optional, Tuple
from terminal.models import (
    CareerContext, CareerReport, CareerDirection, 
    LearningPath, LearningResource, TechRecommendation,
    Timeline, Milestone, ActionItem
)


class CareerPlanner:
    """
    职业规划服务
    
    Requirements:
    - 4.1: 结构化面试，清晰进度指示
    - 4.2: 按顺序收集信息：基本信息 → 兴趣 → 技能 → 经验 → 目标 → 偏好
    - 4.3: 追问不完整的回答
    - 4.4: 提供示例帮助用户理解
    """
    
    # 面试阶段顺序 (Requirements 4.2)
    INTERVIEW_STAGES = [
        "basic_info",      # 基本信息
        "interests",       # 兴趣爱好
        "skills",          # 技能水平
        "experience",      # 工作经验
        "goals",           # 职业目标
        "preferences"      # 工作偏好
    ]
    
    # 每个阶段的问题和示例 (Requirements 4.4)
    STAGE_QUESTIONS = {
        "basic_info": {
            "question": "请介绍一下您的基本情况，包括年龄、学历、专业背景等。",
            "examples": "例如：我今年25岁，本科毕业于XX大学计算机专业，目前在一家互联网公司工作。",
            "followup": "能否补充一下您的学历和专业背景？这对职业规划很重要。"
        },
        "interests": {
            "question": "您对哪些领域或技术方向感兴趣？平时喜欢做什么？",
            "examples": "例如：我对人工智能和数据分析很感兴趣，平时喜欢研究新技术和参加技术社区活动。",
            "followup": "能具体说说您感兴趣的技术方向吗？比如前端、后端、AI、数据等。"
        },
        "skills": {
            "question": "请描述一下您目前掌握的技能，包括编程语言、工具、框架等。",
            "examples": "例如：熟练掌握Python和Java，了解React和Vue，使用过MySQL和MongoDB数据库。",
            "followup": "能详细说说您的技能熟练程度吗？哪些是精通的，哪些是了解的？"
        },
        "experience": {
            "question": "请介绍一下您的工作或项目经验。",
            "examples": "例如：有3年后端开发经验，主要负责电商系统的订单模块，参与过微服务架构改造项目。",
            "followup": "能补充一下您在项目中的具体职责和成果吗？"
        },
        "goals": {
            "question": "您的职业目标是什么？希望在未来3-5年达到什么样的职位或状态？",
            "examples": "例如：希望3年内成为技术专家或团队负责人，5年内能够独立带领团队完成大型项目。",
            "followup": "能具体说说您期望的职位级别或发展方向吗？"
        },
        "preferences": {
            "question": "您对工作有什么偏好？比如工作地点、公司类型、薪资期望、工作强度等。",
            "examples": "例如：希望在一线城市工作，偏好大厂或独角兽公司，期望年薪30万以上，能接受适度加班。",
            "followup": "能补充一下您对公司文化或工作环境的期望吗？"
        }
    }
    
    # 最小回答长度（用于判断回答是否充分）
    MIN_ANSWER_LENGTH = 10
    
    def __init__(self):
        """初始化职业规划服务"""
        self.context: CareerContext = CareerContext()
        self.current_stage: int = 0
        self.collected_info: Dict[str, Any] = {}
        self._needs_followup: bool = False
    
    def start_interview(self) -> str:
        """
        开始职业规划面试，返回第一个问题
        
        Requirements 4.1: 结构化面试，清晰进度指示
        
        Returns:
            str: 欢迎语和第一个问题
        """
        self.reset()
        
        welcome = "🎯 欢迎使用职业规划服务！\n\n"
        welcome += "我将通过几个问题了解您的情况，然后为您生成个性化的职业规划报告。\n"
        welcome += f"共 {len(self.INTERVIEW_STAGES)} 个问题，预计需要 5-10 分钟。\n\n"
        welcome += self._get_progress_bar() + "\n\n"
        welcome += self._get_current_question()
        
        return welcome
    
    def process_answer(self, answer: str) -> Tuple[bool, str]:
        """
        处理用户回答
        
        Requirements 4.3: 追问不完整的回答
        
        Args:
            answer: 用户的回答
            
        Returns:
            Tuple[bool, str]: (是否完成收集, 下一个问题或确认消息)
        """
        if self.current_stage >= len(self.INTERVIEW_STAGES):
            return True, "信息收集已完成！正在为您生成职业规划报告..."
        
        current_stage_name = self.INTERVIEW_STAGES[self.current_stage]
        
        # 检查回答是否充分
        if not self.is_answer_sufficient(current_stage_name, answer):
            if not self._needs_followup:
                self._needs_followup = True
                followup = self.generate_followup_question(current_stage_name, answer)
                return False, followup
        
        # 保存回答
        self._save_answer(current_stage_name, answer)
        self._needs_followup = False
        
        # 移动到下一阶段
        self.current_stage += 1
        
        # 检查是否完成
        if self.current_stage >= len(self.INTERVIEW_STAGES):
            return True, self._get_completion_message()
        
        # 返回下一个问题
        response = self._get_progress_bar() + "\n\n"
        response += self._get_current_question()
        return False, response
    
    def get_progress(self) -> float:
        """
        获取面试进度 (0.0 - 1.0)
        
        Requirements 4.1: 清晰进度指示
        
        Returns:
            float: 进度值，0.0 表示未开始，1.0 表示完成
        """
        if len(self.INTERVIEW_STAGES) == 0:
            return 0.0
        return self.current_stage / len(self.INTERVIEW_STAGES)
    
    def is_answer_sufficient(self, stage: str, answer: str) -> bool:
        """
        判断回答是否足够详细
        
        Requirements 4.3: 追问不完整的回答
        
        Args:
            stage: 当前阶段名称
            answer: 用户的回答
            
        Returns:
            bool: True 表示回答充分，False 表示需要追问
        """
        # 空回答或太短的回答需要追问
        if not answer or len(answer.strip()) < self.MIN_ANSWER_LENGTH:
            return False
        
        return True
    
    def generate_followup_question(self, stage: str, answer: str) -> str:
        """
        生成追问问题
        
        Requirements 4.3: 追问不完整的回答
        
        Args:
            stage: 当前阶段名称
            answer: 用户的回答
            
        Returns:
            str: 追问问题
        """
        stage_info = self.STAGE_QUESTIONS.get(stage, {})
        followup = stage_info.get("followup", "能否提供更多细节？")
        
        response = "📝 您的回答有点简短，"
        response += followup + "\n\n"
        response += f"💡 {stage_info.get('examples', '')}"
        
        return response
    
    def build_report_prompt(self) -> str:
        """
        构建报告生成的提示词
        
        Returns:
            str: 用于 AI 生成报告的提示词
        """
        prompt = "请根据以下用户信息生成一份详细的职业规划报告：\n\n"
        prompt += "## 用户信息\n\n"
        
        stage_names = {
            "basic_info": "基本信息",
            "interests": "兴趣爱好",
            "skills": "技能水平",
            "experience": "工作经验",
            "goals": "职业目标",
            "preferences": "工作偏好"
        }
        
        for stage in self.INTERVIEW_STAGES:
            name = stage_names.get(stage, stage)
            value = getattr(self.context, stage, None) or "未提供"
            prompt += f"### {name}\n{value}\n\n"
        
        prompt += "\n## 报告要求\n\n"
        prompt += self.get_report_template()
        
        return prompt
    
    def get_report_template(self) -> str:
        """
        获取报告模板
        
        Requirements 5.1-5.9: 9 个标准化章节
        
        Returns:
            str: 报告模板说明
        """
        template = """请按照以下结构生成职业规划报告：

### 1. 执行摘要 (Executive Summary)
- 简要概述用户当前状况和主要建议
- 突出最重要的职业发展方向

### 2. 个人档案分析 (Personal Profile Analysis)
- 分析用户的背景、优势和特点
- 识别核心竞争力

### 3. 职业方向推荐 (Career Direction Recommendations)
- 推荐至少 3 个具体职位
- 每个职位包含：职位名称、所属行业、薪资范围、市场需求程度、职位描述、任职要求

### 4. 行业分析 (Industry Analysis)
- 分析推荐行业的市场趋势
- 提供数据支持的未来展望

### 5. 技能差距分析 (Skill Gap Analysis)
- 对比当前技能与目标职位要求
- 识别需要提升的关键技能

### 6. 学习路径 (Learning Path)
- 分类列出学习资源（免费/付费）
- 每个资源包含：名称、类型、链接（如有）、预计学习时间、优先级

### 7. 技术栈推荐 (Technology Stack Recommendations)
- 推荐需要学习的技术
- 每项技术包含：类别、名称、推荐理由、预计学习时间

### 8. 时间线和里程碑 (Timeline and Milestones)
- 短期目标（0-6个月）
- 中期目标（6-18个月）
- 长期目标（18个月以上）
- 每个里程碑包含：目标、时间范围、关键行动

### 9. 行动项 (Action Items)
- 列出优先级排序的具体行动
- 每个行动包含：优先级（1-5）、具体行动、截止时间、预期成果

请确保报告内容具体、可操作，并根据用户的实际情况进行个性化定制。"""
        
        return template
    
    def reset(self) -> None:
        """重置面试状态"""
        self.context = CareerContext()
        self.current_stage = 0
        self.collected_info = {}
        self._needs_followup = False
    
    def get_current_stage_name(self) -> Optional[str]:
        """获取当前阶段名称"""
        if self.current_stage >= len(self.INTERVIEW_STAGES):
            return None
        return self.INTERVIEW_STAGES[self.current_stage]
    
    def is_complete(self) -> bool:
        """检查面试是否完成"""
        return self.current_stage >= len(self.INTERVIEW_STAGES)
    
    # ==================== 私有方法 ====================
    
    def _get_current_question(self) -> str:
        """获取当前阶段的问题"""
        if self.current_stage >= len(self.INTERVIEW_STAGES):
            return ""
        
        stage = self.INTERVIEW_STAGES[self.current_stage]
        stage_info = self.STAGE_QUESTIONS.get(stage, {})
        
        question = f"**问题 {self.current_stage + 1}/{len(self.INTERVIEW_STAGES)}**\n\n"
        question += stage_info.get("question", "") + "\n\n"
        question += f"💡 {stage_info.get('examples', '')}"
        
        return question
    
    def _get_progress_bar(self) -> str:
        """生成进度条"""
        total = len(self.INTERVIEW_STAGES)
        completed = self.current_stage
        
        filled = "█" * completed
        empty = "░" * (total - completed)
        percentage = int(self.get_progress() * 100)
        
        return f"进度: [{filled}{empty}] {percentage}% ({completed}/{total})"
    
    def _save_answer(self, stage: str, answer: str) -> None:
        """保存用户回答到上下文"""
        setattr(self.context, stage, answer)
        self.collected_info[stage] = answer
    
    def _get_completion_message(self) -> str:
        """获取完成消息"""
        message = "✅ 信息收集完成！\n\n"
        message += self._get_progress_bar() + "\n\n"
        message += "感谢您的耐心回答！我正在根据您提供的信息生成个性化职业规划报告...\n"
        message += "报告将包含职位推荐、技能发展路径、学习资源等内容。"
        
        return message


class CareerReportBuilder:
    """
    职业报告构建器
    
    用于构建和验证职业规划报告结构
    Requirements 5.1-5.9
    """
    
    @staticmethod
    def create_sample_report() -> CareerReport:
        """
        创建示例报告结构
        
        用于测试和演示报告格式
        """
        return CareerReport(
            executive_summary="这是执行摘要示例...",
            personal_profile="这是个人档案分析示例...",
            career_directions=[
                CareerDirection(
                    position="高级后端工程师",
                    industry="互联网/软件",
                    salary_range="30-50万/年",
                    demand_level="高",
                    description="负责后端系统架构设计和核心模块开发",
                    requirements=["3年以上后端开发经验", "熟悉分布式系统", "良好的系统设计能力"]
                ),
                CareerDirection(
                    position="技术经理",
                    industry="互联网/软件",
                    salary_range="40-60万/年",
                    demand_level="中",
                    description="带领技术团队完成产品研发",
                    requirements=["5年以上开发经验", "团队管理经验", "良好的沟通能力"]
                ),
                CareerDirection(
                    position="架构师",
                    industry="互联网/软件",
                    salary_range="50-80万/年",
                    demand_level="中",
                    description="负责系统整体架构设计和技术选型",
                    requirements=["8年以上开发经验", "大型系统架构经验", "技术视野广阔"]
                )
            ],
            industry_analysis="互联网行业持续发展，技术人才需求旺盛...",
            skill_gap_analysis="当前技能与目标职位的差距分析...",
            learning_path=LearningPath(
                free_resources=[
                    LearningResource(
                        name="系统设计入门",
                        type="课程",
                        url="https://example.com/course1",
                        estimated_time="20小时",
                        priority="必学"
                    )
                ],
                paid_resources=[
                    LearningResource(
                        name="高级架构师认证",
                        type="认证",
                        url="https://example.com/cert1",
                        estimated_time="100小时",
                        priority="推荐"
                    )
                ]
            ),
            tech_stack=[
                TechRecommendation(
                    category="编程语言",
                    name="Go",
                    reason="高性能后端开发首选",
                    learning_time="2-3个月"
                ),
                TechRecommendation(
                    category="框架",
                    name="Kubernetes",
                    reason="容器编排标准",
                    learning_time="1-2个月"
                )
            ],
            timeline=Timeline(
                short_term=[
                    Milestone(
                        goal="掌握 Go 语言基础",
                        timeframe="0-3个月",
                        key_actions=["完成 Go 官方教程", "实现 2 个小项目"]
                    )
                ],
                mid_term=[
                    Milestone(
                        goal="获得高级工程师职位",
                        timeframe="6-12个月",
                        key_actions=["准备面试", "优化简历", "积累项目经验"]
                    )
                ],
                long_term=[
                    Milestone(
                        goal="晋升为技术经理",
                        timeframe="2-3年",
                        key_actions=["培养领导力", "扩展技术视野", "建立行业人脉"]
                    )
                ]
            ),
            action_items=[
                ActionItem(
                    priority=1,
                    action="开始学习 Go 语言",
                    deadline="本周内",
                    expected_outcome="完成环境搭建和基础语法学习"
                ),
                ActionItem(
                    priority=2,
                    action="更新简历",
                    deadline="两周内",
                    expected_outcome="突出项目经验和技术能力"
                )
            ]
        )
    
    @staticmethod
    def validate_report(report: CareerReport) -> Tuple[bool, List[str]]:
        """
        验证报告是否包含所有必需章节
        
        Requirements 5.1-5.9
        
        Args:
            report: 待验证的报告
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 缺失章节列表)
        """
        missing = []
        
        if not report.executive_summary:
            missing.append("执行摘要 (5.1)")
        if not report.personal_profile:
            missing.append("个人档案分析 (5.2)")
        if len(report.career_directions) < 3:
            missing.append("职业方向推荐 - 至少3个 (5.3)")
        if not report.industry_analysis:
            missing.append("行业分析 (5.4)")
        if not report.skill_gap_analysis:
            missing.append("技能差距分析 (5.5)")
        if not report.learning_path.free_resources and not report.learning_path.paid_resources:
            missing.append("学习路径 (5.6)")
        if not report.tech_stack:
            missing.append("技术栈推荐 (5.7)")
        if not report.timeline.short_term and not report.timeline.mid_term and not report.timeline.long_term:
            missing.append("时间线和里程碑 (5.8)")
        if not report.action_items:
            missing.append("行动项 (5.9)")
        
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_career_direction(direction: CareerDirection) -> Tuple[bool, List[str]]:
        """
        验证职业方向是否包含所有必需字段
        
        Requirements 4.6
        
        Args:
            direction: 待验证的职业方向
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 缺失字段列表)
        """
        missing = []
        
        if not direction.position:
            missing.append("职位名称")
        if not direction.industry:
            missing.append("行业")
        if not direction.salary_range:
            missing.append("薪资范围")
        if not direction.demand_level:
            missing.append("需求水平")
        if not direction.description:
            missing.append("职位描述")
        if not direction.requirements:
            missing.append("任职要求")
        
        return len(missing) == 0, missing
