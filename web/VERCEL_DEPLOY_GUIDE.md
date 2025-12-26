# Vercel 部署完整指南

本指南提供两种部署方法，推荐使用方法一（CLI）。

## 方法一：使用 Vercel CLI（推荐）⭐

这是最可靠的部署方法，可以避免网页界面的配置问题。

### 前置要求

- 已安装 Node.js（https://nodejs.org/）
- 有 Vercel 账号（https://vercel.com）

### 步骤 1：安装 Vercel CLI

打开命令行（Windows 用 PowerShell 或 CMD，Mac/Linux 用 Terminal）：

```bash
npm install -g vercel
```

验证安装：
```bash
vercel --version
```

### 步骤 2：登录 Vercel

```bash
vercel login
```

会打开浏览器，选择登录方式（GitHub/GitLab/Bitbucket/Email）。

### 步骤 3：进入项目目录

```bash
# 进入项目根目录
cd /path/to/hr-weather-qs

# 进入 web 目录
cd web
```

### 步骤 4：首次部署（预览环境）

```bash
vercel
```

按照提示操作：

```
? Set up and deploy "~/hr-weather-qs/web"? [Y/n] 
→ 输入 Y 并回车

? Which scope do you want to deploy to?
→ 选择您的账号（使用方向键选择，回车确认）

? Link to existing project? [y/N]
→ 输入 N 并回车（第一次部署）

? What's your project's name?
→ 输入 ai-assistant-agent 或其他名称，回车

? In which directory is your code located?
→ 直接回车（使用当前目录 ./）
```

等待部署完成（约 1-2 分钟），会显示：

```
✅  Production: https://ai-assistant-agent-xxx.vercel.app [copied to clipboard]
```

### 步骤 5：部署到生产环境

预览环境测试通过后，部署到生产环境：

```bash
vercel --prod
```

完成后会得到生产环境 URL：
```
✅  Production: https://ai-assistant-agent.vercel.app
```

### 步骤 6：配置自定义域名（可选）

在 Vercel Dashboard 中：
1. 进入项目设置
2. 点击 "Domains"
3. 添加您的域名
4. 按照提示配置 DNS

---

## 方法二：使用 Vercel 网页界面

### 步骤 1：访问 Vercel

打开 https://vercel.com 并登录。

### 步骤 2：导入项目

1. 点击 "Add New..." → "Project"
2. 选择 "Import Git Repository"
3. 选择您的 GitHub 仓库 `aimerfeng/hr-weather-qs`
4. 点击 "Import"

### 步骤 3：配置项目

**重要配置项：**

| 配置项 | 值 | 说明 |
|--------|-----|------|
| Framework Preset | **Other** | 不要选 FastAPI！ |
| Root Directory | **web** | 必须设置 |
| Build Command | 留空 | 不需要构建 |
| Output Directory | 留空 | 不需要输出目录 |
| Install Command | `pip install -r requirements.txt` | 自动填充 |

**注意：** 
- ⚠️ Framework Preset 选择 "Other" 而不是 "FastAPI"
- ⚠️ Root Directory 必须设置为 "web"

### 步骤 4：环境变量（可选）

如果需要设置默认 API 配置，添加环境变量：

| Key | Value | 说明 |
|-----|-------|------|
| `DEFAULT_API_BASE_URL` | `https://api.openai.com/v1` | 默认 API 地址 |
| `DEFAULT_MODEL` | `gpt-3.5-turbo` | 默认模型 |

### 步骤 5：部署

点击 "Deploy" 按钮，等待部署完成（约 2-3 分钟）。

---

## 验证部署

部署成功后，访问您的 URL：

### 1. 检查 API 健康状态

访问：`https://your-domain.vercel.app/health`

应该返回：
```json
{
  "status": "healthy",
  "service": "ai-assistant-agent",
  "version": "1.0.0"
}
```

### 2. 访问主页

访问：`https://your-domain.vercel.app/`

应该看到聊天界面。

### 3. 测试 API 文档

访问：`https://your-domain.vercel.app/docs`

应该看到 FastAPI 自动生成的 API 文档。

---

## 常见问题

### Q1: 部署失败，提示 "No fastapi entrypoint found"

**解决方案：**
1. 确认 Root Directory 设置为 `web`
2. 确认 Framework Preset 选择 "Other" 而不是 "FastAPI"
3. 检查 `web/index.py` 文件是否存在
4. 尝试使用 CLI 部署（方法一）

### Q2: 部署成功但访问 404

**解决方案：**
1. 检查 `web/vercel.json` 配置
2. 确认 `web/index.py` 文件存在
3. 查看 Vercel 部署日志中的错误信息

### Q3: API 调用失败

**解决方案：**
1. 在前端设置中配置正确的 API Key
2. 检查浏览器控制台的错误信息
3. 确认 API Key 有效且有足够额度

### Q4: 静态文件无法访问

**解决方案：**
1. 确认 `web/static/` 目录存在
2. 检查 `web/vercel.json` 中的路由配置
3. 尝试访问 `/static/index.html` 直接路径

### Q5: 部署后代码更新没有生效

**解决方案：**
1. 确认代码已推送到 GitHub
2. 在 Vercel Dashboard 中手动触发重新部署
3. 清除浏览器缓存

---

## 自动部署

配置完成后，每次推送到 GitHub 的 `main` 分支，Vercel 会自动部署：

```bash
git add .
git commit -m "更新内容"
git push origin main
```

Vercel 会自动：
1. 检测到 GitHub 更新
2. 开始构建
3. 部署到生产环境
4. 发送部署通知邮件

---

## 查看部署日志

### CLI 方式

```bash
vercel logs
```

### 网页方式

1. 访问 https://vercel.com/dashboard
2. 选择您的项目
3. 点击 "Deployments"
4. 选择具体的部署
5. 查看 "Build Logs" 和 "Function Logs"

---

## 回滚部署

如果新版本有问题，可以快速回滚：

### CLI 方式

```bash
vercel rollback
```

### 网页方式

1. 进入项目的 Deployments 页面
2. 找到之前成功的部署
3. 点击 "..." → "Promote to Production"

---

## 删除部署

如果需要删除项目：

### CLI 方式

```bash
vercel remove ai-assistant-agent
```

### 网页方式

1. 进入项目设置
2. 滚动到底部
3. 点击 "Delete Project"
4. 输入项目名称确认

---

## 性能优化建议

1. **启用缓存**：静态文件会自动缓存
2. **使用 CDN**：Vercel 自动使用全球 CDN
3. **监控性能**：在 Dashboard 查看 Analytics
4. **升级套餐**：如果流量大，考虑升级到 Pro

---

## 获取帮助

- **Vercel 文档**：https://vercel.com/docs
- **项目 Issues**：https://github.com/aimerfeng/hr-weather-qs/issues
- **Vercel 社区**：https://github.com/vercel/vercel/discussions

---

## 总结

推荐使用 **方法一（CLI）** 进行部署，因为：
- ✅ 配置更可靠
- ✅ 错误信息更清晰
- ✅ 可以本地测试
- ✅ 更容易调试

如果遇到问题，请查看部署日志并参考常见问题部分。

祝您部署顺利！🚀
