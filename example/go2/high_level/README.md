# Go2 高级控制示例

本目录包含 Unitree Go2 机器人的高级控制示例代码，使用 `SportClient` API。

## 📂 文件说明

### 🎯 示例程序

| 文件 | 说明 |
|-----|------|
| **go2_simple_demo.py** | ⭐ 基础控制演示 - 推荐新手从这里开始 |
| **go2_keyboard_simple.py** | ⭐ 键盘实时控制 - 手动测试机器人 |
| **go2_debug_window.py** | 🖥️ PyQt5 GUI调试工具 - 可视化测试 |
| **go2_sport_client.py** | 🏛️ 官方完整示例 - API参考 |
| go2_utlidar_switch.py | 激光雷达开关控制 |

### 📖 文档

| 文件 | 说明 |
|-----|------|
| **README.md** | 本文件 - 完整使用指南 |
| **QUICKSTART.md** | 5分钟快速上手 |

## 🚀 快速开始

### 1. 网络配置

#### 有线连接（推荐）

```bash
# 1. 用网线连接电脑和Go2机器人
# 2. 配置电脑IP
sudo ip addr add 192.168.123.100/24 dev enp5s0

# 3. 测试连接
ping 192.168.123.161
```

#### WiFi连接

```bash
# 1. 连接到Go2的WiFi热点：Unitree_Go2xxxxxx
# 2. 测试连接
ping 192.168.12.1
```

### 2. 运行基础演示

```bash
cd /home/ubuutu2004/桌面/unitree_sdk2_python-master/example/go2/high_level

# 运行演示程序
python3 go2_simple_demo.py enp5s0
```

**演示内容**：
- 站立
- 前进/后退
- 左移/右移
- 左转/右转
- 组合运动

### 3. 键盘控制

```bash
# 安装keyboard库
pip3 install keyboard

# 运行键盘控制（需要sudo权限）
sudo python3 go2_keyboard_simple.py enp5s0
```

**按键说明**：
- `w/s/a/d` - 前进/后退/左移/右移
- `j/l` - 左转/右转
- `Space` - 站立
- `c` - 趴下
- `x` - 停止
- `q` - 退出

### 4. GUI调试工具

```bash
# 安装PyQt5
pip3 install PyQt5

# 运行GUI工具
python3 go2_debug_window.py enp5s0
```

## 💻 代码示例

### 最简单的例子

```python
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
import time

# 1. 初始化通信
ChannelFactoryInitialize(0, "enp5s0")

# 2. 创建客户端
client = SportClient()
client.SetTimeout(10.0)
client.Init()

# 3. 站立
client.StandUp()
time.sleep(2)

# 4. 前进2秒
start = time.time()
while time.time() - start < 2:
    client.Move(0.3, 0, 0)  # vx=0.3 m/s
    time.sleep(0.1)

# 5. 停止
client.StopMove()
client.Damp()
```

### 各方向移动

```python
client.Move(0.3, 0, 0)      # 前进 0.3 m/s
client.Move(-0.3, 0, 0)     # 后退 0.3 m/s
client.Move(0, 0.3, 0)      # 左移 0.3 m/s
client.Move(0, -0.3, 0)     # 右移 0.3 m/s
client.Move(0, 0, 0.5)      # 左转 0.5 rad/s
client.Move(0, 0, -0.5)     # 右转 0.5 rad/s
client.Move(0.3, 0, 0.3)    # 前进+左转（组合）
```

### 基础控制命令

```python
client.StandUp()            # 站立
client.StandDown()          # 趴下
client.Damp()               # 阻尼模式（放松）
client.StopMove()           # 停止移动
client.RecoveryStand()      # 恢复站立（摔倒后）
client.BalanceStand()       # 平衡站立
```

### 高级技能

```python
# 倒立（4秒）
client.HandStand(True)
time.sleep(4)
client.HandStand(False)

# 后空翻
client.BackFlip()

# 左侧翻
client.LeftFlip()

# 自由行走
client.FreeWalk()

# 直立行走（4秒）
client.WalkUpright(True)
time.sleep(4)
client.WalkUpright(False)

# 交叉步（4秒）
client.CrossStep(True)
time.sleep(4)
client.CrossStep(False)
```

⚠️ **警告**：执行高级技能前确保周围有3米以上的安全空间！

## 📊 API 参考

### Move 方法参数

```python
client.Move(vx, vy, vyaw)
```

| 参数 | 范围 | 单位 | 说明 |
|-----|------|------|------|
| vx | -1.0 ~ 1.0 | m/s | 前后速度（正为前进） |
| vy | -1.0 ~ 1.0 | m/s | 左右速度（正为左移） |
| vyaw | -1.0 ~ 1.0 | rad/s | 旋转速度（正为左转） |

### 推荐参数

| 动作 | vx | vy | vyaw | 说明 |
|-----|----|----|------|------|
| 正常行走 | 0.3 | 0 | 0 | 安全速度 |
| 快速行走 | 0.5 | 0 | 0 | 较快速度 |
| 原地旋转 | 0 | 0 | 0.5 | 旋转速度 |
| 画圆 | 0.3 | 0 | 0.3 | 前进+转向 |

## 🔧 故障排除

### 错误码 3102：无法连接机器人

```bash
# 1. 检查网络连接
ping 192.168.123.161

# 2. 检查网络接口
ip addr show

# 3. 确认机器人已开机
# 4. 确认网络接口名称正确（enp5s0、eth0等）
```

### keyboard 模块需要 sudo

```bash
sudo pip3 install keyboard
sudo python3 go2_keyboard_simple.py enp5s0
```

### 找不到 unitree_sdk2py

```bash
cd /home/ubuutu2004/桌面/unitree_sdk2_python-master
pip3 install -e .
```

## 📚 学习路径

### 初学者

1. ✅ 阅读本 README
2. ✅ 运行 `go2_simple_demo.py`
3. ✅ 尝试修改速度参数
4. ✅ 使用 `go2_keyboard_simple.py` 手动控制

### 进阶

1. ✅ 查看 `go2_sport_client.py` 了解所有API
2. ✅ 使用 `go2_debug_window.py` 测试高级功能
3. ✅ 编写自己的控制程序
4. ✅ 集成传感器数据

## ⚠️ 安全提示

1. **测试前确认**：机器人周围2米内无障碍物
2. **从低速开始**：先用0.2-0.3 m/s测试
3. **保持监控**：始终有人监控机器人状态
4. **紧急停止**：按 Ctrl+C 或执行 `client.Damp()`
5. **高级技能**：空翻等动作需要3米以上空间

## 🔗 相关链接

- [Unitree Go2 官方文档](https://support.unitree.com/)
- [SDK2 Python GitHub](https://github.com/unitreerobotics/unitree_sdk2_python)
- [Unitree 开发者社区](https://www.unitree.com/)

## 💡 提示

- 控制频率建议10-20Hz（每0.05-0.1秒发送一次命令）
- Move命令需要持续发送才能保持运动
- 调用StopMove()可以立即停止运动
- 阻尼模式(Damp)可以让机器人放松，便于手动调整

## 📝 快速参考

```python
# 初始化模板
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
import time

ChannelFactoryInitialize(0, "enp5s0")
client = SportClient()
client.SetTimeout(10.0)
client.Init()

# 你的控制代码
client.StandUp()
# ...

# 清理
client.StopMove()
client.Damp()
```

---

**祝您使用愉快！** 🤖✨

如有问题，请查看 `QUICKSTART.md` 快速上手指南。

