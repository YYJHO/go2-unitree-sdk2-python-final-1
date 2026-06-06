#!/bin/bash
# Go2 Debug Window 依赖安装脚本

echo "======================================================================"
echo "Go2 Debug Window - 依赖安装"
echo "======================================================================"
echo ""

echo "正在安装依赖..."
echo ""

# 安装PySide2（免费的Qt官方Python绑定）
echo "[1/2] 安装 PySide2..."
pip3 install PySide2 --user
if [ $? -eq 0 ]; then
    echo "✅ PySide2 安装成功"
else
    echo "❌ PySide2 安装失败"
    exit 1
fi

echo ""

# 安装netifaces（网络接口检测）
echo "[2/2] 安装 netifaces..."
pip3 install netifaces --user
if [ $? -eq 0 ]; then
    echo "✅ netifaces 安装成功"
else
    echo "❌ netifaces 安装失败"
    exit 1
fi

echo ""
echo "======================================================================"
echo "✅ 所有依赖安装完成！"
echo "======================================================================"
echo ""
echo "现在可以运行："
echo "  python3 go2_debug_window.py --mock    # 调试模式"
echo "  python3 go2_debug_window.py           # 真实模式"
echo ""
echo "或键盘控制："
echo "  sudo python3 go2_keyboard_simple.py   # 需要sudo权限"
echo ""


