#!/usr/bin/python
"""
检查机器狗状态
读取机器狗的实时状态信息
"""

import sys
import time

if len(sys.argv) < 2:
    print("用法: sudo python3 check_robot_state.py <网络接口>")
    print("示例: sudo python3 check_robot_state.py enp5s0")
    sys.exit(1)

network_interface = sys.argv[1]

print("=" * 70)
print("Go2 机器狗状态检查")
print("=" * 70)

try:
    print("\n[1/4] 导入库...")
    from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
    print("   ✅ 成功")
    
    print("\n[2/4] 初始化通信...")
    ChannelFactoryInitialize(0, network_interface)
    print("   ✅ 成功")
    
    print("\n[3/4] 订阅机器狗状态...")
    
    state_received = False
    latest_state = None
    
    def state_handler(msg: SportModeState_):
        global state_received, latest_state
        state_received = True
        latest_state = msg
    
    # 订阅机器狗状态话题
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub.Init(state_handler, 1)
    print("   ✅ 已订阅状态话题")
    
    print("\n[4/4] 等待接收机器狗状态数据...")
    print("   (最多等待10秒...)")
    
    timeout = 10
    start_time = time.time()
    
    while not state_received and (time.time() - start_time) < timeout:
        time.sleep(0.1)
    
    if state_received and latest_state:
        print("   ✅ 成功接收到状态数据！")
        
        print("\n" + "=" * 70)
        print("机器狗状态信息")
        print("=" * 70)
        
        # 显示关键状态
        print(f"\n【基本状态】")
        print(f"  时间戳: {latest_state.stamp}")
        print(f"  错误代码: {latest_state.error_code}")
        
        print(f"\n【模式状态】")
        print(f"  Gait 状态: {latest_state.gait_type}")
        print(f"  模式: {latest_state.mode}")
        print(f"  进度: {latest_state.progress}")
        
        print(f"\n【位置信息】")
        print(f"  X坐标: {latest_state.position[0]:.3f} m")
        print(f"  Y坐标: {latest_state.position[1]:.3f} m")
        print(f"  高度: {latest_state.body_height:.3f} m")
        
        print(f"\n【速度信息】")
        print(f"  前后速度: {latest_state.velocity[0]:.3f} m/s")
        print(f"  左右速度: {latest_state.velocity[1]:.3f} m/s")
        print(f"  旋转速度: {latest_state.yaw_speed:.3f} rad/s")
        
        print(f"\n【姿态信息】")
        print(f"  Roll: {latest_state.imu_state.rpy[0]:.3f} rad")
        print(f"  Pitch: {latest_state.imu_state.rpy[1]:.3f} rad")
        print(f"  Yaw: {latest_state.imu_state.rpy[2]:.3f} rad")
        
        print(f"\n【足端力】")
        for i, force in enumerate(latest_state.foot_force):
            foot_name = ["右前", "右后", "左前", "左后"][i]
            print(f"  {foot_name}: {force:.1f} N")
        
        print(f"\n【足端位置抬起状态】")
        # foot_position_body 是12个float的一维数组，需要重组为4组x,y,z
        for i in range(4):
            foot_name = ["右前", "右后", "左前", "左后"][i]
            x = latest_state.foot_position_body[i*3]
            y = latest_state.foot_position_body[i*3 + 1]
            z = latest_state.foot_position_body[i*3 + 2]
            print(f"  {foot_name}: x={x:.3f}, y={y:.3f}, z={z:.3f} m")
        
        print("\n" + "=" * 70)
        print("诊断分析")
        print("=" * 70)
        
        # 分析状态
        if latest_state.error_code != 0:
            print(f"\n⚠️  错误代码: {latest_state.error_code}")
            print("   机器狗报告了错误状态")
        
        # 检查足端力
        total_force = sum(latest_state.foot_force)
        if total_force < 10:
            print("\n⚠️  足端力过低（总计 {:.1f}N）".format(total_force))
            print("   可能原因：")
            print("   1. 机器狗处于趴下/阻尼状态")
            print("   2. 机器狗未站立")
            print("   → 尝试：用手机App或遥控器让机器狗先站立")
        elif total_force > 150:
            print(f"\n✅ 足端力正常（总计 {total_force:.1f}N）- 机器狗已站立")
        
        # 检查模式
        if latest_state.mode == 0:
            print("\n⚠️  模式为 0 - 可能在阻尼/待机模式")
            print("   → 需要激活Sport Mode")
        
        print("\n" + "=" * 70)
        print("建议操作")
        print("=" * 70)
        
        print("\n如果机器狗无法控制，请尝试：")
        print("\n1. 用手机App连接机器狗")
        print("   - 确认机器狗在 Sport Mode")
        print("   - 不在锁定(Locked)状态")
        print("   - 电量充足（>20%）")
        
        print("\n2. 用遥控器控制机器狗")
        print("   - 先用遥控器让机器狗站立")
        print("   - 确认遥控器控制正常")
        print("   - 然后再尝试SDK控制")
        
        print("\n3. 按机器狗的电源按钮")
        print("   - 单击：切换模式")
        print("   - 让机器狗自己站起来")
        
        print("\n4. 重启机器狗")
        print("   - 完全关机再开机")
        print("   - 等待系统完全启动（约30秒）")
        
        print("\n" + "=" * 70)
        
    else:
        print("   ❌ 未接收到状态数据")
        print("\n" + "=" * 70)
        print("问题分析")
        print("=" * 70)
        print("\n可能的原因：")
        print("  1. 机器狗未开机")
        print("  2. 机器狗的状态广播服务未运行")
        print("  3. 网络连接问题")
        print("  4. DDS话题订阅失败")
        
        print("\n建议：")
        print("  1. 确认机器狗已开机（LED灯亮）")
        print("  2. 重启机器狗")
        print("  3. 检查网络连接：ping 192.168.123.161")
        print("  4. 用手机App连接，确认机器狗正常")
        
except KeyboardInterrupt:
    print("\n\n用户中断")
    
except Exception as e:
    print(f"\n\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n可能的原因：")
    print("  1. 未使用sudo运行")
    print("  2. 机器狗未开机")
    print("  3. 网络配置问题")

print("\n✅ 程序结束")





