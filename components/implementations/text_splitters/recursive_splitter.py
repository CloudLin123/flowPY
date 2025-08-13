"""
递归文本分割器
递归的使用一系列分割符对文本进行分割
"""

from typing import Any, Dict, List, Optional
from unicodedata import category
from langchain_text_splitters import RecursiveCharacterTextSplitter

from components.base.component import BaseComponent

class RecursiveTextSplitterComponent(BaseComponent):
    """递归文本分割器，按多级分割符将长文本分割成小块"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            "name": 'RecursiveCharacterTextSplitter',
            "type": 'text_splitter',
            "category": 'Text_Splitters',
            "description": '使用递归的方式按多级分隔符分割文本',
            "inputs": [
                {
                    "name": 'documents',
                    "type": 'list',
                    "required": True,
                    "description": '要分割的文档列表，每个文档包含page_content和metadata'
                }
            ],
            "outputs": [
                {
                    "name": 'documents',
                    "type": 'list',
                    "description": '分割后的文档列表，每个文档包含内容和元数据'
                }
            ],
            "params": [
                {
                    "name": 'chunk_size',
                    "type": 'number',
                    "required": False, # 非必填，有默认值
                    "default": 1000,
                    "description": '每个文本块的目标大小(字符数)'
                },
                {
                    "name": 'chunk_overlap',
                    "type": 'number',
                    "required": False,
                    "default": 200,
                    "description": '相邻文本块之间的重叠字符数'
                }
            ]
        }

    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理器

        Args:
            inputs: 输入数据,包含文档列表
            params：参数数据,包含分割配置

        Returns:
            Dict[str, Any]: 包含分割后文档列表的字典
        """

        # 验证输入和参数
        self.validate_inputs(inputs)
        self.validate_params(params)

        # 获取输入文档
        documents = inputs.get("documents", [])

        # 获取输入文档
        chunk_size = int(params.get("chunk_size", 1000))
        chunk_overlap = int(params.get("chunk_overlap", 200))

        # 转换文档格式为langchain的Document对象
        from langchain_core.documents import Document
        docs = []
        for doc in documents:
            if isinstance(doc, dict) and 'page_content' in doc:
                docs.append(Document(
                    page_content = doc["page_content"],
                    metadata = doc.get("metadata", {})
                ))
            elif isinstance(doc, str):
                docs.append(Document(page_content = doc))

        # 创建递归分割器（使用默认的分隔符列表）
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        # 分割文档
        split_docs = text_splitter.split_documents(docs)

        # 格式化输出
        result_docs = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in split_docs
        ]

        return {"documents": result_docs}