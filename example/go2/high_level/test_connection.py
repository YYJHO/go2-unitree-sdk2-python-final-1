#!/usr/bin/python
"""
简单的Go2连接测试程序
用于测试SDK2是否能正常连接机器狗
"""

import sys
import time

print("=" * 60)
print("Go2 连接测试程序")
print("=" * 60)

# 检查参数
if len(sys.argv) < 2:
    print("用法: sudo python3 test_connection.py <网络接口>")
    print("示例: sudo python3 test_connection.py enp5s0")
    sys.exit(1)

network_interface = sys.argv[1]
print(f"网络接口: {network_interface}")
print("=" * 60)

try:
    # 1. 导入库
    print("\n[1/5] 导入SDK库...")
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    print("   ✅ 成功")
    
    # 2. 初始化通信通道
    print("\n[2/5] 初始化DDS通信...")
    ChannelFactoryInitialize(0, network_interface)
    print("   ✅ 成功")
    
    # 3. 创建客户端
    print("\n[3/5] 创建SportClient...")
    client = SportClient()
    client.SetTimeout(10.0)
    print("   ✅ 成功")
    
    # 4. 初始化客户端
    print("\n[4/5] 连接机器狗...")
    client.Init()
    print("   ✅ 成功 - 已连接到机器狗！")
    time.sleep(1)
    
    # 5. 测试简单命令
    print("\n[5/5] 测试控制命令...")
    print("   发送站立命令...")
    client.StandUp()
    time.sleep(3)
    print("   ✅ 命令发送成功")
    
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅✅ 测试完成！SDK2连接正常！")
    print("=" * 60)
    print("\n机器狗应该已经站立起来了。")
    print("\n您现在可以使用其他控制程序：")
    print("  sudo python3 go2_keyboard_simple.py enp5s0")
    print("  sudo python3 go2_sport_client.py enp5s0")
    print("\n清理中...")
    
    client.StopMove()
    time.sleep(0.5)
    client.Damp()
    print("✅ 程序结束")
    
except ImportError as e:
    print(f"   ❌ 导入错误: {e}")
    print("\n可能的原因：")
    print("  1. SDK未正确安装")
    print("  2. 运行: pip3 install -e .")
    
except Exception as e:
    print(f"   ❌ 错误: {e}")
    print("\n可能的原因：")
    print("  1. 未使用sudo运行")
    print("  2. 网络接口名称错误")
    print("  3. 机器狗未开机或未连接")
    print("  4. DDS通信问题")
    print("\n调试信息：")
    import traceback
    traceback.print_exc()





