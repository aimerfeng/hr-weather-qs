@echo off
chcp 65001 >nul
echo ========================================
echo 智能助手 - 终端版本 安装脚本
echo ========================================
echo.

echo [1/2] 正在安装依赖...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ 安装失败！请检查 Python 和 pip 是否正确安装。
    pause
    exit /b 1
)

echo.
echo [2/2] 验证安装...
python -c "import openai, requests, rich, pydantic; print('✓ 所有依赖已成功安装')"

if %errorlevel% neq 0 (
    echo.
    echo ❌ 验证失败！某些依赖可能未正确安装。
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 运行方式：
echo   python -m terminal.main
echo.
echo 或者直接运行：
echo   run.bat
echo.
pause
