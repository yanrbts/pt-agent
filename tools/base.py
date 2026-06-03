from abc import ABC, abstractmethod

class BasePentestTool(ABC):
    """
    工业级渗透工具刚性基类。
    所有手写的 Skill 必须继承此类，确保‘说明书’与‘物理执行’强绑定。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具在 Function Calling 中的唯一标识符"""
        pass

    @property
    @abstractmethod
    def schema(self) -> dict:
        """符合 OpenAI / Anthropic 标准的 JSON Schema 说明书"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """
        物理执行面。内核级异常拦截必在此处落地。
        不管底层命令怎么炸，必须返回纯净的 dict，绝不允许抛出未捕获异常。
        """
        pass