from typing import Dict, Any
from sqlalchemy.sql.functions import user
from typing_extensions import Required
from langchain.memory import ConversationBufferMemory as LCConversationBufferMemory
from components.base.component import *

class ConversationBufferMemoryComponent(BaseComponent):
    """Langchain的对话缓冲记忆组件封装"""

    @classmethod
    def get_metadata(cls) -> Dict:
        """获取组件元数据"""
        return {
            'name': 'ConversationBufferMemory',
            'type': 'memory',
            'category': 'memory',
            'description': '存储对话历史的简单内存组件',
            'icon': '🔄',
            'version': '1.0.0',
            'inputs': [
                ComponentInput('input', 'string', '用户输入', required = True).to_dict(),
                ComponentInput('output', 'string', '系统回复', required = True).to_dict()
            ],
            'outputs': [
                ComponentOutput('memory', 'string', '记忆对象').to_dict(),
                ComponentOutput('history', 'string', '对话历史记录').to_dict()
            ],
            'params': [
                ComponentParam(
                    name = 'return_messages',
                    type = ParamType.BOOLEAN,
                    label = '返回消息对象',
                    description = '是否返回消息对象而不是字符串',
                    default = False
                ).to_dict(),
                ComponentParam(
                    name = 'input_key',
                    type = ParamType.STRING,
                    label = '输入键名',
                    description = '输入消息的键名',
                    default = 'input'
                ).to_dict()
            ]
        }

async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """执行组件处理逻辑"""

    try:
        # 验证输入和参数
        self.validate_inputs(inputs)
        params = self.validate_params(params)

        # 获取参数
        return_messages = params.get('return_messages', False)
        input_key = params.get('input_key', 'input')
        output_key = params.get('output_key', 'output')

        # 获取输入
        user_input = inputs.get('input', '')
        system_output = inputs.get('output', '')

        # 创建记忆组件
        memory = LCConversationBufferMemory(
            return_messages = return_messages,
            input_key = input_key,
            output_key = output_key
        )

        # 如果提供了系统输出，则保存对话
        if system_output:
            memory.save_context({input_key: user_input}, {output_key: system_output})
        
        if return_messages:
            history = memory.load_memory_variables({})
            history_text = str(history)
        else:
            history_text = memory.buffer

        return {
            'memory': memory,
            'history': history_text
        }
    except Exception as e:
        return {'error': f"记忆组件执行失败: {str(e)}"}

