# 智能助手 - Web 版本

基于 FastAPI 和 Vercel Serverless 的 Web 版本智能助手。

## 功能特性

- 🌐 Web 界面 - 美观的聊天界面
- 🔄 流式输出 - SSE 实时显示响应
- 🌤️ 天气查询 - 实时天气和预报
- 💼 职业规划 - 深度职业规划服务
- ⚙️ 灵活配置 - 支持多种 AI 提供商

## 本地开发

### 安装依赖

```bash
cd web
pip install -r requirements.txt
```

### 运行开发服务器

```bash
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 查看界面。

### API 文档

启动服务器后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Vercel 部署

### 方式一：通过 Vercel CLI

1. **安装 Vercel CLI**
```bash
npm install -g vercel
```

2. **登录 Vercel**
```bash
vercel login
```

3. **部署**
```bash
cd web
vercel
```

4. **生产部署**
```bash
vercel --prod
```

### 方式二：通过 GitHub 集成

1. **推送代码到 GitHub**
```bash
git add .
git commit -m "feat: 完成 Web 版本实现"
git push origin main
```

2. **在 Vercel 中导入项目**
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 选择您的 GitHub 仓库
   - 设置根目录为 `web`
   - 点击 "Deploy"

3. **配置环境变量（可选）**
   - `DEFAULT_API_BASE_URL`: 默认 API 地址
   - `DEFAULT_MODEL`: 默认模型名称

### 部署配置

项目包含以下配置文件：

- `vercel.json` - Vercel 部署配置
- `requirements.txt` - Python 依赖
- `api/index.py` - FastAPI 应用入口

## 项目结构

```
web/
├── api/                    # API 端点
│   ├── __init__.py
│   ├── index.py            # 主入口
│   ├── chat.py             # 聊天 API
│   ├── weather.py          # 天气 API
│   └── config.py           # 配置 API
├── lib/                    # 共享库
│   ├── __init__.py
│   ├── agent.py            # 代理核心
│   ├── config_manager.py   # 配置管理
│   ├── career_planner.py   # 职业规划
│   ├── weather_service.py  # 天气服务
│   └── models.py           # 数据模型
├── static/                 # 静态资源
│   ├── index.html          # 主页面
│   ├── styles.css          # 样式表
│   └── app.js              # 前端逻辑
├── vercel.json             # Vercel 配置
├── requirements.txt        # 依赖列表
└── README.md               # 本文件
```

## API 端点

### 聊天 API

- `POST /api/chat` - 发送消息，返回 SSE 流

### 天气 API

- `GET /api/weather/{city}` - 获取城市天气
- `GET /api/forecast/{city}` - 获取天气预报
- `GET /api/history` - 获取查询历史
- `DELETE /api/history` - 清空历史记录

### 配置 API

- `POST /api/config/test` - 测试 API 配置
- `GET /api/config/presets` - 获取预设提供商
- `POST /api/config/validate` - 验证配置

### 健康检查

- `GET /health` - 全局健康检查
- `GET /api/chat/health` - 聊天 API 健康检查
- `GET /api/weather/health` - 天气 API 健康检查
- `GET /api/config/health` - 配置 API 健康检查

## 使用说明

### 首次使用

1. 访问部署后的网站
2. 点击右上角设置按钮
3. 选择 AI 提供商
4. 输入 API Key
5. 选择模型
6. 点击"测试连接"验证配置
7. 点击"保存设置"

### 天气查询

在聊天框中输入：
- "北京天气"
- "上海明天天气"
- "深圳天气预报"

### 职业规划

在聊天框中输入：
- "我想做职业规划"
- "帮我规划职业发展"

程序会通过6个问题了解您的情况，然后生成详细报告。

### 通用问答

直接输入您的问题：
- "Python 怎么学习"
- "推荐一些编程书籍"

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **前端**: HTML5, CSS3, JavaScript (原生)
- **AI**: OpenAI SDK
- **部署**: Vercel Serverless
- **天气**: wttr.in API

## 注意事项

1. **API Key 安全**: API Key 仅保存在用户浏览器的 localStorage 中，不会发送到服务器存储
2. **Serverless 限制**: Vercel Serverless 函数有执行时间限制（默认60秒）
3. **冷启动**: 首次请求可能需要几秒钟的冷启动时间
4. **CORS**: 已配置允许所有来源，生产环境建议限制具体域名

## 故障排除

### 部署失败

1. 检查 `requirements.txt` 中的依赖版本
2. 确保 Python 版本为 3.8+
3. 查看 Vercel 部署日志

### API 连接失败

1. 检查 API Key 是否正确
2. 检查 Base URL 是否正确
3. 检查网络连接
4. 查看浏览器控制台错误信息

### 天气查询失败

1. 检查城市名称拼写
2. 尝试使用英文城市名
3. 检查 wttr.in API 是否可访问

## 开发

### 添加新的 API 端点

1. 在 `api/` 目录创建新的路由文件
2. 在 `api/index.py` 中注册路由
3. 更新 `api/__init__.py`

### 修改前端

1. 编辑 `static/index.html` - HTML 结构
2. 编辑 `static/styles.css` - 样式
3. 编辑 `static/app.js` - 逻辑

### 测试

```bash
# 运行开发服务器
uvicorn api.index:app --reload

# 访问 API 文档
open http://localhost:8000/docs
```

## 许可证

MIT License

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vercel 文档](https://vercel.com/docs)
- [OpenAI API 文档](https://platform.openai.com/docs)
