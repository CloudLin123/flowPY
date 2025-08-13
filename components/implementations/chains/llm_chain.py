# 实现一个基础链组件
from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from components.base.component import *

class LLMChainComponent(BaseComponent):
    """Langchain的LLMChain组件的封装"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件的元数据"""
        return {
            'name': 'LLMChain',
            'type': 'chain',
            'category': 'chains',
            'description': '将大语言模型与提示模板连接的基础链',
            'icon': '🔗',
            'version': '1.0.0',
            'inputs': [
                ComponentInput('llm', 'object', 'LLM组件', required=True).to_dict(),
                ComponentInput('prompt_template', 'string', '提示模板', 
                               description='使用{input_variables}作为变量，例如："回答关于{topic}的问题"',
                               required=True).to_dict(),
                ComponentInput('input_variables', 'object', '输入变量',
                               description='提示模板中使用的变量值',
                               required=True).to_dict()
            ],
            'outputs': [
                ComponentOutput('text', 'string', '链的输出文本').to_dict()
            ],
            'params': [
                ComponentParam(
                    name = 'verbose',
                    type = ParamType.BOOLEAN,
                    label = '详细输出',
                    description = '是否打印链的执行过程',
                    default = False 
                ).to_dict()
            ]
        }

    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """执行组件处理逻辑"""
        try:
            # 验证输入和参数
            self.validate_inputs(inputs)
            params = self.validate_params(params)

            # 获取输入
            llm = inputs.get('llm')
            prompt_template = inputs.get('prompt_template')
            input_variables = inputs.get('input_variables')
            verbose = params.get('verbose', False)

            # 验证输入类型
            if not isinstance(input_variables, dict):
                return {'error': 'input_variables必须是一个字典'}
            
            # 创建提示词模板
            # 从模板文本提取变量名字
            import re
            if prompt_template is None:
                return {'error': '提示模板不能为空'}
                
            variables = re.findall(r'\{([^}]+)\}', prompt_template)

            prompt = PromptTemplate(
                template = prompt_template,
                input_variables = variables
            )

            # 创建链
            chain = LLMChain(
                llm = llm,
                prompt = prompt,
                verbose = verbose
            )

            # 执行链
            result = await chain.arun(**input_variables)

            return {'text': result}

        except Exception as e:
            return {'error': f'LLMChain执行报错：{str(e)}'}