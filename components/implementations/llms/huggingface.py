"""
Hugging Face Transformers模型接口组件
支持本地或远程的huggingface模型
"""

from typing import Any, Dict, Optional
import torch

"""
Pipeline是transformers库中的一个高级抽象,它简化了使用预训练模型的流程
主要参数和功能:
1. task - 指定任务类型:
   - text-generation: 文本生成
   - text-classification: 文本分类 
   - question-answering: 问答
   - summarization: 文本摘要等

2. model - 指定使用的模型:
   - 可以是模型名称如'gpt2'
   - 或本地模型路径
   - 支持自动下载和加载

3. device - 运行设备:
   - 'cpu': CPU设备
   - 'cuda': GPU设备
   - 'cuda:0': 指定GPU设备号

4. tokenizer - 分词器配置:
   - padding: 是否填充
   - truncation: 是否截断
   - max_length: 最大长度

5. 推理参数:
   - batch_size: 批处理大小
   - num_return_sequences: 生成序列数
   - max_new_tokens: 最大新token数
   - temperature: 采样温度
   - top_k/top_p: 采样策略

使用示例:
generator = pipeline(
    task='text-generation',
    model='gpt2',
    device='cuda',
    max_length=50,
    num_return_sequences=1,
    temperature=0.7
)

result = generator("Hello, I'm a language model,")
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# HuggingFacePipeline 是 LangChain 对 transformers pipeline 的封装
# 它让 transformers 模型可以集成到 LangChain 的框架中
# 主要用于:
# 1. 统一接口 - 使其符合LangChain的标准接口
# 2. 链式调用 - 可以和其他LangChain组件组合使用
# 3. 提供更多功能 - 如记忆、提示模板等LangChain特性
from langchain_community.llms import HuggingFacePipeline

from components.base.component import BaseComponent

class HuggingFaceComponent(BaseComponent):
    """
    使用Transformers库访问HuggingFace模型
    
    这是一个可配置的组件类,用户可以通过以下两种方式自定义模型配置:

    1. 初始化配置:
       - 通过配置文件(config.yaml)传入初始参数
       - 这些参数会在组件创建时被加载并应用
    
    2. 运行时动态修改:
       - 通过组件的set_param()方法修改参数
       - 修改仅在当前会话中生效
       - 不会持久化到配置文件或数据库
       - 重启后会恢复到初始配置

    可配置的参数包括:
    - 模型ID (如Mistral、LLAMA等)
    - 运行设备 (CPU/GPU)
    - 生成参数 (温度、最大长度等)
    - 是否信任远程代码等
    """
    
    @classmethod
    def get_metadata(cls) -> Dict:
        return {
            "name": 'HuggingFace',
            "type": 'llm',
            "category": "LLMs",
            "description": 'HuggingFace开源大语言模型',
            "inputs": [
                {
                    "name": 'prompt',
                    "type": 'string',
                    "required": True,
                    "description": '输入的提示文本'
                }
            ],
            "output": [
                {
                    "name": 'text',
                    "type": 'string',
                    "description": '模型生成的文本'
                }
            ],
            "params": [
                {
                    "name": 'model_id',
                    "type": 'string',
                    "required": True, 
                    "description": "HuggingFace模型id，如'mistralai/Mistral-7B-Instruct-v0.1'"
                },
                
                {
                    "name": 'device',
                    "type": 'string',
                    "required": False,
                    "description": "运行设备，可选：CPU 或者 GPU等",
                    "default": 'cpu'
                },
                {
                    "name": "trust_remote_code",
                    "type": 'boolean',
                    "required": False,
                    "default": True, # 是否信任远程代码
                    "description": '是否信任代码'
                },
                {
                    "name": 'temperature',
                    "type": 'number',
                    "required": False,
                    "default": 0.7,
                    "descroption": "生成文本的随机性"
                },
                {
                    "name": 'max_new_tokens',
                    "type": 'number',
                    "required": False, 
                    "default": 512,
                    "description": "最大的生成文本长度"
                },
                {
                    "name": 'load_in_8bit',
                    "type": 'boolean',
                    "required": False,
                    "default": False,
                    "description": "使用8位精度加载模型以节省内存"
                }
            ]
        }
    
    def __init__(self):
        """初始化组件实例"""
        self.llm = None 

    def _initialize_llm(self, params: Dict[str, Any]):
        """初始化LLM实例"""

        if self.llm is None:
            # 从参数中获取配置信息
            model_id = params.get("model_id")
            device = params.get("device", "cpu")
            trust_remote_code = params.get("trust_remote_code", True)
            temperature = float(params.get("tempurature", 0.7))
            max_new_tokens = int(params.get("max_new_tokens", 512))
            load_in_8bit = params.get("load_in_8bit", False)

            # 检查CUDA是否支持
            if device.startswith("cuda") and not torch.cuda.is_available():
                print(f"⚠注意：请求在'{device}'设备上运行，但不支持CUDA，已切换至CPU")
                device = 'cpu'

            # 加载分词器
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code = trust_remote_code,
            )

            # 准备模型加载配置
            model_kwargs = {
                "trust_remote_code": trust_remote_code,
            }

            if load_in_8bit:
                if torch.cuda.is_available():
                    model_kwargs["load_in_8bit"] = True
                    model_kwargs["device_map"] = "auto"
                else:
                    print("⚠注意：8位量化需要CUDA，当前CUDA不可用，请使用默认精度")
            elif device != 'cpu':
                model_kwargs["device_map"] = device

            try:
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    **model_kwargs
                )

                # 创建文本生成器
                text_generation_pipeline = pipeline(
                    "text-generation",
                    model = model,
                    tokenizer = tokenizer,
                    max_new_tokens = max_new_tokens,
                    temperature = temperature,
                    return_full_text = False # 仅返回新生成的文本
                )

                # 创建langchain的HuggingfacePipeline
                # HuggingFacePipeline 来自 langchain_community.llms 模块
                # 它是一个包装器,可以将Hugging Face的pipeline转换为LangChain兼容的LLM
                self.llm = HuggingFacePipeline(pipeline=text_generation_pipeline)
            
            except Exception as e:
                raise RuntimeError(f"加载模型'{model_id}'失败：{str(e)}")

    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理逻辑

        Args：
            inputs: 输入数据，包含提示文本
            params: 组件参数数据，包含模型配置

        Returns:
            Dict[str, Any]: 包含生成文本字典
        """
        # 验证输入和参数
        self.validate_inputs(inputs)
        self.validate_params(params)

        # 获取输入的提示词文本
        prompt = inputs.get("prompt", "")

        # 确保LLM已经初始化
        self._initialize_llm(params)

        # 调用模型生成文本
        response = self.llm(prompt)

        # 返回处理结果
        return {"text": response}
