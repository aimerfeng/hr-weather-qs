# 🚀 部署指南

本文档介绍如何将智能助手部署到 Vercel。

## 📋 前置要求

- GitHub 账号
- Vercel 账号（可以使用 GitHub 登录）
- 已将代码推送到 GitHub 仓库

## 🌐 Vercel 部署步骤

### 方式一：通过 Vercel 网站（推荐）

1. **访问 Vercel**
   - 打开 [vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "New Project"
   - 选择您的 GitHub 仓库 `hr-weather-qs`
   - 点击 "Import"

3. **配置项目**
   - **Project Name**: `ai-assistant-agent`（或自定义名称）
   - **Framework Preset**: 选择 "Other"
   - **Root Directory**: 设置为 `web`（重要！）
   - **Build Command**: 留空
   - **Output Directory**: 留空
   - **Install Command**: `pip install -r requirements.txt`

4. **环境变量（可选）**
   
   如果需要设置默认配置，可以添加以下环境变量：
   - `DEFAULT_API_BASE_URL`: 默认 API 地址
   - `DEFAULT_MODEL`: 默认模型名称
   
   注意：用户仍然可以在前端设置中修改这些配置。

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（通常需要 1-2 分钟）
   - 部署成功后会显示访问链接

6. **访问应用**
   - 点击访问链接或复制 URL
   - 例如：`https://ai-assistant-agent.vercel.app`

### 方式二：通过 Vercel CLI

1. **安装 Vercel CLI**
```bash
npm install -g vercel
```

2. **登录 Vercel**
```bash
vercel login
```

3. **进入 web 目录**
```bash
cd web
```

4. **部署到预览环境**
```bash
vercel
```

5. **部署到生产环境**
```bash
vercel --prod
```

## ⚙️ 配置说明

### vercel.json 配置

项目已包含 `web/vercel.json` 配置文件：

```json
{
  "version": 2,
  "name": "ai-assistant-agent",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### 依赖说明

`web/requirements.txt` 包含所有必需的 Python 依赖：

- `fastapi` - Web 框架
- `openai` - AI API 客户端
- `requests` - HTTP 请求
- `pydantic` - 数据验证
- `uvicorn` - ASGI 服务器

## 🔧 首次使用

部署成功后，用户需要配置 API：

1. **访问部署的网站**
2. **点击右上角设置按钮（齿轮图标）**
3. **配置 API**：
   - 选择 AI 提供商（OpenAI / DeepSeek / 通义千问）
   - 输入 API Key
   - 选择模型
4. **测试连接**：点击"测试连接"按钮验证配置
5. **保存设置**：配置会保存在浏览器 localStorage 中

## 📝 获取 API Key

### OpenAI
- 访问：https://platform.openai.com/api-keys
- 注册/登录账号
- 创建新的 API Key
- 复制 Key（格式：`sk-...`）

### DeepSeek
- 访问：https://platform.deepseek.com/
- 注册/登录账号
- 在 API Keys 页面创建新 Key
- 复制 Key

### 通义千问 (Qwen)
- 访问：https://dashscope.aliyuncs.com/
- 注册/登录阿里云账号
- 开通 DashScope 服务
- 创建 API Key
- 复制 Key

## 🔄 自动部署

Vercel 支持自动部署：

1. **推送到 GitHub**
```bash
git add .
git commit -m "更新内容"
git push origin main
```

2. **自动触发部署**
   - Vercel 会自动检测到 GitHub 的更新
   - 自动开始构建和部署
   - 部署完成后自动更新网站

3. **查看部署状态**
   - 在 Vercel Dashboard 查看部署日志
   - 每次部署都会生成唯一的预览 URL

## 🌍 自定义域名

1. **在 Vercel Dashboard 中**
   - 选择您的项目
   - 进入 "Settings" → "Domains"
   - 点击 "Add Domain"

2. **添加域名**
   - 输入您的域名（例如：`assistant.yourdomain.com`）
   - 按照提示配置 DNS 记录

3. **DNS 配置**
   - 添加 CNAME 记录指向 Vercel
   - 等待 DNS 生效（通常几分钟到几小时）

4. **HTTPS**
   - Vercel 自动提供免费的 SSL 证书
   - 域名配置完成后自动启用 HTTPS

## 🐛 故障排除

### 部署失败

**问题**：部署时出现错误

**解决方案**：
1. 检查 `web/requirements.txt` 中的依赖版本
2. 确保 Root Directory 设置为 `web`
3. 查看 Vercel 部署日志中的详细错误信息
4. 确认 Python 版本兼容（Vercel 使用 Python 3.9）

### 404 错误

**问题**：访问页面显示 404

**解决方案**：
1. 确认 Root Directory 设置为 `web`
2. 检查 `vercel.json` 路由配置
3. 确认静态文件在 `web/static/` 目录下

### API 连接失败

**问题**：前端无法连接到 API

**解决方案**：
1. 检查浏览器控制台的错误信息
2. 确认 API Key 是否正确
3. 测试 API 端点：访问 `https://your-domain.vercel.app/health`
4. 检查 CORS 配置

### 冷启动慢

**问题**：首次请求响应很慢

**说明**：
- Vercel Serverless 函数有冷启动时间
- 首次请求可能需要 3-5 秒
- 后续请求会快很多
- 这是 Serverless 架构的正常现象

### 超时错误

**问题**：请求超时

**解决方案**：
1. Vercel 免费版函数执行时间限制为 10 秒
2. Pro 版本可以延长到 60 秒
3. 如果经常超时，考虑升级 Vercel 计划
4. 或优化代码减少执行时间

## 📊 监控和日志

### 查看日志

1. **Vercel Dashboard**
   - 进入项目
   - 点击 "Deployments"
   - 选择具体的部署
   - 查看 "Build Logs" 和 "Function Logs"

2. **实时日志**
```bash
vercel logs
```

### 性能监控

Vercel 提供内置的性能监控：
- 访问 Dashboard → Analytics
- 查看请求数量、响应时间等指标
- 免费版有基础监控
- Pro 版有更详细的分析

## 💰 费用说明

### Vercel 免费版限制

- ✅ 无限部署
- ✅ 自动 HTTPS
- ✅ 100GB 带宽/月
- ✅ 函数执行时间：10 秒
- ✅ 函数内存：1024MB

### 升级建议

如果遇到以下情况，建议升级到 Pro 版：
- 流量超过 100GB/月
- 需要更长的函数执行时间
- 需要更详细的分析数据
- 需要团队协作功能

## 🔐 安全建议

1. **API Key 安全**
   - API Key 仅保存在用户浏览器中
   - 不要在代码中硬编码 API Key
   - 不要将 API Key 提交到 Git

2. **CORS 配置**
   - 生产环境建议限制允许的域名
   - 修改 `web/api/index.py` 中的 CORS 配置

3. **环境变量**
   - 敏感信息使用 Vercel 环境变量
   - 不要在前端暴露敏感信息

## 📚 相关资源

- [Vercel 文档](https://vercel.com/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [项目 GitHub](https://github.com/aimerfeng/hr-weather-qs)

## 🆘 获取帮助

如果遇到问题：

1. 查看本文档的故障排除部分
2. 查看 Vercel 部署日志
3. 查看浏览器控制台错误
4. 在 GitHub 提交 Issue
5. 查看 Vercel 社区论坛

---

祝您部署顺利！🎉
