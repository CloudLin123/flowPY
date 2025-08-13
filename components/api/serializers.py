"""
组件API序列化器
用于将组件转换为API响应
"""

from rest_framework import serializers
from components.models import Component

class ComponentSerializer(serializers.ModelSerializer):
    """
    组件序列化器
    将组件数据转为前端可用的json格式
    """
    class Meta:
        model = Component
        fields = ['id', 'namme', 'type', 'description', 'input_params', 'output_params']
    
    def to_representation(self, instance):
        """
        增强组件表示
        添加输入/输出参数详细信息等
        """
        data = super().to_representation(instance)
        # 添加更详细的参数信息
        try:
            # 获取组件类的元数据
            module_path = f"components.implementations.{instance.module_path}"
            class_name = instance.class_name

            # 动态导入组件类
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)

            # 获取输入/输出参数定义
            if hasattr(component_class, 'get_metadata'):
                metadata = component_class.get_metadata()
                data['input_schema'] = metadata.get('input_schema', {})
                data['output_schema'] = metadata.get('output_schema', {})
        
        except Exception as e:
            # 如果获取元数据失败，记录错误但不中断序列化
            data['error'] = f'无法加载参数架构： {str(e)}'

        return data