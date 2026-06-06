#!/usr/bin/python
"""
Go2 Debug Window with GUI
Migrated from Go1 SDK to Go2 SDK2
PySide2-based control interface for Go2 robot (免费的Qt官方Python绑定)
"""
import sys
import os
import datetime
import time
import socket
import netifaces

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide2 import QtCore
from PySide2.QtCore import Qt, QTimer, QThread, Signal
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QTabWidget, QListWidget, 
    QListWidgetItem, QGroupBox, QGridLayout, QMessageBox, QMenuBar, QMenu, QAction,
    QCheckBox, QSlider, QRadioButton, QButtonGroup
)

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

# 显示PySide2版本
print(f"✅ PySide2 版本: {QtCore.__version__}")

# 语言文本字典
TEXTS = {
    'zh': {
        'window_title': 'Go2 机器人调试窗口',
        'tab_basic': '基础控制',
        'tab_movement': '运动控制',
        'tab_advanced': '高级技能',
        'tab_state': '机器人状态',
        'tab_logs': '命令日志',
        
        # 基础控制
        'group_basic': '基础命令',
        'btn_stand_up': '站立',
        'btn_stand_down': '趴下',
        'btn_sit': '坐下',
        'btn_damp': '阻尼模式',
        'btn_stop': '停止移动',
        'btn_risesit': '起坐',
        'btn_balance': '平衡站立',
        'btn_recovery': '恢复站立',
        'btn_prepare_motion': '⚡ 准备运动',
        
        # 姿态控制
        'group_euler': '姿态控制 (Euler)',
        'label_roll': 'Roll (横滚):',
        'label_pitch': 'Pitch (俯仰):',
        'label_yaw_euler': 'Yaw (偏航):',
        'unit_euler': 'rad (-0.5 到 0.5)',
        'btn_set_euler': '设置姿态',
        'btn_reset_euler': '重置姿态',
        
        # 速度等级
        'group_speed_level': '速度等级',
        'speed_low': '慢速 (安全)',
        'speed_medium': '中速 (标准)',
        'speed_high': '快速 (运动)',
        
        'group_status': '状态',
        'status_ready': 'Go2 机器人控制界面已就绪',
        'status_robot_ready': '✅ 机器人已准备好运动',
        'status_robot_not_ready': '⚠️  机器人未准备好，请点击"准备运动"',
        'preparing_motion': '正在准备运动：解除阻尼 → 站立',
        'motion_ready': '✅ 机器人已准备好运动！',
        'warn_not_ready': '警告：运动前准备',
        'warn_not_ready_msg': '机器人尚未准备好运动。\n\n根据Unitree官方文档，运动控制前需要：\n1. 解除关节锁定（阻尼模式）\n2. 确保机器人站立\n\n是否自动准备？',
        
        # 运动控制
        'group_movement_params': '运动参数',
        'label_vx': 'VX (前进/后退):',
        'label_vy': 'VY (左移/右移):',
        'label_vyaw': 'VYAW (旋转):',
        'unit_ms': 'm/s (-1.0 到 1.0)',
        'unit_rads': 'rad/s (-1.0 到 1.0)',
        'btn_send_move': '发送移动命令',
        'group_quick_move': '快速移动（长按按钮持续移动）',
        'btn_forward': '↑ 前进 (0.3 m/s)',
        'btn_backward': '↓ 后退 (0.3 m/s)',
        'btn_left': '← 左移 (0.3 m/s)',
        'btn_right': '→ 右移 (0.3 m/s)',
        'btn_turn_left': '↶ 左转 (0.5 rad/s)',
        'btn_turn_right': '↷ 右转 (0.5 rad/s)',
        
        # 高级技能
        'group_skills': '高级技能',
        'group_flips': '空翻技巧',
        'group_actions': '互动动作',
        'group_dance': '舞蹈表演',
        'group_gaits': '步态模式',
        
        # 空翻技巧
        'btn_handstand': '倒立 (4秒)',
        'btn_backflip': '后空翻',
        'btn_leftflip': '左侧翻',
        'btn_frontflip': '前空翻',
        
        # 跳跃动作
        'btn_freejump': '自由跳',
        'btn_frontjump': '前跳',
        'btn_freebound': '自由跳跃',
        'btn_frontpounce': '前扑',
        
        # 互动动作
        'btn_hello': '招手',
        'btn_stretch': '伸展',
        'btn_heart': '比心',
        'btn_pose': '摆姿势',
        'btn_scrape': '刮擦',
        
        # 舞蹈表演
        'btn_dance1': '舞蹈1',
        'btn_dance2': '舞蹈2',
        
        # 步态模式
        'btn_freewalk': '自由行走',
        'btn_upright': '直立行走 (4秒)',
        'btn_crossstep': '交叉步 (4秒)',
        'btn_classicwalk': '经典步态',
        'btn_staticwalk': '静态步态',
        'btn_trotrun': '小跑',
        
        # 其他
        'btn_freeavoid': '自由避障',
        'btn_sit': '坐下',
        
        'warning_skills': '⚠️ 警告: 执行高级技能前请确保机器人周围有足够空间！',
        
        # 日志
        'btn_refresh': '刷新日志',
        'btn_clear': '清空日志',
        
        # 消息框
        'invalid_input': '输入无效',
        'value_range_error': '数值必须在 -1.0 到 1.0 之间',
        'number_error': '请输入有效的数字',
        'confirm': '确认',
        'confirm_handstand': '执行倒立动作 4 秒？',
        'confirm_backflip': '执行后空翻？请确保空间充足！',
        'confirm_leftflip': '执行左侧翻？请确保空间充足！',
        'confirm_clear_log': '清空所有日志？',
        'yes': '是',
        'no': '否',
        
        # 命令日志
        'cmd_stand_up': '站立',
        'cmd_stand_down': '趴下',
        'cmd_damp': '阻尼模式',
        'cmd_stop': '停止移动',
        'cmd_balance': '平衡站立',
        'cmd_recovery': '恢复站立',
        'cmd_handstand_start': '倒立 - 开始',
        'cmd_handstand_end': '倒立 - 结束',
        'cmd_upright_start': '直立行走 - 开始',
        'cmd_upright_end': '直立行走 - 结束',
        'cmd_crossstep_start': '交叉步 - 开始',
        'cmd_crossstep_end': '交叉步 - 结束',
        
        # 菜单
        'menu_language': '语言',
        'menu_chinese': '中文',
        'menu_english': 'English',
    },
    'en': {
        'window_title': 'Go2 Robot Debug Window',
        'tab_basic': 'Basic Control',
        'tab_movement': 'Movement Control',
        'tab_advanced': 'Advanced Skills',
        'tab_state': 'Robot State',
        'tab_logs': 'Command Logs',
        
        # Basic control
        'group_basic': 'Basic Commands',
        'btn_stand_up': 'Stand Up',
        'btn_stand_down': 'Stand Down',
        'btn_sit': 'Sit',
        'btn_damp': 'Damp Mode',
        'btn_stop': 'Stop Move',
        'btn_risesit': 'Rise from Sit',
        'btn_balance': 'Balance Stand',
        'btn_recovery': 'Recovery Stand',
        'btn_prepare_motion': '⚡ Prepare Motion',
        
        # Euler control
        'group_euler': 'Attitude Control (Euler)',
        'label_roll': 'Roll:',
        'label_pitch': 'Pitch:',
        'label_yaw_euler': 'Yaw:',
        'unit_euler': 'rad (-0.5 to 0.5)',
        'btn_set_euler': 'Set Attitude',
        'btn_reset_euler': 'Reset Attitude',
        
        # Speed level
        'group_speed_level': 'Speed Level',
        'speed_low': 'Low (Safe)',
        'speed_medium': 'Medium (Standard)',
        'speed_high': 'High (Sport)',
        
        'group_status': 'Status',
        'status_ready': 'Go2 Robot Control Interface Ready',
        'status_robot_ready': '✅ Robot Ready for Motion',
        'status_robot_not_ready': '⚠️  Robot Not Ready, Click "Prepare Motion"',
        'preparing_motion': 'Preparing Motion: Release Damp → Stand Up',
        'motion_ready': '✅ Robot is Ready for Motion!',
        'warn_not_ready': 'Warning: Motion Preparation',
        'warn_not_ready_msg': 'Robot is not ready for motion.\n\nAccording to Unitree official documentation:\n1. Release joint lock (Damp mode)\n2. Ensure robot is standing\n\nAuto-prepare now?',
        
        # Movement control
        'group_movement_params': 'Movement Parameters',
        'label_vx': 'VX (Forward/Backward):',
        'label_vy': 'VY (Left/Right):',
        'label_vyaw': 'VYAW (Rotation):',
        'unit_ms': 'm/s (-1.0 to 1.0)',
        'unit_rads': 'rad/s (-1.0 to 1.0)',
        'btn_send_move': 'Send Move Command',
        'group_quick_move': 'Quick Movement (Press & Hold)',
        'btn_forward': '↑ Forward (0.3 m/s)',
        'btn_backward': '↓ Backward (0.3 m/s)',
        'btn_left': '← Left (0.3 m/s)',
        'btn_right': '→ Right (0.3 m/s)',
        'btn_turn_left': '↶ Turn Left (0.5 rad/s)',
        'btn_turn_right': '↷ Turn Right (0.5 rad/s)',
        
        # Advanced skills
        'group_skills': 'Advanced Skills',
        'group_flips': 'Flip Skills',
        'group_actions': 'Interactive Actions',
        'group_dance': 'Dance Performance',
        'group_gaits': 'Gait Modes',
        
        # Flip skills
        'btn_handstand': 'Hand Stand (4s)',
        'btn_backflip': 'Back Flip',
        'btn_leftflip': 'Left Flip',
        'btn_frontflip': 'Front Flip',
        
        # Jump actions
        'btn_freejump': 'Free Jump',
        'btn_frontjump': 'Front Jump',
        'btn_freebound': 'Free Bound',
        'btn_frontpounce': 'Front Pounce',
        
        # Interactive actions
        'btn_hello': 'Hello',
        'btn_stretch': 'Stretch',
        'btn_heart': 'Heart',
        'btn_pose': 'Pose',
        'btn_scrape': 'Scrape',
        
        # Dance performance
        'btn_dance1': 'Dance 1',
        'btn_dance2': 'Dance 2',
        
        # Gait modes
        'btn_freewalk': 'Free Walk',
        'btn_upright': 'Walk Upright (4s)',
        'btn_crossstep': 'Cross Step (4s)',
        'btn_classicwalk': 'Classic Walk',
        'btn_staticwalk': 'Static Walk',
        'btn_trotrun': 'Trot Run',
        
        # Others
        'btn_freeavoid': 'Free Avoid',
        'btn_sit': 'Sit',
        
        'warning_skills': '⚠️ WARNING: Ensure sufficient space around robot before executing advanced skills!',
        
        # Logs
        'btn_refresh': 'Refresh Log',
        'btn_clear': 'Clear Log',
        
        # Message boxes
        'invalid_input': 'Invalid Input',
        'value_range_error': 'Values must be between -1.0 and 1.0',
        'number_error': 'Please enter valid numbers',
        'confirm': 'Confirm',
        'confirm_handstand': 'Execute Hand Stand for 4 seconds?',
        'confirm_backflip': 'Execute Back Flip? Ensure space is clear!',
        'confirm_leftflip': 'Execute Left Flip? Ensure space is clear!',
        'confirm_clear_log': 'Clear all logs?',
        'yes': 'Yes',
        'no': 'No',
        
        # Command logs
        'cmd_stand_up': 'Stand Up',
        'cmd_stand_down': 'Stand Down',
        'cmd_damp': 'Damp Mode',
        'cmd_stop': 'Stop Move',
        'cmd_balance': 'Balance Stand',
        'cmd_recovery': 'Recovery Stand',
        'cmd_handstand_start': 'Hand Stand - Start',
        'cmd_handstand_end': 'Hand Stand - End',
        'cmd_upright_start': 'Walk Upright - Start',
        'cmd_upright_end': 'Walk Upright - End',
        'cmd_crossstep_start': 'Cross Step - Start',
        'cmd_crossstep_end': 'Cross Step - End',
        
        # Menu
        'menu_language': 'Language',
        'menu_chinese': '中文',
        'menu_english': 'English',
    }
}


