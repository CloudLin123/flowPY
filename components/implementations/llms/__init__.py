"""
LLM模型组件集合
此模块包含各种大语言模型接口组件

__all__ 在本项目中的作用:

1. 控制模块导入行为:
   当其他模块使用 'from components.implementations.llms import *' 时,
   只会导入 __all__ 列表中指定的这些组件类。

2. 明确公开API:
   通过 __all__ 明确声明这些LLM组件类是此模块的公开接口,
   其他代码应该使用这些组件类来调用不同的语言模型。

3. 组件注册机制:
   在项目启动时,这些组件类会被自动注册到组件管理器中。
   例如:
   - 首先通过 import * 导入所有组件
   - 组件管理器遍历已导入的组件类
   - 将它们注册为可用的LLM实现
   - 后续可以通过组件名称动态创建对应的LLM实例

4. 版本管理:
   当需要增加新的模型支持时,只需:
   - 创建新的组件类文件
   - 在这里import
   - 添加到 __all__ 列表中
   即可使新组件在整个系统中可用
"""

# 导入现有的LLM组件
from .deepseekr1 import DeepSeekComponent
from .gemini import GeminiComponent

# 导入新增的开源模型组件
from .huggingface import HuggingFaceComponent
from .llama import LlamaCppComponent

# 导出所有组件类，确保会被注册
# __all__ 变量定义了此模块公开的API接口
__all__ = [
    "DeepSeekComponent",
    "GeminiComponent", 
    "LlamaCppComponent",
    "HuggingFaceComponent"
]