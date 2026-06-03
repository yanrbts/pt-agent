import sys
import signal
from core.engine import PentestAgentEngine
from core.ui import PentestUI

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号，实现优雅退出"""
    print("\n\n⚠️  检测到 Ctrl+C，正在优雅退出...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    try:
        PentestUI.banner()
        user_instruction = PentestUI.get_user_instruction()
        engine = PentestAgentEngine()
        final_report = engine.run_loop(user_instruction, max_turns=6)
        PentestUI.print_final_report(final_report)
        
    except KeyboardInterrupt:
        print("渗透测试已被手动终止")
    except Exception as e:
        print(f"程序发生异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()