def check_go2_network():
    """检查是否在Go2的网段（192.168.123.*）"""
    try:
        # 获取所有网络接口
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr.get('addr', '')
                    if ip.startswith('192.168.123.'):
                        print(f"✅ 检测到Go2网段IP: {ip} ({interface})")
                        return True
        print("⚠️  未检测到Go2网段 (192.168.123.*)")
        return False
    except Exception as e:
        print(f"⚠️  网络检测失败: {e}")
        return False


class MockSportClient:
    """模拟的SportClient，用于无机器人调试"""
    
    def __init__(self):
        print("🔧 启动模拟模式 (Mock Mode) - 无需真实机器人连接")
    
    def SetTimeout(self, timeout):
        pass
    
    def Init(self):
        pass
    
    def StandUp(self):
        print("  [模拟] StandUp() - 站立")
        return 0
    
    def StandDown(self):
        print("  [模拟] StandDown() - 趴下")
        return 0
    
    def Damp(self):
        print("  [模拟] Damp() - 阻尼模式")
        return 0
    
    def StopMove(self):
        print("  [模拟] StopMove() - 停止移动")
        return 0
    
    def BalanceStand(self):
        print("  [模拟] BalanceStand() - 平衡站立")
        return 0
    
    def RecoveryStand(self):
        print("  [模拟] RecoveryStand() - 恢复站立")
        return 0
    
    def Move(self, vx, vy, vyaw):
        print(f"  [模拟] Move(vx={vx:.2f}, vy={vy:.2f}, vyaw={vyaw:.2f})")
        return 0
    
    def HandStand(self, enable):
        print(f"  [模拟] HandStand({enable}) - 倒立")
        return 0
    
    def BackFlip(self):
        print("  [模拟] BackFlip() - 后空翻")
        return 0
    
    def LeftFlip(self):
        print("  [模拟] LeftFlip() - 左侧翻")
        return 0
    
    def FreeWalk(self):
        print("  [模拟] FreeWalk() - 自由行走")
        return 0
    
    def WalkUpright(self, enable):
        print(f"  [模拟] WalkUpright({enable}) - 直立行走")
        return 0
    
    def CrossStep(self, enable):
        print(f"  [模拟] CrossStep({enable}) - 交叉步")
        return 0
    
    # 新增高级技能
    def FrontFlip(self):
        print("  [模拟] FrontFlip() - 前空翻")
        return 0
    
    def FrontJump(self):
        print("  [模拟] FrontJump() - 前跳")
        return 0
    
    def FrontPounce(self):
        print("  [模拟] FrontPounce() - 前扑")
        return 0
    
    def Hello(self):
        print("  [模拟] Hello() - 招手")
        return 0
    
    def Stretch(self):
        print("  [模拟] Stretch() - 伸展")
        return 0
    
    def Heart(self):
        print("  [模拟] Heart() - 比心")
        return 0
    
    def Pose(self, enable):
        print(f"  [模拟] Pose({enable}) - 摆姿势")
        return 0
    
    def Scrape(self):
        print("  [模拟] Scrape() - 刮擦")
        return 0
    
    def Sit(self):
        print("  [模拟] Sit() - 坐下")
        return 0
    
    def RiseSit(self):
        print("  [模拟] RiseSit() - 起坐")
        return 0
    
    def Euler(self, roll, pitch, yaw):
        print(f"  [模拟] Euler(roll={roll:.3f}, pitch={pitch:.3f}, yaw={yaw:.3f}) - 设置姿态")
        return 0
    
    def SpeedLevel(self, level):
        print(f"  [模拟] SpeedLevel({level}) - 速度等级")
        return 0
    
    def Dance1(self):
        print("  [模拟] Dance1() - 舞蹈1")
        return 0
    
    def Dance2(self):
        print("  [模拟] Dance2() - 舞蹈2")
        return 0
    
    def ClassicWalk(self, enable):
        print(f"  [模拟] ClassicWalk({enable}) - 经典步态")
        return 0
    
    def StaticWalk(self):
        print("  [模拟] StaticWalk() - 静态步态")
        return 0
    
    def TrotRun(self):
        print("  [模拟] TrotRun() - 小跑")
        return 0
    
    def FreeBound(self, enable):
        print(f"  [模拟] FreeBound({enable}) - 自由跳跃")
        return 0
    
    def FreeJump(self, enable):
        print(f"  [模拟] FreeJump({enable}) - 自由跳")
        return 0
    
    def FreeAvoid(self, enable):
        print(f"  [模拟] FreeAvoid({enable}) - 自由避障")
        return 0


