#!/usr/bin/python
"""
Go2 简洁键盘控制
直接使用 SportClient，无额外封装
"""
import sys
import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: 'keyboard' 模块未安装")
    print("安装方法: pip install keyboard")
    print("运行需要sudo权限: sudo python3 go2_keyboard_simple.py")


def main():
    """主函数"""
    if not KEYBOARD_AVAILABLE:
        print("\nERROR: keyboard模块是必需的")
        print("请运行: pip install keyboard")
        return
    
    # 获取网络接口
    network_interface = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 60)
    print("Go2 简洁键盘控制 (直接使用SportClient)")
    print("=" * 60)
    if network_interface:
        print(f"网络接口: {network_interface}")
    else:
        print("网络接口: 默认")
        print("用法: python3 go2_keyboard_simple.py [network_interface]")
    print("=" * 60)
    
    print("\nWARNING: 确保机器人周围没有障碍物!")
    input("按Enter继续...")
    
    # 初始化
    if network_interface:
        ChannelFactoryInitialize(0, network_interface)
    else:
        ChannelFactoryInitialize(0)
    
    client = SportClient()
    client.SetTimeout(10.0)
    client.Init()
    print("✓ SportClient 初始化完成\n")
    time.sleep(0.5)
    
    # 状态变量
    is_standing = False
    speed = 0.3  # 默认速度
    
    # 显示控制说明
    print("=" * 60)
    print("控制说明:")
    print("  移动: w(前) s(后) a(左) d(右) j(左转) l(右转)")
    print("  组合: w+a(斜前左) w+d(斜前右) 等")
    print("  状态: Space(站立) c(趴下) x(停止) r(恢复) 0(阻尼)")
    print("  速度: +(增) -(减)")
    print("  退出: q")
    print("=" * 60)
    print(f"当前速度: {speed:.1f} m/s")
    print("\n✨ 支持组合按键：可以同时按住多个方向键！")
    print("注意: 需要sudo权限捕获键盘")
    print("如果按键无效，请尝试: sudo python3 go2_keyboard_simple.py\n")
    
    try:
        while True:
            time.sleep(0.05)  # 20Hz控制频率
            
            # 检查是否按下移动键
            move_keys = keyboard.is_pressed('w') or keyboard.is_pressed('s') or \
                       keyboard.is_pressed('a') or keyboard.is_pressed('d') or \
                       keyboard.is_pressed('j') or keyboard.is_pressed('l')
            
            if move_keys:
                # 如果未站立，显示警告
                if not is_standing:
                    print("⚠ 机器人未站立，请先按Space站立", end='\r')
                else:
                    # 累加各方向的速度（支持组合按键）
                    vx = 0.0
                    vy = 0.0
                    vyaw = 0.0
                    direction_text = []
                    
                    # 前后方向
                    if keyboard.is_pressed('w'):
                        vx += speed
                        direction_text.append("↑前")
                    if keyboard.is_pressed('s'):
                        vx -= speed
                        direction_text.append("↓后")
                    
                    # 左右方向
                    if keyboard.is_pressed('a'):
                        vy += speed
                        direction_text.append("←左")
                    if keyboard.is_pressed('d'):
                        vy -= speed
                        direction_text.append("→右")
                    
                    # 旋转方向
                    if keyboard.is_pressed('j'):
                        vyaw += 0.5
                        direction_text.append("↶左转")
                    if keyboard.is_pressed('l'):
                        vyaw -= 0.5
                        direction_text.append("↷右转")
                    
                    # 限制速度范围
                    vx = max(-1.0, min(1.0, vx))
                    vy = max(-1.0, min(1.0, vy))
                    vyaw = max(-1.0, min(1.0, vyaw))
                    
                    # 发送移动命令
                    client.Move(vx, vy, vyaw)
                    
                    # 显示当前移动状态
                    direction_str = "+".join(direction_text)
                    print(f"{direction_str} | vx:{vx:>5.2f} vy:{vy:>5.2f} vyaw:{vyaw:>5.2f}    ", end='\r')
            
            # 状态控制（使用elif，不与移动组合）
            elif keyboard.is_pressed('space'):
                print("\n▲ 站立中...        ")
                client.StandUp()
                is_standing = True
                time.sleep(1.5)  # 等待站立完成
            
            elif keyboard.is_pressed('c'):
                print("\n▼ 趴下中...        ")
                client.StandDown()
                is_standing = False
                time.sleep(1)
            
            elif keyboard.is_pressed('x'):
                client.StopMove()
                print("⏹ 停止            ", end='\r')
            
            elif keyboard.is_pressed('r'):
                print("\n⟳ 恢复站立中...    ")
                client.RecoveryStand()
                is_standing = True
                time.sleep(2)
            
            elif keyboard.is_pressed('0'):
                print("\n◌ 阻尼模式        ")
                client.Damp()
                is_standing = False
                time.sleep(0.5)
            
            # 速度调节
            elif keyboard.is_pressed('+') or keyboard.is_pressed('='):
                speed = min(1.0, speed + 0.1)
                print(f"\n▲ 速度: {speed:.1f} m/s      ")
                time.sleep(0.2)
            
            elif keyboard.is_pressed('-'):
                speed = max(0.1, speed - 0.1)
                print(f"\n▼ 速度: {speed:.1f} m/s      ")
                time.sleep(0.2)
            
            # 退出
            elif keyboard.is_pressed('q'):
                print("\n\n退出程序...")
                break
    
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n清理中...")
        client.StopMove()
        time.sleep(0.5)
        client.Damp()
        print("✓ 程序结束")


if __name__ == '__main__':
    main()





