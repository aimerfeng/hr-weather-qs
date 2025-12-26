# 📦 分发说明

## 打包内容

将整个 `terminal` 文件夹打包即可分发给用户。

### 包含的文件

```
terminal/
├── __init__.py          # Python 包初始化
├── main.py              # 主程序
├── agent.py             # 代理核心
├── config_manager.py    # 配置管理
├── career_planner.py    # 职业规划
├── weather_service.py   # 天气服务
├── models.py            # 数据模型
├── requirements.txt     # 依赖列表
├── README.md            # 使用说明
├── DISTRIBUTION.md      # 本文件
├── install.bat          # Windows 安装脚本
├── run.bat              # Windows 运行脚本
├── install.sh           # Linux/Mac 安装脚本
└── run.sh               # Linux/Mac 运行脚本
```

## 用户使用步骤

### Windows 用户

1. **解压文件夹**
2. **双击运行 `install.bat`** 安装依赖
3. **双击运行 `run.bat`** 启动程序

或者在命令行中：
```cmd
cd terminal
python -m pip install -r requirements.txt
python -m terminal.main
```

### Linux/Mac 用户

1. **解压文件夹**
2. **添加执行权限并安装**
```bash
cd terminal
chmod +x install.sh run.sh
./install.sh
```
3. **运行程序**
```bash
./run.sh
```

或者：
```bash
python3 -m pip install -r requirements.txt
python3 -m terminal.main
```

## 系统要求

- **Python 版本**: Python 3.8 或更高
- **网络连接**: 需要访问 AI API 和天气 API
- **操作系统**: Windows / Linux / macOS

## 依赖说明

所有依赖都在 `requirements.txt` 中列出：

```
openai>=1.0.0      # AI API 客户端
httpx>=0.23.0      # HTTP 客户端（openai 依赖）
distro>=1.7.0      # 系统信息（openai 依赖）
jiter>=0.10.0      # JSON 解析（openai 依赖）
sniffio>=1.3.0     # 异步检测（openai 依赖）
requests>=2.28.0   # HTTP 请求（天气 API）
rich>=13.0.0       # 终端美化
pydantic>=2.0.0    # 数据验证
```

## 配置要求

用户需要准备：

1. **AI API Key** - 从以下任一提供商获取：
   - OpenAI: https://platform.openai.com/api-keys
   - DeepSeek: https://platform.deepseek.com/
   - 通义千问: https://dashscope.aliyuncs.com/

2. **网络环境** - 确保可以访问 AI API（国内用户使用 OpenAI 可能需要代理）

## 首次运行

程序首次运行时会自动引导用户完成配置：

1. 选择 AI 提供商
2. 输入 API Key
3. 选择模型

配置会保存到 `data/config.json`，下次自动加载。

## 数据文件

程序运行时会在 `data/` 目录创建：

- `config.json` - API 配置（包含 API Key，请勿分享）
- `weather_history.json` - 天气查询历史

## 打包建议

### 方式一：ZIP 压缩包

```bash
# 打包整个 terminal 文件夹
zip -r terminal.zip terminal/
```

### 方式二：tar.gz 压缩包（Linux/Mac）

```bash
tar -czf terminal.tar.gz terminal/
```

### 方式三：7z 压缩包（推荐，跨平台）

```bash
7z a terminal.7z terminal/
```

## 注意事项

1. **不要包含 `data/` 文件夹** - 这是用户的配置和数据，每个用户应该有自己的
2. **不要包含 `__pycache__/`** - 这是 Python 缓存，会自动生成
3. **确保 README.md 清晰** - 用户主要看这个文件了解如何使用
4. **测试打包** - 在干净的环境中测试打包后的程序是否能正常运行

## 版本更新

更新版本时：

1. 修改 `__init__.py` 中的 `__version__`
2. 更新 `README.md` 中的更新日志
3. 重新打包分发

## 技术支持

建议在 README.md 中提供：

- 常见问题解答
- 联系方式（邮箱/GitHub）
- Issue 提交地址

## 许可证

建议添加 LICENSE 文件，推荐使用 MIT License。
