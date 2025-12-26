#!/bin/bash

echo "========================================"
echo "智能助手 - 终端版本 安装脚本"
echo "========================================"
echo ""

echo "[1/2] 正在安装依赖..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 安装失败！请检查 Python 和 pip 是否正确安装。"
    exit 1
fi

echo ""
echo "[2/2] 验证安装..."
python3 -c "import openai, requests, rich, pydantic; print('✓ 所有依赖已成功安装')"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 验证失败！某些依赖可能未正确安装。"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "运行方式："
echo "  python3 -m terminal.main"
echo ""
echo "或者直接运行："
echo "  ./run.sh"
echo ""
