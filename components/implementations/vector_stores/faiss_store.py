"""
FAISS向量存储组件(高效,持久化只是附加功能)
基于Facebook AI Similarity Search(FAISS)的向量存储实现

FAISS是一个高效的向量相似度搜索库,主要功能:
1. 将文本转换为向量并建立索引
2. 快速查找相似向量

工作原理:
1. 使用embedding模型将文本转换为向量(数值数组)
   - embedding模型能将语义相近的文本转换为距离相近的向量
   - 例如"我喜欢猫"和"我爱小猫"会得到相似的向量
2. FAISS对这些向量建立索引
   - 使用特殊的数据结构来组织向量
   - 支持快速的最近邻搜索
3. 查询时:
   - 先用相同的embedding模型将查询文本转为向量
   - 然后用FAISS找到最相似的向量
   - 返回对应的原始文本
"""

"""
FAISS向量存储组件的上下游组件交互说明:

上游组件:
1. 文档加载器(如PDFLoader):
   - 负责读取原始文档并提取文本内容
   - 输出格式为包含page_content和metadata的文档列表
   - 例如从PDF中提取的每一页都是一个文档对象

2. 文本分割器(如RecursiveTextSplitter):
   - 将长文本分割成适合向量化的小段
   - 保持文档的格式(page_content和metadata)
   - 控制文本块的大小和重叠度

FAISS向量存储的处理流程:
1. 接收上游组件的文档列表
2. 使用embedding模型将文本转换为向量
3. 构建FAISS索引进行存储
4. 提供向量检索接口

下游应用:
1. 相似度搜索:
   - 接收查询文本
   - 返回最相似的文档片段
2. 问答系统:
   - 根据问题检索相关上下文
   - 结合LLM生成答案
3. 文本推荐:
   - 基于文本相似度推荐相关内容

数据流转格式:
1. 输入文档格式:
   {
     "page_content": "文本内容",
     "metadata": {"source": "来源", "page": "页码"}
   }
2. 查询结果格式:
   [
     {
       "page_content": "匹配的文本片段",
       "metadata": {"相关元数据"}
     }
   ]

这种组件化设计让FAISS可以灵活地集成到不同的应用场景中。
"""

from typing import Any, Dict, List, Optional
import os
import tempfile
# 这里可以直接导入FAISS是因为langchain_community已经将faiss作为依赖项打包在内
# 当我们安装langchain_community时,它会自动安装faiss-cpu作为依赖
# 但如果要直接使用faiss库的底层功能,则需要单独安装:
# pip install faiss-cpu  # CPU版本
# pip install faiss-gpu  # GPU版本(需要CUDA支持)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from components.base.component import BaseComponent

class FAISSVectorStoreComponent(BaseComponent):
    """FAISS向量存储组件，用于创建和查询向量数据库"""

    @classmethod
    def get_metadata(cls) -> Dict:
        return {
            "name": "FAISSVectorStore",
            "type": "vector_store",
            "category": "Vector Stores",
            "description": "使用FAISS创建高效的向量存储，支持相似度搜索",
            "inputs": [
                {
                    "name": "documents",
                    "type": "list",
                    "required": True,
                    "description": "要索引的文档列表，每个文档包含page_content和metadata"
                },
                {
                    "name": "query",
                    "type": "str",
                    "required": False,
                    "description": "查询文本(可选，是否要执行搜索)"
                }
            ],
            "outputs": [
                {
                    "name": "vector_store",
                    "type": "object",
                    "description": "创建FAISS向量存储的对象(供后续组件使用)"
                },
                {
                    "name": "results",
                    "type": "list",
                    "description": "查询结果文档列表(如果提供了查询)"
                }
            ],
            "params": [
                {
                    "name": "embedding_model",
                    "type": "string",
                    "required": False,
                    "default": "sentence-transformers/all-MiniLM-L6-v2", # 默认使用MiniLM词嵌入模型
                    "description": "你要用的生成嵌入模型名称"
                },
                {
                    "name": "save_path",
                    "type": "string",
                    "required": False,
                    "description": "向量存储的保存途径(可选)"
                },
                {
                    "name": "load_path",
                    "type": "string",
                    "required": False,
                    "description": "加载现有的向量存储路径(可选)"
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
        """初始化组件实例"""
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
            inputs: 输入数据，包含文档列表和可选的查询
            params: 参数数据，包含向量存储配置

        Returns：
            Dict[str, Any]: 包含向量存储（和/或者）查询结果的字典
        """

        # 验证输入和参数
        self.validate_inputs(inputs)
        self.validate_params(params)

        # 获取嵌入模型名称
        embedding_model = params.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

        # 初始化嵌入模型
        self._initiallize_embeddings(embedding_model)

        # 检查是否需要加载现有向量存储
        load_path = params.get("load_path")
        if load_path and os.path.exists(load_path):
            self.vector_store = FAISS.load_local(load_path, self.embeddings)
        else:
            # 获取输入文档
            documents = inputs.get('documents', [])

            # 转换文档格式为langchain的Document对象
            from langchain_core.documents import Document
            docs = []
            for doc in documents:
                if isinstance(doc,dict) and "page_content" in doc:
                    docs.append(Document(
                        page_content = doc["page_content"],
                        metadata = doc.get("metadata", {})
                    ))
            
            # 创建向量存储
            if docs:
                self.vector_store = FAISS.from_documents(docs, self.embeddings)

                # 保存向量存储（如果指定了保存路径）
                save_path = params.get("seve_path")
                if save_path:
                    os.makedirs(os.path.dirname(save_path), exist_ok = True)
                    self.vector_store.save_local(save_path)
        
        result = {"vector_store": self.vector_store}

        # 执行查询(如果提供了查询文本)
        query = inputs.get('query')
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