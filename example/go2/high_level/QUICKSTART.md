# Go2 快速开始指南

## 🚀 5分钟上手

### 第1步：连接机器人（2分钟）

```bash
# 有线连接
sudo ip addr add 192.168.123.100/24 dev enp5s0
ping 192.168.123.161

# 或 WiFi连接（连接到 Unitree_Go2xxxxxx）
ping 192.168.12.1
```

### 第2步：运行第一个程序（3分钟）

```bash
cd /home/ubuutu2004/桌面/unitree_sdk2_python-master/example/go2/high_level
python3 go2_simple_demo.py enp5s0
```

**就这么简单！** 机器人会自动执行一系列动作。

## 📝 第一个自定义程序

创建文件 `my_first_go2.py`：

```python
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
import time

# 初始化
ChannelFactoryInitialize(0, "enp5s0")
client = SportClient()
client.SetTimeout(10.0)
client.Init()

print("让Go2站起来并走几步...")

# 站立
client.StandUp()
time.sleep(2)

# 前进3秒
print("前进中...")
start = time.time()
while time.time() - start < 3:
    client.Move(0.3, 0, 0)
    time.sleep(0.1)

# 停止
print("停止")
client.StopMove()
time.sleep(1)

# 放松
client.Damp()
print("完成！")
```

运行：
```bash
python3 my_first_go2.py
```

## 🎮 常用命令速查

### 初始化（每个程序开始都要）

```python
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

ChannelFactoryInitialize(0, "enp5s0")
client = SportClient()
client.SetTimeout(10.0)
client.Init()
```

### 基础动作

```python
client.StandUp()        # 站立
client.StandDown()      # 趴下
client.Damp()           # 放松（阻尼模式）
client.StopMove()       # 停止
```

### 移动

```python
# Move(前后, 左右, 旋转)
client.Move(0.3, 0, 0)      # 前进
client.Move(-0.3, 0, 0)     # 后退
client.Move(0, 0.3, 0)      # 左移
client.Move(0, -0.3, 0)     # 右移
client.Move(0, 0, 0.5)      # 左转
client.Move(0, 0, -0.5)     # 右转
```

**注意**：Move命令需要持续发送（循环中调用）

### 定时移动模板

```python
# 移动N秒
duration = 3  # 秒
start = time.time()
while time.time() - start < duration:
    client.Move(0.3, 0, 0)
    time.sleep(0.1)
client.StopMove()
```

## 🎪 高级技能

```python
# 后空翻（需要大空间！）
client.BackFlip()
time.sleep(3)

# 倒立4秒
client.HandStand(True)
time.sleep(4)
client.HandStand(False)

# 直立行走
client.WalkUpright(True)
time.sleep(5)
client.WalkUpright(False)
```

## 📊 参数说明

### Move(vx, vy, vyaw)

| 参数 | 范围 | 推荐值 | 说明 |
|-----|------|--------|------|
| vx | -1.0~1.0 | 0.3 | 前后速度 (m/s) |
| vy | -1.0~1.0 | 0.3 | 左右速度 (m/s) |
| vyaw | -1.0~1.0 | 0.5 | 旋转速度 (rad/s) |

## 🔧 常见问题

### Q: 错误码3102
**A**: 网络连接问题
```bash
ping 192.168.123.161  # 检查连接
ip addr show          # 检查网络接口
```

### Q: Move后机器人不动
**A**: Move命令需要持续发送（在循环中）

### Q: 如何紧急停止
**A**: 
```python
client.StopMove()  # 停止移动
client.Damp()      # 进入阻尼模式
```

或按 `Ctrl + C`

## 📂 示例文件

| 文件 | 说明 | 运行命令 |
|-----|------|----------|
| go2_simple_demo.py | 基础演示 | `python3 go2_simple_demo.py enp5s0` |
| go2_keyboard_simple.py | 键盘控制 | `sudo python3 go2_keyboard_simple.py enp5s0` |
| go2_debug_window.py | GUI工具 | `python3 go2_debug_window.py enp5s0` |

## 🎓 学习路线

**第1天**：基础
1. 运行 `go2_simple_demo.py`
2. 修改速度参数试试
3. 写一个简单的前进后退程序

**第2天**：控制
1. 使用 `go2_keyboard_simple.py` 手动控制
2. 尝试让机器人画圆（前进+转向）
3. 写一个定时巡逻程序

**第3天**：进阶
1. 测试高级技能（空翻等）
2. 使用GUI调试工具
3. 开始开发自己的应用

## 💡 实用代码片段

### 画正方形

```python
for i in range(4):
    # 前进2秒
    start = time.time()
    while time.time() - start < 2:
        client.Move(0.3, 0, 0)
        time.sleep(0.1)
    
    # 左转90度（约1.5秒）
    start = time.time()
    while time.time() - start < 1.5:
        client.Move(0, 0, 0.5)
        time.sleep(0.1)
    
    time.sleep(0.5)
```

### 来回巡逻

```python
while True:
    # 前进5秒
    start = time.time()
    while time.time() - start < 5:
        client.Move(0.3, 0, 0)
        time.sleep(0.1)
    
    # 转180度
    start = time.time()
    while time.time() - start < 3:
        client.Move(0, 0, 0.5)
        time.sleep(0.1)
    
    time.sleep(1)
```

### 安全包装

```python
try:
    client.StandUp()
    time.sleep(2)
    
    # 你的控制代码
    # ...
    
except KeyboardInterrupt:
    print("\n用户中断")
finally:
    print("清理...")
    client.StopMove()
    client.Damp()
```

## 🎯 下一步

1. ✅ 完成第一个程序
2. ✅ 阅读 `README.md` 了解所有API
3. ✅ 查看 `go2_sport_client.py` 官方示例
4. ✅ 开始你的项目！

---

**开始你的Go2之旅吧！** 🤖✨





