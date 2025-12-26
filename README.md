# AI Assistant Agent 智能助手代理

基于 OpenAI Python SDK 的智能代理系统，提供天气查询和职业规划两大核心功能。

## 功能特性

- 🌤️ **实时天气查询**: 查询任意城市的当前天气和未来5天预报
- 📊 **天气历史记录**: 自动保存查询历史，快速访问常用城市
- 💼 **深度职业规划**: 通过结构化面试生成个性化职业规划报告
- 🔄 **流式输出**: 所有AI响应采用流式输出，提升用户体验
- ⚙️ **灵活配置**: 支持 OpenAI、DeepSeek、Qwen 等多种 AI 提供商

## 项目结构

```
ai-assistant-agent/
├── web/                    # Web 版本 (Vercel 部署)
│   ├── api/                # Serverless API 端点
│   ├── static/             # 静态资源 (HTML/CSS/JS)
│   └── lib/                # 共享库
├── terminal/               # 终端版本
├── tests/                  # 测试文件
│   ├── unit/               # 单元测试
│   └── property/           # 属性测试
├── requirements.txt        # 开发依赖
└── README.md
```

## 快速开始

### 环境要求

- Python 3.9+
- pip 包管理器

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/aimerfeng/hr-weather-qs.git
cd hr-weather-qs

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 终端版本

### 运行方式

```bash
cd terminal
pip install -r requirements.txt
python main.py
```

### 使用说明

启动后，直接在命令行输入消息与助手对话。输入 `exit` 或 `退出` 结束对话。

### 示例对话

```
欢迎使用智能助手！
我可以帮您查询天气或提供职业规划建议。
输入 'exit' 或 '退出' 结束对话。

您: 北京今天天气怎么样？

助手: 让我为您查询北京的天气信息...

北京当前天气：
🌡️ 温度: 25°C (体感 27°C)
💧 湿度: 60%
💨 风速: 10.5 km/h
☀️ 天气状况: 晴

未来5天预报：
- 周一: 20-28°C 晴
- 周二: 18-26°C 多云
- 周三: 15-22°C 小雨
...

您: 我想做职业规划

助手: 好的，我来帮您进行职业规划。首先，请告诉我一些基本信息：

1. 您目前的职业/专业是什么？
2. 您有多少年工作经验？

您: 我是计算机专业，工作3年了

助手: 了解了。接下来请告诉我：
- 您对哪些技术领域比较感兴趣？
- 您目前掌握了哪些技术技能？
...
```

## Web 版本

### 本地运行

```bash
cd web
pip install -r requirements.txt
uvicorn api.index:app --reload
```

访问 http://localhost:8000 查看界面。

### Vercel 部署

1. Fork 本仓库到您的 GitHub 账号
2. 在 Vercel 中导入项目
3. 配置环境变量（可选）:
   - `DEFAULT_API_BASE_URL`: 默认 API 地址
   - `DEFAULT_MODEL`: 默认模型名称
4. 部署完成后即可访问

### 界面说明

- **主聊天区**: 与助手对话的主要区域
- **侧边栏**: 显示天气时间表和查询历史
- **设置面板**: 点击右上角齿轮图标配置 API

## API 配置

支持以下 AI 提供商：

| 提供商 | API Base URL | 模型 |
|--------|--------------|------|
| OpenAI | https://api.openai.com/v1 | gpt-4, gpt-3.5-turbo |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| Qwen | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo, qwen-plus |

## 天气 API

本项目使用 [wttr.in](https://wttr.in) 免费天气 API，无需 API Key。

## 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行属性测试
pytest tests/property/

# 查看测试覆盖率
pytest --cov=terminal --cov=web
```

## 技术栈

- **后端**: Python, FastAPI, OpenAI SDK
- **前端**: HTML, CSS, JavaScript
- **测试**: pytest, hypothesis
- **部署**: Vercel Serverless

## License

MIT License