class CommandWorker(QThread):
    """后台线程执行机器人命令，避免阻塞GUI"""
    command_finished = Signal(str, object)  # 信号：命令名称，返回值
    
    def __init__(self, sport_client, command_name, command_func, *args, **kwargs):
        super().__init__()
        self.sport_client = sport_client
        self.command_name = command_name
        self.command_func = command_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """在后台线程中执行命令"""
        try:
            result = self.command_func(*self.args, **self.kwargs)
            self.command_finished.emit(self.command_name, result)
        except Exception as e:
            self.command_finished.emit(self.command_name, f"Error: {str(e)}")


class Go2Control:
    """Go2 Robot Control using SDK2"""
    
    def __init__(self, network_interface=None, force_mock=False):
        """Initialize Go2 control
        
        Args:
            network_interface: 网络接口名称
            force_mock: 强制使用模拟模式
        """
        # 检查是否应该使用模拟模式
        self.is_mock_mode = force_mock or not check_go2_network()
        
        # 机器人状态
        self.latest_state = None
        self.state_subscriber = None
        
        if self.is_mock_mode:
            # 使用模拟的SportClient
            self.sport_client = MockSportClient()
            self.sport_client.SetTimeout(10.0)
            self.sport_client.Init()
            print("🔧 调试模式已启动 - 所有命令将被模拟执行")
        else:
            # Initialize DDS communication
            if network_interface:
                ChannelFactoryInitialize(0, network_interface)
            else:
                ChannelFactoryInitialize(0)
            
            # Create real sport client
            self.sport_client = SportClient()
            self.sport_client.SetTimeout(10.0)
            self.sport_client.Init()
            print("✅ Go2 Sport Client initialized!")
            
            # Subscribe to robot state
            try:
                self.state_subscriber = ChannelSubscriber("rt/sportmodestate", SportModeState_)
                self.state_subscriber.Init(self._state_handler, 1)
                print("✅ 已订阅机器人状态 / Robot state subscribed")
            except Exception as e:
                print(f"⚠️  状态订阅失败 / State subscription failed: {e}")
        
        # Current movement parameters
        self.vx = 0.0
        self.vy = 0.0
        self.vyaw = 0.0
    
    def _state_handler(self, msg: SportModeState_):
        """处理机器人状态回调"""
        self.latest_state = msg
    
    def is_robot_standing(self):
        """检查机器人是否站立（通过足端力判断）"""
        if self.is_mock_mode:
            return True  # 调试模式总是返回True
        
        if self.latest_state is None:
            return False  # 没有收到状态数据
        
        # 计算总足端力
        total_force = sum(self.latest_state.foot_force)
        
        # 如果足端力大于150N，认为机器人已站立
        # 参考 check_robot_state.py 的判断逻辑
        return total_force > 150


