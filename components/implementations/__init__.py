"""
将implementations下的所有应用集成到主应用
即更新 components/implementations/__init__.py 文件以包含新组件
"""

from .llms import *
from .memory import *
from .chains import *

# 以下时RAG（检索增强生成）的组件
"""
加载: 使用文档加载器从各种格式获取原始内容
分割: 使用文本分割器将长文档切分成适当大小的块
嵌入: 将文本块转换为向量表示(通常使用嵌入模型)
存储: 在向量数据库中存储文本及其向量表示
检索: 基于查询的相似度，从向量存储中检索相关文本
生成: 将检索到的相关上下文与用户查询一起发送给LLM
"""
from .vector_stores import *
from .text_splitters import *
from .document_loaders import *
