from typing import Any, Dict

from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from components.base.component import *
import os

class DeepSeekComponent(BaseComponent):
    """Ollama DeepSeek模型组件"""
    
    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            "name": "DeepSeek",
            "type": "llm",
            "category": "language_models",
            "description": "通过Ollama访问的DeepSeek-R1-1.5B模型",
            "icon": "deepseek-icon",
            "version": "1.0.0",
            "inputs": [
                ComponentInput("prompt", "string", "输入提示词").to_dict()
            ],
            "outputs": [
                ComponentOutput('text', 'string', '生成的文本').to_dict()
            ],
            "params": [
                ComponentParam(
                    name="model",
                    type=ParamType.SELECT,
                    label="模型",
                    description="要使用的DeepSeek模型",
                    required=True,
                    options=[
                        {"label": "deepseek-r1-1.5b", "value": "deepseek-r1-1.5b"},
                        {"label": "deepseek-coder", "value": "deepseek-coder"}
                    ],
                    default="deepseek-r1-1.5b"
                ).to_dict(),
                ComponentParam(
                    name="temperature",
                    type=ParamType.NUMBER,
                    label="温度",
                    description="控制生成的随机性 (0-2)",
                    default=0.7,
                    min=0,
                    max=2
                ).to_dict(),
                ComponentParam(
                    name="max_output_tokens",
                    type=ParamType.NUMBER,
                    label="最大输出令牌数",
                    description="生成的最大令牌数量",
                    default=1024,
                    min=1
                ).to_dict(),
                ComponentParam(
                    name="top_p",
                    type=ParamType.NUMBER,
                    label="Top P",
                    description="核采样参数",
                    default=0.9,
                    min=0,
                    max=1,
                    advanced=True
                ).to_dict(),
                ComponentParam(
                    name="top_k",
                    type=ParamType.NUMBER,
                    label="Top K",
                    description="考虑的候选令牌数",
                    default=40,
                    min=1,
                    advanced=True
                ).to_dict(),
                ComponentParam(
                    name="ollama_base_url",
                    type=ParamType.STRING,
                    label="Ollama服务URL",
                    description="本地Ollama服务的基础URL（可选，默认使用环境变量）",
                    default=os.environ.get('DEEPSEEK_API_BASE', 'http://localhost:11434'),
                    required=False
                ).to_dict(),
                ComponentParam(
                    name="system_prompt",
                    type=ParamType.STRING,
                    label="系统提示词",
                    description="系统提示词，用于指导模型行为",
                    default="你是一个有用的AI助手",
                    multiline=True,
                    required=False
                ).to_dict(),
            ]
        }
    
    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """执行组件处理逻辑"""
        try:
            # 验证输入和参数
            self.validate_inputs(inputs)
            params = self.validate_params(params)
            
            # 获取参数
            prompt = inputs.get("prompt", "")
            model = params.get("model", "deepseek-r1-1.5b")
            temperature = float(params.get("temperature", 0.7))
            max_output_tokens = int(params.get("max_output_tokens", 1024))
            top_p = float(params.get("top_p", 0.9))
            top_k = int(params.get("top_k", 40))
            ollama_base_url = params.get("ollama_base_url") or os.environ.get('DEEPSEEK_API_BASE', 'http://localhost:11434')
            system_prompt = params.get("system_prompt", "")
            
            # 创建LangChain模型
            """
            tips:
                ChatOllama 和 OllamaLLM 有以下关键区别：
                    1、使用场景不同：
                        ChatOllama：设计用于对话场景，支持消息历史记录和多轮对话
                        OllamaLLM：设计用于单轮文本补全，不维护对话历史
                    2、输入格式不同：
                        ChatOllama：接受 BaseMessage 对象列表作为输入（如SystemMessage、HumanMessage等）
                        OllamaLLM：接受单个字符串作为输入
            """
            # 使用ChatOllama并正确设置系统提示词
            if system_prompt:
                # 创建消息列表，包含系统消息和用户消息
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                
                llm = ChatOllama(
                    model=model,
                    base_url=ollama_base_url,
                    temperature=temperature,
                    num_predict=max_output_tokens,  # Ollama使用num_predict而不是max_output_tokens
                    top_p=top_p,
                    top_k=top_k
                )
                
                # 调用模型
                result = llm.invoke(messages)
                
                return {"text": result.content}
            else:
                # 如果没有系统提示词，可以直接使用OllamaLLM
                llm = OllamaLLM(
                    model=model,
                    base_url=ollama_base_url,
                    temperature=temperature,
                    num_predict=max_output_tokens,
                    top_p=top_p,
                    top_k=top_k
                )
                
                # 调用模型
                result = llm.invoke(prompt)
                
                return {"text": result}
        except Exception as e:
            return {"error": f"Ollama DeepSeek错误: {str(e)}"}