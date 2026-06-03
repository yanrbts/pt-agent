import os
import importlib
from .base import BasePentestTool

def load_all_skills() -> dict[str, BasePentestTool]:
    """
    【动态路由黑魔法】自动扫描当前目录下所有的 python 脚本，
    实例化所有继承了 BasePentestTool 的 Skill，并组装成字典返回。
    """
    skills_registry = {}
    current_dir = os.path.dirname(__file__)

    for file in os.listdir(current_dir):
        if file.endswith(".py") and file != "base.py" and not file.startswith("__"):
            module_name = f"tools.{file[:-3]}"
            module = importlib.import_module(module_name)
            
            # 寻找模块中继承了 BasePentestTool 的类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePentestTool) and attr != BasePentestTool:
                    instance = attr()
                    skills_registry[instance.name] = instance
                    
    return skills_registry