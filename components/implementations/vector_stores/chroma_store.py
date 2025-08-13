"""
Chroma向量存储组件
基于Chroma数据库的向量存储实现
Chroma设计为持久化优先的数据库,默认就会写入磁盘,适合长期存储和增量更新的场景
"""


from typing import Any, Dict, List, Optional
import os
import tempfile
from unittest import result
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from components.base.component import BaseComponent

class ChromaVectorStoreComponent(BaseComponent):
    """Chroma向量存储组件，用于创始和查询持久化向量数据库"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            "name": "chromavectorstore",
            "type": "vector_store",
            "category": "Vector Store",
            "description": "使用Chroma创建持久化向量存储，支持相似度搜索",
            "inputs": [
                {
                    "name": 'documents',
                    "type": "list",
                    "required": False,
                    "description": "要索引的文档列表，每个文档包含page_content和metadata"
                },
                {
                    "name": "query",
                    "type": "string",
                    "required": False,
                    "description": "查询文本（如果要执行搜索）"
                }
            ],
            "outputs": [
                {
                    "name": "vector_store",
                    "type": "object",
                    "description": "创建的向量存储对像（供后续组件使用）"
                },
                {
                    "name": "results",
                    "type": "list",
                    "description": "查询结果文档列表（如果提供了查询）"
                }
            ],
            "params": [
                {
                    "name": "embedding_model",
                    "type": "string",
                    "required": False,
                    "default": "sentence-transformers/all-MiniLM-L6-v2",
                    "description": "用于生成嵌入的模型名称"
                },
                {
                    "name": "persist_directory",
                    "type": "string",
                    "required": True,
                    "description": "Chroma数据库的持久化目录路径"
                },
                {
                    "name": "collection_name",
                    "type": "string",
                    "required": False,
                    "default": "langchain_chroma",
                    "description": "Chroma集合名称"
                },
                {
                    "name": "top_k",
                    "type": "number",
                    "required": False,
                    "default": 5,
                    "description": "查询时返回的最相似的文档数量"
                }
            ]
        }

    def __init__(self):
        """
        初始化组件实例

        这是什么意思？
        该方法是Python类的构造函数（初始化方法），当你创建该类的对象时会自动调用。
        这里初始化了两个实例变量：
        - self.embeddings：用于存储嵌入模型对象，初始为None，后续会根据参数加载实际的嵌入模型。
        - self.vector_store：用于存储Chroma向量数据库对象，初始为None，后续会根据输入文档或持久化目录加载或创建实际的向量存储。
        """
        self.embeddings = None
        self.vector_store = None

    def _initialize_embeddings(self, model_name):
        """初始化嵌入模型"""
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name = model_name,
                cache_folder = os.path.join(tempfile.gettempdir(), "hf_models")
            )
    
    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理逻辑

        Args：
            inputs: 输入数据，包含可选的文档列表和查询
            params：参数数据，包含向量存储配置
        
        Returns:
            Dict[str, Any]: 包含向量存储（和/或）查询结果的字典
        """

        # 验证参数
        self.validate_params(params)

        # 获取参数
        embedding_model = params.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        persist_directory = params.get("persist_directory")
        collection_name = params.get("collection_name", "langchain_chroma")

        # 确保持久化目录存储表
        os.makedirs(persist_directory, exist_ok = True)

        # 初始化嵌入模型
        self._initialize_embeddings(embedding_model)

        # 获取输入文档
        documents = inputs.get("documents", [])

        # 准备langchain文档对象
        from langchain_core.documents import Document
        docs = []
        for doc in documents:
            if isinstance(doc, dict) and "page_content" in doc:
                docs.append(Document(
                    page_content=doc["page_content"],
                    metadata=doc.get("metadata", {})
                ))

        # 创建或加载向量存储
        if docs:
            # 有新文档，创建或更新
            self.vector_store = Chroma.from_documents(
                documents = docs,
                embedding = self.embeddings,
                persist_directory = persist_directory,
                collection_name = collection_name
            )
        else:
            # 没有新文档，加载现有的
            self.vector_store = Chroma(
                persist_directory = persist_directory,
                embedding_function = self.embeddings,
                collection_name = collection_name
            )

        # 持久化存储
        self.vector_store.persist()

        result = {"vector_store": self.vector_store}

        # 执行查询(如果提供了查询文本)
        query = inputs.get("query")
        if query and self.vector_store:
            top_k = int(params.get("top_k", 5))
            search_results = self.vector_store.similarity_search(query, k = top_k)

            # 格式化查询结果
            formatted_results = []
            for doc in search_results:
                formatted_results.append({
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                })

            result["results"] = formatted_results
    
        return result