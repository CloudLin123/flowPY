from typing import Dict, Any
import os
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from components.base.component import BaseComponent, ComponentInput, ComponentOutput, ComponentParam,ParamType

class GeminiComponent(BaseComponent):
    """Google Gemini模型组件"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            'name': 'Gemini',
            'type': 'llm',
            'category': 'language_models',
            'description': 'Google Gemini大语言模型',
            'icon': 'gemini-icon',
            'version': '1.0.0',
            'inputs': [
                ComponentInput('prompt', 'string', '输入提示词').to_dict()
            ],
            'outputs': [
                ComponentOutput('text', 'string', '生成的文本').to_dict()
            ],
            'pramas': [
                ComponentParam(
                    name = 'model',
                    type = ParamType.SELECT,
                    label = '模型',
                    description = '要使用的Gemini模型',
                    required = True,
                    options = [
                        {"label": 'gemini-pro', 'value': 'gemini-pro'},
                        {"label": 'gemini-pro-vision', 'value': 'gemini-pro-vision'},
                        {"label": 'gemini-1.5-pro', 'value': 'gemini-1.5-pro'},
                        {"label": 'gemini-1.5-flash', 'value': 'gemini-1.5-flash'}
                    ],
                    default = 'gemini-pro'
                ).to_dict(),
                ComponentParam(
                    name = 'temperature',
                    type = ParamType.NUMBER,
                    label = '温度',
                    description = '控制生成的随机性（0~1）,俗称人情味或者情感温度',
                    default = 0.75,
                    min = 0,
                    max = 1
                ).to_dict(),
                ComponentParam(
                    name = 'max_output_tokens',
                    type = ParamType.NUMBER,
                    label = '最大的输出tokens长度',
                    description = '生成的最大tokens数量,一个token可能是一个词、一个字或者一个标点',
                    default = 1024,
                    min = 1,
                ).to_dict(),
                ComponentParam(
                    name = 'top_p',
                    type = ParamType.NUMBER,
                    label = 'Top-p采样',
                    description = '控制生成的多样性,0~1,0为最确定,1为最随机',
                    default = 0.95,
                    min = 0,
                    max = 1,
                    advanced = True
                ).to_dict(),
                ComponentParam(
                    name = 'top_k',
                    type = ParamType.NUMBER,
                    label = 'Top-k采样',
                    description = '考虑的候选token数量,越大越随机',
                    default = 40,
                    min = 1,
                    advanced = True
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
            prompt = inputs.get('prompt', '')
            model = params.get('model', 'gemini-pro')
            temperature = float(params.get('temperature', 0.75))
            max_output_tokens = int(params.get('max_output_tokens', 1024))
            # 控制模型只考虑累积概率达到 p 值的词汇，值越低月保守肯定，反之则多样性更高
            top_p = float(params.get('top_p', 0.95)) 
            # 限制模型只考虑概率最高的 k 个词汇
            # 通常同时使用 top_p 和 top_k，先应用 top_k 过滤，再应用 top_p 进一步筛选，实现更精细的控制。
            top_k = int(params.get('top_k', 40))
            api_key = params.get('api_key') or os.environ.get('GEMINI_API_KEY')

            if not api_key:
                return {'error': '未提供Gemini API密钥,请在参数中指定或设置GEMINI_API_KEY环境变量'}
            
            # 创建Langchain模型
            
            
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_tokens=max_output_tokens,
                top_p=top_p,
                top_k=top_k,
                api_key=SecretStr(api_key),  # 将 api_key 转换为 SecretStr 类型
            )
            
            # 调用模型
            result = llm.invoke(prompt)

            # 提取文本内容
            text_content = result.content

            return {'text': text_content}
        except Exception as e:
            return {"error": f'Gemini API错误: {str(e)}'}