class DebugWindow(QWidget):
    """Main debug window for Go2 robot"""
    
    def __init__(self, go2_control: Go2Control):
        super().__init__()
        self.go2_control = go2_control
        self.current_lang = 'zh'  # 默认中文
        self.current_worker = None  # 当前执行的worker线程
        self.worker_list = []  # 保存所有worker线程的引用，防止过早销毁
        
        # 持续移动相关
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.send_continuous_move)
        self.current_vx = 0.0
        self.current_vy = 0.0
        self.current_vyaw = 0.0
        
        self.setGeometry(200, 200, 900, 700)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create menu bar
        self.create_menu_bar()
        main_layout.setMenuBar(self.menu_bar)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        self.create_all_tabs()
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        
        # 设置初始语言
        self.update_language()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        self.menu_bar = QMenuBar(self)
        self.language_menu = self.menu_bar.addMenu(TEXTS[self.current_lang]['menu_language'])
        
        # 中文选项
        self.action_chinese = QAction(TEXTS[self.current_lang]['menu_chinese'], self)
        self.action_chinese.triggered.connect(lambda: self.switch_language('zh'))
        self.language_menu.addAction(self.action_chinese)
        
        # 英文选项
        self.action_english = QAction(TEXTS[self.current_lang]['menu_english'], self)
        self.action_english.triggered.connect(lambda: self.switch_language('en'))
        self.language_menu.addAction(self.action_english)
    
    def switch_language(self, lang):
        """切换语言"""
        if lang != self.current_lang:
            self.current_lang = lang
            self.update_language()
    
    def update_language(self):
        """更新所有界面文本"""
        t = TEXTS[self.current_lang]
        
        # 更新窗口标题
        self.setWindowTitle(t['window_title'])
        
        # 更新菜单
        self.language_menu.setTitle(t['menu_language'])
        self.action_chinese.setText(t['menu_chinese'])
        self.action_english.setText(t['menu_english'])
        
        # 重新创建所有标签页
        self.tab_widget.clear()
        self.create_all_tabs()
    
    def create_all_tabs(self):
        """创建所有标签页"""
        t = TEXTS[self.current_lang]
        
        self.basic_control_tab = self.create_basic_control_tab()
        self.movement_tab = self.create_movement_tab()
        self.advanced_tab = self.create_advanced_tab()
        self.state_tab = self.create_state_tab()
        self.log_tab = LogTab(self)
        
        self.tab_widget.addTab(self.basic_control_tab, t['tab_basic'])
        self.tab_widget.addTab(self.movement_tab, t['tab_movement'])
        self.tab_widget.addTab(self.advanced_tab, t['tab_advanced'])
        self.tab_widget.addTab(self.state_tab, t['tab_state'])
        self.tab_widget.addTab(self.log_tab, t['tab_logs'])
    
    def create_basic_control_tab(self):
        """Create basic control tab"""
        t = TEXTS[self.current_lang]
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Basic commands group
        basic_group = QGroupBox(t['group_basic'])
        basic_layout = QGridLayout()
        
        # Create buttons
        btn_stand_up = QPushButton(t['btn_stand_up'])
        btn_stand_up.clicked.connect(self.cmd_stand_up)
        btn_stand_down = QPushButton(t['btn_stand_down'])
        btn_stand_down.clicked.connect(self.cmd_stand_down)
        btn_sit = QPushButton(t['btn_sit'])
        btn_sit.clicked.connect(self.cmd_sit)
        btn_damp = QPushButton(t['btn_damp'])
        btn_damp.clicked.connect(self.cmd_damp)
        btn_stop = QPushButton(t['btn_stop'])
        btn_stop.clicked.connect(self.cmd_stop_move)
        btn_risesit = QPushButton(t['btn_risesit'])
        btn_risesit.clicked.connect(self.cmd_rise_sit)
        btn_balance = QPushButton(t['btn_balance'])
        btn_balance.clicked.connect(self.cmd_balance_stand)
        btn_recovery = QPushButton(t['btn_recovery'])
        btn_recovery.clicked.connect(self.cmd_recovery_stand)
        
        # Add buttons to grid (3列布局)
        basic_layout.addWidget(btn_stand_up, 0, 0)
        basic_layout.addWidget(btn_stand_down, 0, 1)
        basic_layout.addWidget(btn_sit, 0, 2)
        basic_layout.addWidget(btn_damp, 1, 0)
        basic_layout.addWidget(btn_stop, 1, 1)
        basic_layout.addWidget(btn_risesit, 1, 2)
        basic_layout.addWidget(btn_balance, 2, 0)
        basic_layout.addWidget(btn_recovery, 2, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Status display
        status_group = QGroupBox(t['group_status'])
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        
        # 显示当前模式
        if self.go2_control.is_mock_mode:
            mode_text = "🔧 调试模式 (Mock Mode) - 无需真实机器人连接"
            self.status_text.append(mode_text)
            self.status_text.append("所有命令将在终端显示，不会发送到机器人")
        else:
            mode_text = "✅ 真实模式 (Real Mode) - 已连接到Go2机器人"
            self.status_text.append(mode_text)
        
        self.status_text.append(t['status_ready'])
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Euler姿态控制组
        euler_group = QGroupBox(t['group_euler'])
        euler_layout = QVBoxLayout()
        
        # Roll滑块
        roll_layout = QHBoxLayout()
        roll_layout.addWidget(QLabel(t['label_roll']))
        self.roll_input = QLineEdit("0.0")
        self.roll_input.setAlignment(Qt.AlignRight)
        self.roll_input.setMaximumWidth(80)
        roll_layout.addWidget(self.roll_input)
        roll_layout.addWidget(QLabel(t['unit_euler']))
        euler_layout.addLayout(roll_layout)
        
        # Pitch滑块
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel(t['label_pitch']))
        self.pitch_input = QLineEdit("0.0")
        self.pitch_input.setAlignment(Qt.AlignRight)
        self.pitch_input.setMaximumWidth(80)
        pitch_layout.addWidget(self.pitch_input)
        pitch_layout.addWidget(QLabel(t['unit_euler']))
        euler_layout.addLayout(pitch_layout)
        
        # Yaw滑块
        yaw_euler_layout = QHBoxLayout()
        yaw_euler_layout.addWidget(QLabel(t['label_yaw_euler']))
        self.yaw_euler_input = QLineEdit("0.0")
        self.yaw_euler_input.setAlignment(Qt.AlignRight)
        self.yaw_euler_input.setMaximumWidth(80)
        yaw_euler_layout.addWidget(self.yaw_euler_input)
        yaw_euler_layout.addWidget(QLabel(t['unit_euler']))
        euler_layout.addLayout(yaw_euler_layout)
        
        # 按钮
        euler_btn_layout = QHBoxLayout()
        btn_set_euler = QPushButton(t['btn_set_euler'])
        btn_set_euler.clicked.connect(self.cmd_set_euler)
        btn_reset_euler = QPushButton(t['btn_reset_euler'])
        btn_reset_euler.clicked.connect(self.cmd_reset_euler)
        euler_btn_layout.addWidget(btn_set_euler)
        euler_btn_layout.addWidget(btn_reset_euler)
        euler_layout.addLayout(euler_btn_layout)
        
        euler_group.setLayout(euler_layout)
        layout.addWidget(euler_group)
        
        # 速度等级控制组
        speed_group = QGroupBox(t['group_speed_level'])
        speed_layout = QHBoxLayout()
        
        self.speed_level_group = QButtonGroup(self)
        
        self.radio_speed_low = QRadioButton(t['speed_low'])
        self.radio_speed_medium = QRadioButton(t['speed_medium'])
        self.radio_speed_high = QRadioButton(t['speed_high'])
        
        self.radio_speed_medium.setChecked(True)  # 默认中速
        
        self.speed_level_group.addButton(self.radio_speed_low, 0)
        self.speed_level_group.addButton(self.radio_speed_medium, 1)
        self.speed_level_group.addButton(self.radio_speed_high, 2)
        
        self.speed_level_group.buttonClicked.connect(self.cmd_set_speed_level)
        
        speed_layout.addWidget(self.radio_speed_low)
        speed_layout.addWidget(self.radio_speed_medium)
        speed_layout.addWidget(self.radio_speed_high)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_movement_tab(self):
        """Create movement control tab"""
        t = TEXTS[self.current_lang]
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 准备运动按钮和状态显示
        prepare_group = QGroupBox("运动准备 / Motion Preparation")
        prepare_layout = QVBoxLayout()
        
        # 准备运动按钮
        btn_prepare = QPushButton(t['btn_prepare_motion'])
        btn_prepare.clicked.connect(self.cmd_prepare_motion)
        btn_prepare.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; font-size: 14px; }")
        prepare_layout.addWidget(btn_prepare)
        
        # 状态显示标签
        self.robot_status_label = QLabel()
        self.robot_status_label.setWordWrap(True)
        self.robot_status_label.setStyleSheet("QLabel { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }")
        prepare_layout.addWidget(self.robot_status_label)
        
        # 启动状态更新定时器
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_robot_status_display)
        self.status_update_timer.start(500)  # 每500ms更新一次状态
        
        prepare_group.setLayout(prepare_layout)
        layout.addWidget(prepare_group)
        
        # Movement parameters group
        param_group = QGroupBox(t['group_movement_params'])
        param_layout = QVBoxLayout()
        
        # VX (forward/backward)
        vx_layout = QHBoxLayout()
        vx_layout.addWidget(QLabel(t['label_vx']))
        self.vx_input = QLineEdit("0.0")
        self.vx_input.setAlignment(Qt.AlignRight)
        vx_layout.addWidget(self.vx_input)
        vx_layout.addWidget(QLabel(t['unit_ms']))
        param_layout.addLayout(vx_layout)
        
        # VY (left/right)
        vy_layout = QHBoxLayout()
        vy_layout.addWidget(QLabel(t['label_vy']))
        self.vy_input = QLineEdit("0.0")
        self.vy_input.setAlignment(Qt.AlignRight)
        vy_layout.addWidget(self.vy_input)
        vy_layout.addWidget(QLabel(t['unit_ms']))
        param_layout.addLayout(vy_layout)
        
        # VYAW (rotation)
        vyaw_layout = QHBoxLayout()
        vyaw_layout.addWidget(QLabel(t['label_vyaw']))
        self.vyaw_input = QLineEdit("0.0")
        self.vyaw_input.setAlignment(Qt.AlignRight)
        vyaw_layout.addWidget(self.vyaw_input)
        vyaw_layout.addWidget(QLabel(t['unit_rads']))
        param_layout.addLayout(vyaw_layout)
        
        # Send move button
        btn_send_move = QPushButton(t['btn_send_move'])
        btn_send_move.clicked.connect(self.cmd_move)
        param_layout.addWidget(btn_send_move)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Quick movement buttons (长按持续移动)
        quick_group = QGroupBox(t['group_quick_move'])
        quick_layout = QGridLayout()
        
        btn_forward = QPushButton(t['btn_forward'])
        btn_forward.pressed.connect(lambda: self.start_continuous_move(0.3, 0, 0))
        btn_forward.released.connect(self.stop_continuous_move)
        
        btn_backward = QPushButton(t['btn_backward'])
        btn_backward.pressed.connect(lambda: self.start_continuous_move(-0.3, 0, 0))
        btn_backward.released.connect(self.stop_continuous_move)
        
        btn_left = QPushButton(t['btn_left'])
        btn_left.pressed.connect(lambda: self.start_continuous_move(0, 0.3, 0))
        btn_left.released.connect(self.stop_continuous_move)
        
        btn_right = QPushButton(t['btn_right'])
        btn_right.pressed.connect(lambda: self.start_continuous_move(0, -0.3, 0))
        btn_right.released.connect(self.stop_continuous_move)
        
        btn_turn_left = QPushButton(t['btn_turn_left'])
        btn_turn_left.pressed.connect(lambda: self.start_continuous_move(0, 0, 0.5))
        btn_turn_left.released.connect(self.stop_continuous_move)
        
        btn_turn_right = QPushButton(t['btn_turn_right'])
        btn_turn_right.pressed.connect(lambda: self.start_continuous_move(0, 0, -0.5))
        btn_turn_right.released.connect(self.stop_continuous_move)
        
        quick_layout.addWidget(btn_forward, 0, 1)
        quick_layout.addWidget(btn_backward, 2, 1)
        quick_layout.addWidget(btn_left, 1, 0)
        quick_layout.addWidget(btn_right, 1, 2)
        quick_layout.addWidget(btn_turn_left, 3, 0)
        quick_layout.addWidget(btn_turn_right, 3, 2)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_advanced_tab(self):
        """Create advanced skills tab"""
        t = TEXTS[self.current_lang]
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Warning label at top
        warning_label = QLabel(t['warning_skills'])
        warning_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")
        layout.addWidget(warning_label)
        
        # 空翻技巧组
        flips_group = QGroupBox(t['group_flips'])
        flips_layout = QGridLayout()
        
        btn_handstand = QPushButton(t['btn_handstand'])
        btn_handstand.clicked.connect(self.cmd_hand_stand)
        btn_backflip = QPushButton(t['btn_backflip'])
        btn_backflip.clicked.connect(self.cmd_back_flip)
        btn_leftflip = QPushButton(t['btn_leftflip'])
        btn_leftflip.clicked.connect(self.cmd_left_flip)
        btn_frontflip = QPushButton(t['btn_frontflip'])
        btn_frontflip.clicked.connect(self.cmd_front_flip)
        btn_frontjump = QPushButton(t['btn_frontjump'])
        btn_frontjump.clicked.connect(self.cmd_front_jump)
        btn_frontpounce = QPushButton(t['btn_frontpounce'])
        btn_frontpounce.clicked.connect(self.cmd_front_pounce)
        
        flips_layout.addWidget(btn_handstand, 0, 0)
        flips_layout.addWidget(btn_backflip, 0, 1)
        flips_layout.addWidget(btn_leftflip, 0, 2)
        flips_layout.addWidget(btn_frontflip, 1, 0)
        flips_layout.addWidget(btn_frontjump, 1, 1)
        flips_layout.addWidget(btn_frontpounce, 1, 2)
        
        flips_group.setLayout(flips_layout)
        layout.addWidget(flips_group)
        
        # 互动动作组
        actions_group = QGroupBox(t['group_actions'])
        actions_layout = QGridLayout()
        
        btn_hello = QPushButton(t['btn_hello'])
        btn_hello.clicked.connect(self.cmd_hello)
        btn_stretch = QPushButton(t['btn_stretch'])
        btn_stretch.clicked.connect(self.cmd_stretch)
        btn_heart = QPushButton(t['btn_heart'])
        btn_heart.clicked.connect(self.cmd_heart)
        btn_pose = QPushButton(t['btn_pose'])
        btn_pose.clicked.connect(self.cmd_pose)
        btn_scrape = QPushButton(t['btn_scrape'])
        btn_scrape.clicked.connect(self.cmd_scrape)
        
        actions_layout.addWidget(btn_hello, 0, 0)
        actions_layout.addWidget(btn_stretch, 0, 1)
        actions_layout.addWidget(btn_heart, 0, 2)
        actions_layout.addWidget(btn_pose, 1, 0)
        actions_layout.addWidget(btn_scrape, 1, 1)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # 舞蹈表演组
        dance_group = QGroupBox(t['group_dance'])
        dance_layout = QGridLayout()
        
        btn_dance1 = QPushButton(t['btn_dance1'])
        btn_dance1.clicked.connect(self.cmd_dance1)
        btn_dance2 = QPushButton(t['btn_dance2'])
        btn_dance2.clicked.connect(self.cmd_dance2)
        
        dance_layout.addWidget(btn_dance1, 0, 0)
        dance_layout.addWidget(btn_dance2, 0, 1)
        
        dance_group.setLayout(dance_layout)
        layout.addWidget(dance_group)
        
        # 步态模式组
        gaits_group = QGroupBox(t['group_gaits'])
        gaits_layout = QGridLayout()
        
        btn_freewalk = QPushButton(t['btn_freewalk'])
        btn_freewalk.clicked.connect(self.cmd_free_walk)
        btn_upright = QPushButton(t['btn_upright'])
        btn_upright.clicked.connect(self.cmd_walk_upright)
        btn_crossstep = QPushButton(t['btn_crossstep'])
        btn_crossstep.clicked.connect(self.cmd_cross_step)
        btn_classicwalk = QPushButton(t['btn_classicwalk'])
        btn_classicwalk.clicked.connect(self.cmd_classic_walk)
        btn_staticwalk = QPushButton(t['btn_staticwalk'])
        btn_staticwalk.clicked.connect(self.cmd_static_walk)
        btn_trotrun = QPushButton(t['btn_trotrun'])
        btn_trotrun.clicked.connect(self.cmd_trot_run)
        btn_freejump = QPushButton(t['btn_freejump'])
        btn_freejump.clicked.connect(self.cmd_free_jump)
        btn_freebound = QPushButton(t['btn_freebound'])
        btn_freebound.clicked.connect(self.cmd_free_bound)
        btn_freeavoid = QPushButton(t['btn_freeavoid'])
        btn_freeavoid.clicked.connect(self.cmd_free_avoid)
        
        gaits_layout.addWidget(btn_freewalk, 0, 0)
        gaits_layout.addWidget(btn_classicwalk, 0, 1)
        gaits_layout.addWidget(btn_staticwalk, 0, 2)
        gaits_layout.addWidget(btn_upright, 1, 0)
        gaits_layout.addWidget(btn_crossstep, 1, 1)
        gaits_layout.addWidget(btn_trotrun, 1, 2)
        gaits_layout.addWidget(btn_freejump, 2, 0)
        gaits_layout.addWidget(btn_freebound, 2, 1)
        gaits_layout.addWidget(btn_freeavoid, 2, 2)
        
        gaits_group.setLayout(gaits_layout)
        layout.addWidget(gaits_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_state_tab(self):
        """Create robot state display tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 状态显示区域
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setFont(QFont("Monospace", 10))
        self.state_display.setStyleSheet("QTextEdit { background-color: #1E1E1E; color: #D4D4D4; }")
        layout.addWidget(self.state_display)
        
        # 刷新按钮
        refresh_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 刷新状态 / Refresh State")
        btn_refresh.clicked.connect(self.update_state_display)
        refresh_layout.addWidget(btn_refresh)
        
        # 自动刷新开关
        self.auto_refresh_checkbox = QCheckBox("自动刷新 / Auto Refresh")
        self.auto_refresh_checkbox.setChecked(True)
        refresh_layout.addWidget(self.auto_refresh_checkbox)
        
        layout.addLayout(refresh_layout)
        
        # 启动状态显示定时器
        self.state_display_timer = QTimer()
        self.state_display_timer.timeout.connect(self.update_state_display)
        self.state_display_timer.start(1000)  # 每1秒更新一次
        
        tab.setLayout(layout)
        return tab
    
    def update_state_display(self):
        """更新状态显示"""
        if not self.auto_refresh_checkbox.isChecked():
            return
        
        output = []
        output.append("=" * 70)
        output.append("Go2 机器人状态信息 / Robot State Information")
        output.append("=" * 70)
        output.append("")
        
        if self.go2_control.is_mock_mode:
            # 调试模式：显示完整格式但数值为0
            output.append("🔧 调试模式 (Mock Mode) - 未连接到Go2")
            output.append("   所有数值为0（仅用于测试GUI界面）")
            output.append("")
            
            # 显示完整的状态格式，但数值都为0
            self._append_mock_state_data(output)
            
        elif self.go2_control.latest_state is None:
            output.append("⚠️  等待机器人状态数据...")
            output.append("")
            output.append("可能原因：")
            output.append("  1. 机器人未开机")
            output.append("  2. 网络连接问题")
            output.append("  3. 状态话题未发布")
            output.append("")
        else:
            state = self.go2_control.latest_state
            self._append_real_state_data(output, state)
        
        output.append("=" * 70)
        output.append(f"更新时间 / Update Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
        output.append("=" * 70)
        
        self.state_display.setText("\n".join(output))
    
    def _append_mock_state_data(self, output):
        """添加模拟状态数据（调试模式，数值全为0）"""
        # 基本状态
        output.append("【基本状态 / Basic Status】")
        output.append(f"  错误代码 Error Code: 0")
        output.append("")
        
        # 模式状态
        output.append("【模式状态 / Mode Status】")
        output.append(f"  步态类型 Gait Type: 0")
        output.append(f"  模式 Mode: 0")
        output.append(f"  进度 Progress: 0")
        output.append("")
        
        # 位置信息
        output.append("【位置信息 / Position】")
        output.append(f"  X坐标:    0.000 m")
        output.append(f"  Y坐标:    0.000 m")
        output.append(f"  身体高度 Height:    0.000 m")
        output.append("")
        
        # 速度信息
        output.append("【速度信息 / Velocity】")
        output.append(f"  前后速度 VX:    0.000 m/s")
        output.append(f"  左右速度 VY:    0.000 m/s")
        output.append(f"  旋转速度 Vyaw:    0.000 rad/s")
        output.append("")
        
        # 姿态信息
        output.append("【姿态信息 / Attitude (IMU)】")
        output.append(f"  Roll:     0.000 rad  (  0.0°)")
        output.append(f"  Pitch:    0.000 rad  (  0.0°)")
        output.append(f"  Yaw:      0.000 rad  (  0.0°)")
        output.append("")
        
        # 足端力
        output.append("【足端力 / Foot Force】")
        foot_names = ["右前 FR", "左前 FL", "右后 RR", "左后 RL"]
        for name in foot_names:
            output.append(f"  {name}:      0.0 N")
        output.append(f"  总计 Total:      0.0 N")
        output.append(f"  ⚠️  机器人未站立 (<150N)")
        output.append("")
        
        # 足端位置
        output.append("【足端位置 / Foot Position (Body Frame)】")
        for name in foot_names:
            output.append(f"  {name}: x=  0.000, y=  0.000, z=  0.000 m")
        output.append("")
    
    def _append_real_state_data(self, output, state):
        """添加真实状态数据"""
        # 基本状态
        output.append("【基本状态 / Basic Status】")
        output.append(f"  错误代码 Error Code: {state.error_code}")
        if state.error_code != 0:
            output.append(f"    ⚠️  机器人报告错误！")
        output.append("")
        
        # 模式状态
        output.append("【模式状态 / Mode Status】")
        output.append(f"  步态类型 Gait Type: {state.gait_type}")
        output.append(f"  模式 Mode: {state.mode}")
        output.append(f"  进度 Progress: {state.progress}")
        output.append("")
        
        # 位置信息
        output.append("【位置信息 / Position】")
        output.append(f"  X坐标: {state.position[0]:>8.3f} m")
        output.append(f"  Y坐标: {state.position[1]:>8.3f} m")
        output.append(f"  身体高度 Height: {state.body_height:>8.3f} m")
        output.append("")
        
        # 速度信息
        output.append("【速度信息 / Velocity】")
        output.append(f"  前后速度 VX: {state.velocity[0]:>8.3f} m/s")
        output.append(f"  左右速度 VY: {state.velocity[1]:>8.3f} m/s")
        output.append(f"  旋转速度 Vyaw: {state.yaw_speed:>8.3f} rad/s")
        output.append("")
        
        # 姿态信息
        output.append("【姿态信息 / Attitude (IMU)】")
        output.append(f"  Roll:  {state.imu_state.rpy[0]:>8.3f} rad  ({state.imu_state.rpy[0]*57.3:>6.1f}°)")
        output.append(f"  Pitch: {state.imu_state.rpy[1]:>8.3f} rad  ({state.imu_state.rpy[1]*57.3:>6.1f}°)")
        output.append(f"  Yaw:   {state.imu_state.rpy[2]:>8.3f} rad  ({state.imu_state.rpy[2]*57.3:>6.1f}°)")
        output.append("")
        
        # 足端力
        output.append("【足端力 / Foot Force】")
        foot_names = ["右前 FR", "左前 FL", "右后 RR", "左后 RL"]
        total_force = 0
        for i, force in enumerate(state.foot_force):
            output.append(f"  {foot_names[i]}: {force:>8.1f} N")
            total_force += force
        output.append(f"  总计 Total: {total_force:>8.1f} N")
        
        # 判断站立状态
        if total_force > 150:
            output.append(f"  ✅ 机器人已站立 (>150N)")
        else:
            output.append(f"  ⚠️  机器人未站立 (<150N)")
        output.append("")
        
        # 足端位置
        output.append("【足端位置 / Foot Position (Body Frame)】")
        # foot_position_body 是12个float的一维数组，需要重组为4组x,y,z
        for i in range(4):
            x = state.foot_position_body[i*3]
            y = state.foot_position_body[i*3 + 1]
            z = state.foot_position_body[i*3 + 2]
            output.append(f"  {foot_names[i]}: x={x:>7.3f}, y={y:>7.3f}, z={z:>7.3f} m")
        output.append("")
    
    # 通用命令执行方法
    def execute_command(self, command_name, command_func, *args, allow_concurrent=False, **kwargs):
        """在后台线程中执行命令
        
        Args:
            command_name: 命令名称
            command_func: 命令函数
            allow_concurrent: 是否允许并发执行（用于快速命令如Move）
        """
        # 如果不允许并发且有正在执行的worker，等待它完成
        if not allow_concurrent and self.current_worker is not None:
            try:
                if self.current_worker.isRunning():
                    print(f"等待上一个命令完成... / Waiting for previous command to finish...")
                    return
            except RuntimeError:
                # Worker对象已被删除，清除引用
                self.current_worker = None
        
        # 创建新的worker线程
        worker = CommandWorker(
            self.go2_control.sport_client,
            command_name,
            command_func,
            *args,
            **kwargs
        )
        
        # 设置线程在结束后自动删除
        worker.finished.connect(worker.deleteLater)
        
        # 连接完成信号
        worker.command_finished.connect(self.on_command_finished)
        
        # 添加到worker列表，防止过早被垃圾回收
        self.worker_list.append(worker)
        
        # 启动线程
        worker.start()
        
        # 只有不允许并发时才保存为current_worker
        if not allow_concurrent:
            self.current_worker = worker
    
    def on_command_finished(self, command_name, result):
        """命令执行完成的回调"""
        if result is not None and str(result).startswith("Error"):
            print(f"命令执行错误: {command_name} - {result}")
        else:
            print(f"命令执行完成: {command_name}, 返回值: {result}")
        
        # 清理已完成的线程
        self.cleanup_finished_workers()
    
    def cleanup_finished_workers(self):
        """清理已完成的worker线程"""
        # 过滤掉已完成或已删除的worker
        cleaned_list = []
        for w in self.worker_list:
            try:
                if w.isRunning():
                    cleaned_list.append(w)
            except RuntimeError:
                # Worker对象已被Qt删除，跳过
                pass
        self.worker_list = cleaned_list
    
    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        print("\n正在关闭程序... / Closing program...")
        
        # 停止持续移动定时器
        if self.move_timer.isActive():
            self.move_timer.stop()
            print("✅ 定时器已停止 / Timer stopped")
        
        # 等待所有worker线程结束
        for worker in self.worker_list:
            try:
                if worker.isRunning():
                    print("⏳ 等待线程结束... / Waiting for thread to finish...")
                    worker.wait(1000)  # 等待最多1秒
                    if worker.isRunning():
                        worker.terminate()  # 强制终止
                        worker.wait()
            except RuntimeError:
                # Worker对象已被Qt删除，跳过
                pass
        
        print("✅ 所有线程已清理 / All threads cleaned up")
        event.accept()
    
    # 更新机器人状态显示
    def update_robot_status_display(self):
        """定时更新机器人状态显示"""
        t = TEXTS[self.current_lang]
        
        if self.go2_control.is_mock_mode:
            # 调试模式
            status_html = """
            <div style='background-color: #E3F2FD; color: #1565C0;'>
                <b>🔧 调试模式 (Mock Mode)</b><br>
                ✅ 无需真实机器人，所有功能可测试
            </div>
            """
        else:
            # 真实模式
            if self.go2_control.is_robot_standing():
                # 机器人已站立
                total_force = sum(self.go2_control.latest_state.foot_force) if self.go2_control.latest_state else 0
                status_html = f"""
                <div style='background-color: #C8E6C9; color: #2E7D32;'>
                    <b>✅ 机器人已准备好运动</b><br>
                    足端力: {total_force:.1f}N (已站立)
                </div>
                """
            else:
                # 机器人未站立
                if self.go2_control.latest_state is None:
                    status_html = """
                    <div style='background-color: #FFECB3; color: #F57C00;'>
                        <b>⚠️  等待机器人状态数据...</b><br>
                        请确保机器人已开机
                    </div>
                    """
                else:
                    total_force = sum(self.go2_control.latest_state.foot_force)
                    status_html = f"""
                    <div style='background-color: #FFCDD2; color: #C62828;'>
                        <b>⚠️  机器人未准备好</b><br>
                        足端力: {total_force:.1f}N (需要≥150N)<br>
                        请点击上方"准备运动"按钮
                    </div>
                    """
        
        self.robot_status_label.setText(status_html)
    
    # Command methods
    def cmd_prepare_motion(self):
        """准备运动：解除阻尼并站立"""
        t = TEXTS[self.current_lang]
        self.status_text.append("")
        self.status_text.append(t['preparing_motion'])
        self.log_command(t['preparing_motion'])
        
        # 步骤1：解除阻尼（通过StandUp命令自动解除）
        # 根据Unitree文档，调用StandUp会自动解除Damp模式
        
        # 步骤2：站立
        self.execute_command(t['cmd_stand_up'], self.go2_control.sport_client.StandUp)
        self.log_command(t['cmd_stand_up'])
        
        self.status_text.append(t['motion_ready'])
        
        print("\n" + "="*60)
        print("✅ 机器人准备命令已发送 / Robot Preparation Command Sent")
        print("="*60)
    
    def check_robot_ready(self):
        """检查机器人是否准备好运动（通过真实状态检测）"""
        # 使用真实的机器人状态判断
        if not self.go2_control.is_robot_standing():
            t = TEXTS[self.current_lang]
            reply = QMessageBox.question(
                self, 
                t['warn_not_ready'],
                t['warn_not_ready_msg'],
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cmd_prepare_motion()
                # 等待一小段时间让机器人站立
                import time
                time.sleep(2)
                return self.go2_control.is_robot_standing()
            else:
                return False
        return True
    
    def cmd_stand_up(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_stand_up'], self.go2_control.sport_client.StandUp)
        self.log_command(t['cmd_stand_up'])
    
    def cmd_stand_down(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_stand_down'], self.go2_control.sport_client.StandDown)
        self.log_command(t['cmd_stand_down'])
    
    def cmd_damp(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_damp'], self.go2_control.sport_client.Damp)
        self.log_command(t['cmd_damp'])
    
    def cmd_stop_move(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_stop'], self.go2_control.sport_client.StopMove)
        self.log_command(t['cmd_stop'])
    
    def cmd_balance_stand(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_balance'], self.go2_control.sport_client.BalanceStand)
        self.log_command(t['cmd_balance'])
    
    def cmd_recovery_stand(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_recovery'], self.go2_control.sport_client.RecoveryStand)
        self.log_command(t['cmd_recovery'])
    
    def cmd_sit(self):
        """坐下"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_sit'], self.go2_control.sport_client.Sit)
        self.log_command(t['btn_sit'])
    
    def cmd_rise_sit(self):
        """起坐"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_risesit'], self.go2_control.sport_client.RiseSit)
        self.log_command(t['btn_risesit'])
    
    def cmd_set_euler(self):
        """设置姿态角度"""
        t = TEXTS[self.current_lang]
        try:
            roll = float(self.roll_input.text())
            pitch = float(self.pitch_input.text())
            yaw = float(self.yaw_euler_input.text())
            
            # 验证范围
            if not (-0.5 <= roll <= 0.5) or not (-0.5 <= pitch <= 0.5) or not (-0.5 <= yaw <= 0.5):
                QMessageBox.warning(self, t['invalid_input'], 
                                  "姿态角度必须在 -0.5 到 0.5 rad 之间")
                return
            
            self.execute_command(f"Euler: roll={roll}, pitch={pitch}, yaw={yaw}",
                               self.go2_control.sport_client.Euler, roll, pitch, yaw)
            self.log_command(f"设置姿态: Roll={roll}, Pitch={pitch}, Yaw={yaw}")
        except ValueError:
            QMessageBox.warning(self, t['invalid_input'], t['number_error'])
    
    def cmd_reset_euler(self):
        """重置姿态到水平"""
        self.roll_input.setText("0.0")
        self.pitch_input.setText("0.0")
        self.yaw_euler_input.setText("0.0")
        self.execute_command("Reset Euler",
                           self.go2_control.sport_client.Euler, 0.0, 0.0, 0.0)
        self.log_command("重置姿态")
    
    def cmd_set_speed_level(self, button):
        """设置速度等级"""
        level = self.speed_level_group.id(button)
        speed_names = ["慢速", "中速", "快速"]
        self.execute_command(f"SpeedLevel: {level}",
                           self.go2_control.sport_client.SpeedLevel, level)
        self.log_command(f"设置速度等级: {level} ({speed_names[level]})")
        print(f"✅ 速度等级已设置为: {level} ({speed_names[level]})")
    
    def cmd_move(self):
        # 检查机器人是否准备好
        if not self.check_robot_ready():
            return
        
        t = TEXTS[self.current_lang]
        try:
            vx = float(self.vx_input.text())
            vy = float(self.vy_input.text())
            vyaw = float(self.vyaw_input.text())
            
            # Validate ranges
            if not (-1.0 <= vx <= 1.0) or not (-1.0 <= vy <= 1.0) or not (-1.0 <= vyaw <= 1.0):
                QMessageBox.warning(self, t['invalid_input'], t['value_range_error'])
                return
            
            # Move命令允许快速连续发送
            self.execute_command(f"Move: vx={vx}, vy={vy}, vyaw={vyaw}", 
                               self.go2_control.sport_client.Move, vx, vy, vyaw, 
                               allow_concurrent=True)
            self.log_command(f"Move: vx={vx}, vy={vy}, vyaw={vyaw}")
        except ValueError:
            QMessageBox.warning(self, t['invalid_input'], t['number_error'])
    
    def quick_move(self, vx, vy, vyaw):
        # Move命令允许快速连续发送
        self.execute_command(f"Quick Move: vx={vx}, vy={vy}, vyaw={vyaw}",
                           self.go2_control.sport_client.Move, vx, vy, vyaw,
                           allow_concurrent=True)
        self.log_command(f"Quick Move: vx={vx}, vy={vy}, vyaw={vyaw}")
    
    def start_continuous_move(self, vx, vy, vyaw):
        """开始持续移动（长按按钮时）"""
        # 检查机器人是否准备好
        if not self.check_robot_ready():
            return
        
        self.current_vx = vx
        self.current_vy = vy
        self.current_vyaw = vyaw
        
        # 立即发送第一次移动命令
        self.send_continuous_move()
        
        # 启动定时器，每100ms发送一次移动命令
        self.move_timer.start(100)
        
        print(f"开始持续移动 / Start continuous move: vx={vx}, vy={vy}, vyaw={vyaw}")
    
    def stop_continuous_move(self):
        """停止持续移动（松开按钮时）"""
        # 停止定时器
        self.move_timer.stop()
        
        # 发送停止命令（速度设为0）
        self.execute_command("Stop Continuous Move",
                           self.go2_control.sport_client.Move,
                           0.0, 0.0, 0.0,
                           allow_concurrent=True)
        
        print("停止持续移动 / Stop continuous move")
    
    def send_continuous_move(self):
        """定时发送持续移动命令"""
        self.execute_command(
            f"Continuous Move: vx={self.current_vx}, vy={self.current_vy}, vyaw={self.current_vyaw}",
            self.go2_control.sport_client.Move,
            self.current_vx,
            self.current_vy,
            self.current_vyaw,
            allow_concurrent=True
        )
    
    def cmd_hand_stand(self):
        t = TEXTS[self.current_lang]
        reply = QMessageBox.question(self, t['confirm'], 
                                     t['confirm_handstand'],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_command(t['cmd_handstand_start'], 
                               self.go2_control.sport_client.HandStand, True)
            self.log_command(t['cmd_handstand_start'])
            QTimer.singleShot(4000, lambda: self.end_hand_stand())
    
    def end_hand_stand(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_handstand_end'],
                           self.go2_control.sport_client.HandStand, False)
        self.log_command(t['cmd_handstand_end'])
    
    def cmd_back_flip(self):
        t = TEXTS[self.current_lang]
        reply = QMessageBox.question(self, t['confirm'], 
                                     t['confirm_backflip'],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_command(t['btn_backflip'], 
                               self.go2_control.sport_client.BackFlip)
            self.log_command(t['btn_backflip'])
    
    def cmd_left_flip(self):
        t = TEXTS[self.current_lang]
        reply = QMessageBox.question(self, t['confirm'], 
                                     t['confirm_leftflip'],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_command(t['btn_leftflip'],
                               self.go2_control.sport_client.LeftFlip)
            self.log_command(t['btn_leftflip'])
    
    def cmd_free_walk(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_freewalk'],
                           self.go2_control.sport_client.FreeWalk)
        self.log_command(t['btn_freewalk'])
    
    def cmd_walk_upright(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_upright_start'],
                           self.go2_control.sport_client.WalkUpright, True)
        self.log_command(t['cmd_upright_start'])
        QTimer.singleShot(4000, lambda: self.end_walk_upright())
    
    def end_walk_upright(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_upright_end'],
                           self.go2_control.sport_client.WalkUpright, False)
        self.log_command(t['cmd_upright_end'])
    
    def cmd_cross_step(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_crossstep_start'],
                           self.go2_control.sport_client.CrossStep, True)
        self.log_command(t['cmd_crossstep_start'])
        QTimer.singleShot(4000, lambda: self.end_cross_step())
    
    def end_cross_step(self):
        t = TEXTS[self.current_lang]
        self.execute_command(t['cmd_crossstep_end'],
                           self.go2_control.sport_client.CrossStep, False)
        self.log_command(t['cmd_crossstep_end'])
    
    # 新增高级技能命令
    def cmd_front_flip(self):
        """前空翻"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_frontflip'],
                           self.go2_control.sport_client.FrontFlip)
        self.log_command(t['btn_frontflip'])
    
    def cmd_front_jump(self):
        """前跳"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_frontjump'],
                           self.go2_control.sport_client.FrontJump)
        self.log_command(t['btn_frontjump'])
    
    def cmd_front_pounce(self):
        """前扑"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_frontpounce'],
                           self.go2_control.sport_client.FrontPounce)
        self.log_command(t['btn_frontpounce'])
    
    def cmd_hello(self):
        """招手"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_hello'],
                           self.go2_control.sport_client.Hello)
        self.log_command(t['btn_hello'])
    
    def cmd_stretch(self):
        """伸展"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_stretch'],
                           self.go2_control.sport_client.Stretch)
        self.log_command(t['btn_stretch'])
    
    def cmd_heart(self):
        """比心"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_heart'],
                           self.go2_control.sport_client.Heart)
        self.log_command(t['btn_heart'])
    
    def cmd_pose(self):
        """摆姿势"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_pose'],
                           self.go2_control.sport_client.Pose, True)
        self.log_command(t['btn_pose'])
        QTimer.singleShot(4000, lambda: self._end_pose())
    
    def _end_pose(self):
        self.go2_control.sport_client.Pose(False)
    
    def cmd_scrape(self):
        """刮擦"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_scrape'],
                           self.go2_control.sport_client.Scrape)
        self.log_command(t['btn_scrape'])
    
    def cmd_dance1(self):
        """舞蹈1"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_dance1'],
                           self.go2_control.sport_client.Dance1)
        self.log_command(t['btn_dance1'])
    
    def cmd_dance2(self):
        """舞蹈2"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_dance2'],
                           self.go2_control.sport_client.Dance2)
        self.log_command(t['btn_dance2'])
    
    def cmd_classic_walk(self):
        """经典步态"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_classicwalk'],
                           self.go2_control.sport_client.ClassicWalk, True)
        self.log_command(t['btn_classicwalk'])
    
    def cmd_static_walk(self):
        """静态步态"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_staticwalk'],
                           self.go2_control.sport_client.StaticWalk)
        self.log_command(t['btn_staticwalk'])
    
    def cmd_trot_run(self):
        """小跑"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_trotrun'],
                           self.go2_control.sport_client.TrotRun)
        self.log_command(t['btn_trotrun'])
    
    def cmd_free_jump(self):
        """自由跳"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_freejump'],
                           self.go2_control.sport_client.FreeJump, True)
        self.log_command(t['btn_freejump'] + " - Start")
        QTimer.singleShot(4000, lambda: self._end_free_jump())
    
    def _end_free_jump(self):
        self.go2_control.sport_client.FreeJump(False)
        self.log_command("Free Jump - End")
    
    def cmd_free_bound(self):
        """自由跳跃"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_freebound'],
                           self.go2_control.sport_client.FreeBound, True)
        self.log_command(t['btn_freebound'] + " - Start")
        QTimer.singleShot(4000, lambda: self._end_free_bound())
    
    def _end_free_bound(self):
        self.go2_control.sport_client.FreeBound(False)
        self.log_command("Free Bound - End")
    
    def cmd_free_avoid(self):
        """自由避障"""
        t = TEXTS[self.current_lang]
        self.execute_command(t['btn_freeavoid'],
                           self.go2_control.sport_client.FreeAvoid, True)
        self.log_command(t['btn_freeavoid'] + " - Start")
        QTimer.singleShot(4000, lambda: self._end_free_avoid())
    
    def _end_free_avoid(self):
        self.go2_control.sport_client.FreeAvoid(False)
        self.log_command("Free Avoid - End")
    
    def log_command(self, command):
        """Log command to status text and file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {command}"
        
        # Update status text
        self.status_text.append(log_entry)
        
        # Save to file
        with open("go2_command_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")
        
        # Update log tab
        self.log_tab.update_log()
        
        print(log_entry)


class LogTab(QWidget):
    """Log viewing tab"""
    
    def __init__(self, parent: DebugWindow):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        
        # Log list
        self.log_list = QListWidget()
        self.log_list.setSelectionMode(QListWidget.SingleSelection)
        self.layout.addWidget(self.log_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        t = TEXTS[parent.current_lang]
        self.refresh_button = QPushButton(t['btn_refresh'])
        self.refresh_button.clicked.connect(self.update_log)
        self.clear_button = QPushButton(t['btn_clear'])
        self.clear_button.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.refresh_button)
        btn_layout.addWidget(self.clear_button)
        self.layout.addLayout(btn_layout)
        
        self.setLayout(self.layout)
        self.update_log()
    
    def update_log(self):
        """Update log display"""
        self.log_list.clear()
        if os.path.exists("go2_command_log.txt"):
            with open("go2_command_log.txt", "r") as log_file:
                lines = log_file.readlines()
                for line in lines:
                    item = QListWidgetItem(line.strip())
                    self.log_list.addItem(item)
            # Scroll to bottom
            self.log_list.scrollToBottom()
    
    def clear_log(self):
        """Clear log file"""
        t = TEXTS[self.parent.current_lang]
        reply = QMessageBox.question(self, t['confirm'], 
                                     t['confirm_clear_log'],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if os.path.exists("go2_command_log.txt"):
                os.remove("go2_command_log.txt")
            self.log_list.clear()
            print("Log cleared")


def main():
    """Main function"""
    print("="*60)
    print("Go2 机器人调试窗口 / Go2 Robot Debug Window")
    print("="*60)
    
    # Parse command line arguments
    network_interface = None
    force_mock = False
    
    for arg in sys.argv[1:]:
        if arg == "--mock" or arg == "-m":
            force_mock = True
            print("🔧 强制启用模拟模式 / Force mock mode enabled")
        else:
            network_interface = arg
            print(f"使用网络接口 / Using network interface: {network_interface}")
    
    if not force_mock:
        print("\n检测网络环境... / Detecting network environment...")
    
    print("\n初始化 Go2 控制... / Initializing Go2 control...")
    
    # Initialize Go2 control
    go2_control = Go2Control(network_interface, force_mock=force_mock)
    
    if go2_control.is_mock_mode:
        print("\n" + "="*60)
        print("🔧 调试/模拟模式 (Mock Mode)")
        print("="*60)
        print("✅ 无需连接真实机器人")
        print("✅ 所有GUI功能可以正常测试")
        print("✅ 长按按钮可以测试持续移动")
        print("✅ 命令执行结果会在终端显示")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✅ 真实模式 (Real Mode)")
        print("="*60)
        print("警告 / WARNING: 确保机器人周围没有障碍物！")
        print("Ensure there are no obstacles around the robot!")
        print("="*60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    window = DebugWindow(go2_control)
    window.show()
    
    print("\n调试窗口已打开！/ Debug window opened!")
    print("提示 / Tip: 使用顶部菜单切换语言 / Use top menu to switch language")
    print("\n用法 / Usage:")
    print("  python3 go2_debug_window.py              # 自动检测模式")
    print("  python3 go2_debug_window.py --mock       # 强制模拟模式")
    print("  python3 go2_debug_window.py eth0         # 指定网络接口")
    print("  python3 go2_debug_window.py eth0 --mock  # 指定接口+模拟模式")
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()





