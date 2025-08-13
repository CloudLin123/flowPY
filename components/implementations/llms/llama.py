"""
Llama系列模型接口组件
支持通过llama.cpp或者llama-cpp-python库连接本地部署的Llama系列模型
"""

from typing import Dict, Any, List, Optional
from langchain_community.llms.llamacpp import LlamaCpp
from components.base.component import BaseComponent

class LlamaCppComponent(BaseComponent):
    """使用llama-cpp-python库访问本地部署的Llama模型"""

    @classmethod
    def get_metadata(cls) -> Dict:
        return {
            "name": "LlamaCpp",
            "type": "llm", # 组件类型
            "category": "LLMs", # 组件分类
            "description": "本地Llama系列大语言模型(使用llama-cpp-python)",
            "inputs":[
                {
                    "name": 'prompt',
                    "type": 'string',
                    "required": True,
                    "description": "输入的提示文本——用户的问题",
                }
            ],
            "outputs":[
                {
                    "name": 'text',
                    "type": 'string',
                    "description": "模型生成的文本——回答",
                }
            ],
            "params": [
                {
                    "name": 'model_path',
                    "type": 'string',
                    "required": True,
                    "description": 'Llama模型文件路径(.gguf格式)'
                },
                {
                    "name": 'n_ctx',
                    "type": 'number',
                    "required": False,
                    "default": 2048,
                    "description": '上下文长度大小'
                },
                {
                    "name": 'temperature',
                    "type": 'number',
                    "required": False,
                    "deffault": 0.7,
                    "description": '生成文本的随机性，或者说是人情味'
                },
                {
                    "name": 'n_gpu_layers',
                    "type": 'number',
                    "required": False,
                    "default": 0,
                    "description": '在GPU上运行的层数,0表示只使用cpu'
                },
                {
                    "name": 'max_tokens',
                    "type": 'number',
                    "required": False,
                    "default": 1024,
                    "description": '生成文本的最大长度'
                }
            ]
        }
    
    def __init__(self):
        """初始化组件实例"""
        self.llm = None
    
    def initialize(self, params: Dict[str, Any]):
        """初始化LLM实例"""
        if self.llm is None:
            # 从参数中获取配置信息
            model_path = params.get('model_path')
            n_ctx = int(params.get('n_ctx', 2048))
            temperature = float(params.get('temperature', 0.7))
            n_gpu_layers = int(params.get('n_gpu_layers', 0))
            max_tokens = int(params.get('max_tokens', 256))

            # 创建LlamaCpp实例
            self.llm = LlamaCpp(
                model_path=model_path,
                n_ctx=n_ctx,
                temperature=temperature,
                n_gpu_layers=n_gpu_layers,
                max_tokens=max_tokens,
                verbose=False # 避免过多日志输出
            )
    
    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理逻辑

        Args:
            inputs: 输入参数，包含提示词文本——用户的问题
            params: 组件参数，包含模型配置

        Returns:
            Dict[str, Any]: 输出结果，包含生成文本的字典——模型的回答
        """

        # 验证输入和参数
        self.validate_inputs(inputs)
        self.validate_params(params)

        # 获取输入的提示词文本——用户的问题
        prompt = inputs.get("prompt", "")

        # 确保LLM已经初始化
        self._initialize_llm(params)

        # 调用模型生成文本
        response = self.llm(prompt)

        # 返回处理结果
        return {"text": response}