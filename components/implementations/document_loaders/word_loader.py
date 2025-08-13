"""
word文档加载器组件
使用langchain_community.document_loaders的Docx2txtLoader库
"""

from json import load
from typing import Any, Dict, Optional
import os
from langchain_community.document_loaders import Docx2txtLoader

from components.base.component import BaseComponent

class WordLoaderComponent(BaseComponent):
    """Word文档加载器组件，将Word文档转换为文本"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            "name": 'WordLoader',
            "type": 'document_loader',
            "category": 'Document Loader',
            "description": '加载Word(.docx)文档并提取其中的文本内容',
            "inputs": [], # 无输入，直接从参数获取文件路径
            "outputs": [
                {
                    "name": 'documents',
                    "type": 'list',
                    "description": '加载的文档列表，每个文档包含的内容和元数据'
                }
            ],
            "params": [
                {
                    "name": 'file_path',
                    "type": 'string',
                    "required": True,
                    "description": 'Word文件的路径(.docx格式)'
                }
            ]
        }
    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理逻辑

        Args：
            inputs: 输入数据(空)
            params: 组件参数数据，包含文件路径

        Rerurns：
            Dict[str, Any]: 包含文档列表的字典
        """

        # 验证参数
        self.validate_params(params)

        # 获取文件路径
        file_path = params.get('file_path')

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到Word文件：{file_path}")

        # 使用Docx2txtLoader加载文档
        loader = Docx2txtLoader(file_path)
        documents = loader.load()

        # 格式化输出为字典列表
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return {"documents": formatted_docs}