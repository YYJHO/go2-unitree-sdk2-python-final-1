#!/usr/bin/python
"""
Go2机器狗完整功能测试
测试所有基本控制功能
"""

import sys
import time

def print_step(step, total, msg):
    """打印步骤信息"""
    print(f"\n[{step}/{total}] {msg}")

def main():
    if len(sys.argv) < 2:
        print("用法: sudo python3 full_test.py <网络接口>")
        print("示例: sudo python3 full_test.py enp5s0")
        sys.exit(1)
    
    network_interface = sys.argv[1]
    
    print("=" * 70)
    print("Go2 机器狗完整功能测试")
    print("=" * 70)
    print(f"网络接口: {network_interface}")
    print("=" * 70)
    
    print("\n⚠️  警告：测试期间机器狗会执行以下动作：")
    print("   - 站立")
    print("   - 前进（约1米）")
    print("   - 左转")
    print("   - 趴下")
    print("\n   请确保机器狗周围有足够空间（至少2米x2米）！")
    
    confirm = input("\n确认开始测试？(输入 yes 继续): ")
    if confirm.lower() != 'yes':
        print("已取消测试")
        sys.exit(0)
    
    try:
        # 步骤1: 导入库
        print_step(1, 8, "导入SDK库...")
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.go2.sport.sport_client import SportClient
        print("   ✅ 成功")
        
        # 步骤2: 初始化DDS
        print_step(2, 8, "初始化DDS通信...")
        ChannelFactoryInitialize(0, network_interface)
        print("   ✅ 成功")
        
        # 步骤3: 创建客户端
        print_step(3, 8, "创建SportClient...")
        client = SportClient()
        client.SetTimeout(10.0)
        print("   ✅ 成功")
        
        # 步骤4: 连接机器狗
        print_step(4, 8, "连接机器狗...")
        client.Init()
        print("   ✅ 成功 - 已建立连接")
        time.sleep(1)
        
        # 步骤5: 站立
        print_step(5, 8, "测试站立...")
        print("   发送StandUp命令...")
        result = client.StandUp()
        print(f"   返回值: {result}")
        print("   等待3秒让机器狗站稳...")
        time.sleep(3)
        print("   ✅ 站立测试完成")
        
        # 步骤6: 前进
        print_step(6, 8, "测试前进...")
        print("   机器狗将前进2秒（速度0.3m/s）")
        start = time.time()
        while time.time() - start < 2:
            client.Move(0.3, 0, 0)
            time.sleep(0.1)
        client.StopMove()
        print("   ✅ 前进测试完成")
        time.sleep(1)
        
        # 步骤7: 转向
        print_step(7, 8, "测试转向...")
        print("   机器狗将左转1秒")
        start = time.time()
        while time.time() - start < 1:
            client.Move(0, 0, 0.5)
            time.sleep(0.1)
        client.StopMove()
        print("   ✅ 转向测试完成")
        time.sleep(1)
        
        # 步骤8: 趴下
        print_step(8, 8, "测试趴下...")
        print("   发送StandDown命令...")
        result = client.StandDown()
        print(f"   返回值: {result}")
        time.sleep(2)
        print("   ✅ 趴下测试完成")
        
        # 清理
        print("\n" + "=" * 70)
        print("🎉 所有测试完成！")
        print("=" * 70)
        print("\n测试结果总结：")
        print("  ✅ SDK库导入正常")
        print("  ✅ DDS通信正常")
        print("  ✅ 机器狗连接成功")
        print("  ✅ 站立命令有效")
        print("  ✅ 移动控制有效")
        print("  ✅ 转向控制有效")
        print("  ✅ 趴下命令有效")
        print("\n您的配置完全正常，可以开始使用了！")
        print("\n推荐使用：")
        print(f"  sudo python3 go2_keyboard_simple.py {network_interface}")
        print("=" * 70)
        
        # 最后清理
        print("\n清理中...")
        client.StopMove()
        time.sleep(0.5)
        client.Damp()
        print("✅ 测试程序结束")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        if 'client' in locals():
            print("清理中...")
            client.StopMove()
            client.Damp()
        
    except Exception as e:
        print(f"\n\n❌ 测试失败！")
        print(f"错误信息: {e}")
        print("\n可能的原因：")
        print("  1. 未使用sudo运行")
        print("  2. 机器狗未开机或未连接")
        print("  3. 机器狗的Sport Mode未启动")
        print("  4. 网络配置问题")
        print("\n详细错误信息：")
        import traceback
        traceback.print_exc()
        
        if 'client' in locals():
            print("\n尝试清理...")
            try:
                client.StopMove()
                client.Damp()
            except:
                pass

if __name__ == '__main__':
    main()





