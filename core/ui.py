# core/ui.py
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.theme import Theme

# 保持自定义主题
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "critical": "bold white on red",
})

console = Console(theme=custom_theme)

class PentestUI:
    @staticmethod
    def banner():
        """渲染全新精简、高辨识度的个性化赛博黑客 Banner"""
        # 极简紧凑型艺术字，仅占用 3 行高度，带物理边界感
        logo_lines = [
            r" ⚡ [ 🧠 DEEPSEEK - PENTEST.AGENT v2.6 ] ⚡",
            r" ┌────────────────────────────────────────────────────────┐",
            r" │  🧬 [SYS.INIT] => [■■■■■■■■■■■■■■■■] 100% KERNEL READY │",
            r" └────────────────────────────────────────────────────────┘"
        ]
        
        # 使用矩阵绿（Matrix Green）和淡青色组合
        logo_text = Text("\n".join(logo_lines), style="bold green")
        console.print(logo_text)

    @staticmethod
    def get_user_instruction() -> str:
        """安全捕获用户输入的渗透指令"""
        console.print("\n[bold yellow]✉️  [系统就绪][/bold yellow] 请输入安全测试或资产审计任务：")
        instruction = Prompt.ask("[bold green]🏴‍☠️ >>[/bold green]")
        if not instruction.strip():
            console.print("[error]❌ 指令不能为空。[/error]")
            sys.exit(1)
        return instruction

    @staticmethod
    def log_control_turn(turn: int):
        """精简版轮次提示，防止刷屏"""
        console.print(f"\n[bold info]🔄 [TURN {turn}][/bold info] 🧠 DeepSeek 正在对当前资产状态进行推理...")

    @staticmethod
    def print_reasoning(content: str):
        """渲染思维链"""
        console.print(Panel(
            Text(content, style="italic dim white"),
            title="🧠 DeepSeek 思维链 (Reasoning)",
            border_style="blue",
            expand=False
        ))

    @staticmethod
    def log_intercept(count: int):
        console.print(f"[bold warning]🛡️  [拦截防线][/bold warning] 拦截到大模型请求物理调用 [bold yellow]{count}[/bold yellow] 个本地渗透工具...")

    @staticmethod
    def log_tool_start(func_name: str, args: dict):
        console.print(f"  [cyan]🔧 [EXEC][/cyan] [bold white]{func_name}[/bold white] ➔ Arguments: {args}")

    @staticmethod
    def log_tool_error(func_name: str, error_msg: str):
        console.print(f"  [bold error]❌ [CRITICAL][/bold error] 技能 {func_name} 物理异常: {error_msg}")

    @staticmethod
    def print_final_report(report: str):
        console.print("\n")
        console.print(Panel(
            report,
            title="📊 FINAL SECURITY AUDIT REPORT",
            border_style="bold green",
            padding=(1, 2)
        ))