# 🌟 智能助手 - 终端版本

一个功能强大的命令行智能助手，支持天气查询、职业规划和通用问答。

## ✨ 功能特性

- 🌤️ **天气查询** - 查询任何城市的实时天气和未来5天预报
- 🎯 **职业规划** - 提供深度职业发展建议和个性化规划报告
- 💬 **通用问答** - 回答各种问题，提供信息和建议
- 🎨 **美观界面** - 彩色终端输出，流式显示响应
- 📝 **历史记录** - 自动保存天气查询历史

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 方式一：直接运行
```bash
python -m terminal.main
```

### 方式二：作为模块导入
```python
from terminal.main import run
run()
```

## ⚙️ 配置

首次运行时，程序会引导您完成 API 配置：

1. 选择 AI 提供商（OpenAI / DeepSeek / 通义千问 / 自定义）
2. 输入 API Key
3. 选择模型

配置会自动保存到 `data/config.json`，下次运行时自动加载。

### 支持的 AI 提供商

- **OpenAI** - GPT-4, GPT-3.5-turbo 等
- **DeepSeek** - deepseek-chat, deepseek-coder 等
- **通义千问 (Qwen)** - qwen-turbo, qwen-plus 等
- **自定义** - 任何兼容 OpenAI API 的服务

## 📖 使用说明

### 天气查询
```
您: 北京天气怎么样
您: 上海明天天气
您: 查询深圳的天气
```

### 职业规划
```
您: 我想做职业规划
您: 帮我规划职业发展
```

程序会通过6个问题了解您的情况，然后生成详细的职业规划报告。

### 通用问答
```
您: Python 怎么学习
您: 推荐一些好书
您: 如何提高编程能力
```

### 特殊命令

- `/help` - 显示帮助信息
- `/clear` - 清空对话历史
- `/config` - 重新配置 API
- `/history` - 显示天气查询历史
- `/cancel` - 取消当前职业规划面试
- `exit` / `quit` / `退出` - 结束对话

## 📁 文件结构

```
terminal/
├── __init__.py          # 包初始化
├── main.py              # 主程序入口
├── agent.py             # 代理核心逻辑
├── config_manager.py    # 配置管理
├── career_planner.py    # 职业规划服务
├── weather_service.py   # 天气查询服务
├── models.py            # 数据模型定义
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 🔧 依赖说明

- `openai` - OpenAI SDK，用于调用 AI API
- `requests` - HTTP 请求库，用于天气 API
- `rich` - 终端美化库，提供彩色输出
- `pydantic` - 数据验证库，用于数据模型
- `httpx`, `distro`, `jiter`, `sniffio` - OpenAI SDK 的依赖

## 📝 数据存储

程序会在 `data/` 目录下创建以下文件：

- `config.json` - API 配置
- `weather_history.json` - 天气查询历史（最多10条）

## 🌐 网络要求

- 需要访问 AI API（OpenAI / DeepSeek / Qwen 等）
- 需要访问天气 API（wttr.in）
- 如果在国内使用 OpenAI，可能需要代理

## ⚠️ 注意事项

1. **API Key 安全** - 请妥善保管您的 API Key，不要分享给他人
2. **网络连接** - 确保网络连接正常，某些 API 可能需要代理
3. **API 费用** - 使用 AI API 可能产生费用，请注意控制使用量
4. **天气数据** - 天气数据来自 wttr.in 免费 API，可能存在延迟

## 🐛 常见问题

### Q: 提示 "未安装 openai 库"
A: 运行 `pip install openai httpx distro jiter sniffio`

### Q: 连接超时或无法访问
A: 检查网络连接，如果使用 OpenAI 可能需要配置代理

### Q: API Key 无效
A: 检查 API Key 是否正确，是否已过期，是否有足够的额度

### Q: 找不到城市
A: 尝试使用英文城市名，或检查拼写是否正确

## 📄 许可证

MIT License

## 👨‍💻 作者

Your Name

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
