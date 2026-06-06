#!/bin/bash

# Go2机器狗连接诊断脚本

echo "=========================================="
echo "Go2 机器狗连接诊断"
echo "=========================================="

# 1. 检查网络接口
echo -e "\n【1】网络接口状态"
ip link show enp5s0 | grep "state"

# 2. 检查IP地址
echo -e "\n【2】IP地址配置"
ip addr show enp5s0 | grep "inet " | grep -v "inet6"

# 检查机器狗IP
if ip addr show enp5s0 | grep -q "192.168.123"; then
    echo "  ✅ 机器狗网段IP已配置"
else
    echo "  ❌ 缺少机器狗网段IP (192.168.123.x)"
fi

# 3. 检查路由表
echo -e "\n【3】路由表"
ip route show | grep "192.168"

# 检查机器狗路由
if ip route show | grep -q "192.168.123.0/24"; then
    echo "  ✅ 机器狗路由已配置"
else
    echo "  ❌ 缺少机器狗路由"
fi

# 4. 测试ping
echo -e "\n【4】网络连通性测试"
echo -n "  测试机器狗 (192.168.123.161)... "
if timeout 3 ping -c 2 -W 2 192.168.123.161 &>/dev/null; then
    echo "✅ 成功"
    PING_OK=true
else
    echo "❌ 失败"
    PING_OK=false
fi

echo -n "  测试互联网 (8.8.8.8)... "
if timeout 3 ping -c 2 -W 2 8.8.8.8 &>/dev/null; then
    echo "✅ 成功"
else
    echo "❌ 失败"
fi

# 5. 检查DDS通信端口
echo -e "\n【5】DDS通信检查"
echo "  DDS使用UDP端口 7400-7600"
echo -n "  检查防火墙状态... "
if command -v ufw &> /dev/null; then
    STATUS=$(sudo ufw status 2>/dev/null | grep -i status | awk '{print $2}')
    if [ "$STATUS" == "active" ]; then
        echo "⚠️  防火墙开启 (可能阻止DDS通信)"
    else
        echo "✅ 防火墙关闭"
    fi
else
    echo "✅ 未安装ufw"
fi

# 6. 检查是否能解析机器狗
echo -e "\n【6】网络连接质量"
if $PING_OK; then
    ping -c 10 -i 0.2 192.168.123.161 2>&1 | tail -2
fi

echo -e "\n=========================================="
echo "诊断总结"
echo "=========================================="

# 综合判断
HAS_IP=$(ip addr show enp5s0 | grep -q "192.168.123" && echo true || echo false)
HAS_ROUTE=$(ip route show | grep -q "192.168.123.0/24" && echo true || echo false)

if $HAS_IP && $HAS_ROUTE && $PING_OK; then
    echo "✅ 网络配置正常"
    echo ""
    echo "如果仍然无法控制，可能的原因："
    echo "  1. 机器狗的运动服务未启动"
    echo "     → 用手机App检查机器狗状态"
    echo "  2. 需要用sudo运行控制程序"
    echo "     → sudo python3 go2_keyboard_simple.py enp5s0"
    echo "  3. DDS通信端口被阻止"
    echo "     → sudo ufw disable (临时关闭防火墙测试)"
    echo "  4. 机器狗处于低电量保护模式"
    echo "     → 给机器狗充电"
else
    echo "❌ 网络配置有问题"
    if ! $HAS_IP; then
        echo "  → 缺少机器狗IP，运行: sudo ip addr add 192.168.123.222/24 dev enp5s0"
    fi
    if ! $HAS_ROUTE; then
        echo "  → 缺少路由，运行: sudo ip route add 192.168.123.0/24 dev enp5s0"
    fi
    if ! $PING_OK; then
        echo "  → 无法ping通，检查机器狗是否开机、网线是否连接"
    fi
fi

echo "=========================================="





