"""
字符文本分割器组件
基于字符数量和分割符对文本进行分割
"""

from typing import Any, Dict, Optional
from unittest import result
from langchain_text_splitters import CharacterTextSplitter

from components.base.component import BaseComponent

class CharacterTextSplitterComponent(BaseComponent):
    """基于字符的文本分割器，将长文本分割成较小的片段"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            "name": 'CharacterTextSplitter',
            "type": 'text_spliter',
            "category": 'Text Splitters',
            "description": '按照字符数和分隔符将长文本分割成小块',
            "inputs": [
                {
                    "name": 'documents',
                    "type": 'list',
                    "required": True,
                    "description": "要分割的文档列表，每个文档包含page_content和metadata"
                }
            ],
            "outputs": [
                {
                    "name": 'splits',
                    "type": 'list',
                    "description": '分割后的文档列表，每个文档包含内容和原数据'
                }
            ],
            "params": [
                {
                    "name": 'chunk_size', 
                    "type": 'number',
                    "required": False,
                    "default": 1000,
                    "description": '每个文本块的目标大小（字符数）'
                },
                {
                    "name": 'chunk_overlap',
                    "type": 'number',
                    "requied": False,
                    "default": 200,
                    "description": '相邻文本块之间的重叠字符数'
                },
                {
                    "name": 'separator',
                    "type": 'string',
                    "required": False,
                    "default": '\n',
                    "description": '分隔文本时使用的分割符'
                }
            ]
        }

    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        异步执行组件的核心处理逻辑。在组件运行过程中,异步编程的作用包括:

        1. 提高系统并发性能:
           - 当多个组件同时运行时,异步可以让CPU在等待IO时切换执行其他任务
           - 例如在等待PDF文件读取时,可以同时执行文本分割等计算任务
           - 避免单个组件阻塞整个工作流程的执行

        2. 支持长时间运行的任务:
           - 文本分割等耗时操作可以异步执行,不会阻塞主线程
           - 系统可以同时处理多个文档,提高整体吞吐量
           - 用户界面保持响应,可以查看进度或取消任务

        3. 资源利用更高效:
           - IO密集型任务(如文件读写)可以并发执行
           - CPU密集型任务(如文本处理)可以在多个协程间调度
           - 内存和CPU资源得到更均衡的利用

        4. 与其他异步组件协同:
           - 上游的文档加载器异步读取文件
           - 本组件异步处理文本分割
           - 下游的向量存储异步保存结果
           - 形成完整的异步处理管道
        """

        """
        执行组件的核心处理逻辑

        Args：
            inputs: 输入数据，包含文档列表
            params: 参数数据，包含分割配置

        Return：
            Dict[str,Any]: 包含分割后的文档列表的字典
        """

        # 验证输入和参数
        self.validate_inputs(inputs)
        self.validate_params(params)
        # 注意:inputs和params实际上是字典类型,而不是列表
        # 组件定义中的inputs和params是列表,用于描述接口规范
        # 实际执行时传入的是字典,所以可以用get方法获取值
        documents = inputs.get("documents", [])

        # 获取分割参数
        chunk_size = int(params.get("chunk_size", 1000))
        chunk_overlap = int(params.get("chunk_overlap", 200))
        separator = params.get("separator", "\n")

        # 转换文档格式为langchain的Document对象
        from langchain_core.documents import Document
        docs = []
        for doc in documents:
            # 这段代码处理两种数据格式:
            # 1. 字典格式: {"page_content": "文本内容", "metadata": {...}}
            # 2. 字符串格式: "文本内容"
            
            # 如果输入是字典且包含page_content字段
            if isinstance(doc, dict) and "page_content" in doc:
                # metadata是一个可选的字典类型字段,用于存储文档的额外信息（在document_loader中自动提取）
                # 当上游组件(如文件加载器)处理Word文档时,会自动提取:
                # 1. 文件系统信息:
                #    - 文件名、路径
                #    - 创建时间、修改时间
                #    - 文件大小等
                # 2. Word文档属性:
                #    - 标题、作者
                #    - 创建日期、最后修改日期
                #    - 页数、字数统计等
                # 3. 其他自定义信息:
                #    - 文档分类标签
                #    - 处理状态标记
                #    - 业务相关属性
                # metadata字段会被自动创建为字典类型,可以灵活存储任意键值对
                docs.append(Document(
                    page_content = doc["page_content"],  # 文档的主要文本内容
                    metadata = doc.get("metadata", {})   # metadata是dict类型,由上游组件自动提取和填充
                ))
            elif isinstance(doc, str):
                # 纯文本输入不包含元数据
                docs.append(Document(page_content = doc))
        
        # 创建langchain的文本分割器
        text_splitter = CharacterTextSplitter(
            separator = separator,
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        # 分割文档
        split_docs = text_splitter.split_documents(docs)
        
        # 格式化输出
        # 这个列表推导式将langchain的Document对象列表转换为标准字典格式
        # 遍历split_docs中的每个Document对象:
        # - 提取doc.page_content作为文本内容
        # - 提取doc.metadata作为元数据
        # - 组装成{"page_content": 内容, "metadata": 元数据}的字典
        result_docs = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in split_docs
        ]

        return {"documents": result_docs}