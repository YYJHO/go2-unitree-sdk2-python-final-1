#!/usr/bin/python
"""
Go2 机器狗 + 在线大模型 集成示例
演示如何同时控制机器狗和调用在线API
"""

import sys
import time
import requests
import json
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


class Go2LLMController:
    """Go2机器狗与大模型集成控制器"""
    
    def __init__(self, network_interface):
        """
        初始化控制器
        
        Args:
            network_interface: 连接机器狗的网络接口名称
        """
        print("=" * 60)
        print("Go2 机器狗 + 在线大模型 集成示例")
        print("=" * 60)
        print(f"网络接口: {network_interface}")
        print("=" * 60)
        
        # 初始化机器狗连接
        print("\n1. 初始化机器狗连接...")
        ChannelFactoryInitialize(0, network_interface)
        self.client = SportClient()
        self.client.SetTimeout(10.0)
        self.client.Init()
        print("   ✅ 机器狗连接成功")
        
        # 测试互联网连接
        print("\n2. 测试互联网连接...")
        if self.test_internet():
            print("   ✅ 互联网连接正常")
        else:
            print("   ⚠️  互联网连接失败，API调用可能不可用")
        
        self.is_standing = False
        
    def test_internet(self):
        """测试互联网连接"""
        try:
            response = requests.get("http://www.baidu.com", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def call_llm_api(self, prompt, api_url=None, api_key=None):
        """
        调用在线大模型API（示例）
        
        Args:
            prompt: 提示词
            api_url: API地址（根据您使用的服务修改）
            api_key: API密钥（根据您使用的服务修改）
        
        Returns:
            str: API返回的文本
        """
        print(f"\n🤖 调用大模型API...")
        print(f"   提示词: {prompt}")
        
        # 这里是一个示例框架，您需要根据实际使用的API修改
        # 例如：OpenAI、通义千问、文心一言、智谱AI等
        
        # 示例1: OpenAI格式
        if api_url and api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                data = {
                    "model": "gpt-3.5-turbo",  # 根据实际模型修改
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                response = requests.post(
                    api_url, 
                    headers=headers, 
                    json=data, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                    print(f"   ✅ API响应: {answer}")
                    return answer
                else:
                    print(f"   ❌ API错误: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"   ❌ 调用失败: {e}")
                return None
        else:
            # 模拟响应（用于测试）
            print("   ℹ️  模拟模式（未配置真实API）")
            mock_response = "这是一个模拟响应。请配置真实的API参数。"
            print(f"   响应: {mock_response}")
            return mock_response
    
    def stand_up(self):
        """站立"""
        print("\n📍 执行动作: 站立")
        self.client.StandUp()
        self.is_standing = True
        time.sleep(2)
        print("   ✅ 站立完成")
    
    def move_forward(self, duration=2, speed=0.3):
        """前进"""
        print(f"\n📍 执行动作: 前进 ({duration}秒, {speed}m/s)")
        start = time.time()
        while time.time() - start < duration:
            self.client.Move(speed, 0, 0)
            time.sleep(0.1)
        self.client.StopMove()
        print("   ✅ 前进完成")
    
    def turn_left(self, duration=2):
        """左转"""
        print(f"\n📍 执行动作: 左转 ({duration}秒)")
        start = time.time()
        while time.time() - start < duration:
            self.client.Move(0, 0, 0.5)
            time.sleep(0.1)
        self.client.StopMove()
        print("   ✅ 左转完成")
    
    def sit_down(self):
        """趴下"""
        print("\n📍 执行动作: 趴下")
        self.client.StandDown()
        self.is_standing = False
        time.sleep(2)
        print("   ✅ 趴下完成")
    
    def parse_command_with_llm(self, user_input, api_url=None, api_key=None):
        """
        使用大模型解析用户指令并执行
        
        Args:
            user_input: 用户输入的自然语言指令
        """
        # 构造提示词
        prompt = f"""
你是一个机器狗控制助手。用户说："{user_input}"

请判断用户想让机器狗执行什么动作，只返回以下JSON格式（不要其他内容）：
{{
    "action": "stand/forward/turn_left/sit",
    "duration": 2,
    "speed": 0.3
}}

如果无法识别，返回：{{"action": "unknown"}}
"""
        
        # 调用大模型
        response = self.call_llm_api(prompt, api_url, api_key)
        
        if response:
            try:
                # 解析JSON响应
                command = json.loads(response)
                action = command.get("action", "unknown")
                
                # 执行对应动作
                if action == "stand":
                    self.stand_up()
                elif action == "forward":
                    duration = command.get("duration", 2)
                    speed = command.get("speed", 0.3)
                    self.move_forward(duration, speed)
                elif action == "turn_left":
                    duration = command.get("duration", 2)
                    self.turn_left(duration)
                elif action == "sit":
                    self.sit_down()
                else:
                    print("   ⚠️  无法识别的指令")
            except json.JSONDecodeError:
                print("   ⚠️  大模型返回格式错误")
    
    def demo_sequence(self):
        """演示序列"""
        print("\n" + "=" * 60)
        print("开始演示序列")
        print("=" * 60)
        
        # 1. 测试大模型API
        print("\n【步骤1】测试大模型API")
        self.call_llm_api("你好，请用一句话介绍机器狗")
        
        # 2. 控制机器狗
        print("\n【步骤2】控制机器狗")
        self.stand_up()
        time.sleep(1)
        
        self.move_forward(duration=2, speed=0.2)
        time.sleep(1)
        
        self.turn_left(duration=1)
        time.sleep(1)
        
        self.sit_down()
        
        print("\n" + "=" * 60)
        print("演示完成")
        print("=" * 60)
    
    def cleanup(self):
        """清理资源"""
        print("\n清理中...")
        self.client.StopMove()
        time.sleep(0.5)
        self.client.Damp()
        print("✅ 清理完成")


def main():
    """主函数"""
    
    # 获取网络接口参数
    if len(sys.argv) < 2:
        print("用法: python3 go2_with_llm_example.py <网络接口>")
        print("示例: python3 go2_with_llm_example.py enp5s0")
        sys.exit(1)
    
    network_interface = sys.argv[1]
    
    # ==================== 配置区 ====================
    # 在这里配置您的大模型API
    API_URL = None  # 例如: "https://api.openai.com/v1/chat/completions"
    API_KEY = None  # 您的API密钥
    # ==============================================
    
    try:
        # 创建控制器
        controller = Go2LLMController(network_interface)
        
        # 运行演示
        print("\n警告: 确保机器狗周围2米内无障碍物!")
        input("按Enter开始演示...")
        
        controller.demo_sequence()
        
        # 交互模式（可选）
        print("\n" + "=" * 60)
        print("进入交互模式（输入'quit'退出）")
        print("=" * 60)
        
        while True:
            user_input = input("\n请输入指令: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # 简单的指令解析（不使用LLM）
            if "站" in user_input or "stand" in user_input.lower():
                controller.stand_up()
            elif "前" in user_input or "forward" in user_input.lower():
                controller.move_forward()
            elif "转" in user_input or "turn" in user_input.lower():
                controller.turn_left()
            elif "趴" in user_input or "sit" in user_input.lower():
                controller.sit_down()
            else:
                print("支持的指令: 站立、前进、转弯、趴下")
                # 如果配置了API，可以调用：
                # controller.parse_command_with_llm(user_input, API_URL, API_KEY)
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'controller' in locals():
            controller.cleanup()


if __name__ == '__main__':
    main()





