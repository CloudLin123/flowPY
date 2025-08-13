"""
PDF文档加载器组件
使用langchain_community.document_loaders.PyPDFLoader库加载PDF文件内容
"""

from typing import Any, Dict, Optional
import os
from langchain_community.document_loaders import PyPDFLoader

from components.base.component import BaseComponent

class PDFLoaderComponent(BaseComponent):
    """PDF文档加载器组件，将PDF文档转换为文本"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """
        获取组件元数据,用于前后端交互和组件配置
        
        这个方法在组件运行过程中的作用:
        1. 前端初始化:
           - 前端根据name和description展示组件的基本信息
           - 根据category对组件进行分类展示
           - type标识这是一个文档加载器组件
        
        2. 参数配置:
           - params定义了组件需要的参数(file_path)
           - 前端根据params渲染参数配置表单
           - required=True表示文件路径为必填项
           - 用户填写PDF文件路径后提交给后端
        
        3. 输入输出规范:
           - inputs为空列表,表示不需要其他组件的输入
           - outputs定义输出格式为文档列表
           - execute()方法负责实际提取文本内容和元数据:
             * 使用PyPDFLoader加载PDF文件
             * load()方法提取每页的文本内容(page_content)
             * 自动生成包含页码等信息的元数据(metadata)
             * 将结果格式化为标准文档列表
           - 下游组件可以根据这个格式处理文档
        
        4. 数据校验:
           - 后端根据params定义校验参数格式
           - 确保file_path参数存在且为字符串类型
           - 校验通过后再执行组件的核心逻辑
        """
        return {
            "name": 'PDFLoader',
            "type": 'document_loader', 
            "category": 'Document Loader',
            "description": '加载PDF文档给并提取其中的文本内容',
            "inputs": [], # 无输入，直接从参数获取文件路径
            "outputs": [
                {
                    "name": "documents",
                    "type": 'list',
                    "description": '加载的文档列表，每个文档包含页面内容和元数据'
                }
            ],
            "params": [
                {
                    "name": 'file_path',
                    "type": 'string',
                    "required": True,
                    "description": 'PDF文件路径'
                }
            ]
        }

    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理器

        Args：
            inputs: 输入数据（空）
            params: 组件参数数据，包含文件路径

        Returns：
            Dict[str, Any]: 包含文档列表的字典
        """

        # 验证参数
        self.validate_params(params)

        # 获取文件路径
        file_path = params.get('file_path')

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到PDF文件：{file_path}")

        # 使用PyPDFLoader加载文档
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 格式化输出为字典列表
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })

        return {"documents": formatted_docs}