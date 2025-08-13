from rest_framework import serializers
from core.models import Credential

class CredentialSerializer(serializers.ModelSerializer):
    """
    凭证序列化器，注意敏感信息的处理
    """
    class Meta:
        model = Credential
        fields = ['id', 'name', 'credential_type', 'created_at']
        read_only_fields = ['created_at']

    # 创建凭证时接收完整的信息
    def create(self, validated_data):
        """
        validated_data是经过序列化器验证后的数据字典，包含了前端提交的所有有效字段值
        这个方法使用这些验证过的数据创建一个新的Credential对象
        **validated_data是Python的解包语法，将字典中的键值对作为参数传递给create方法
        """
        return Credential.objects.create(**validated_data)

    # 获取凭证时隐藏敏感数据
    def to_representation(self, instance):
        """
        当API返回凭证数据时，这个方法会被调用来转换模型实例为可序列化的字典
        """
        ret = super().to_representation(instance)
        # 添加掩码化的值字段，用于表示存在敏感数据但不显示实际内容
        # 可以改成其他字符串，如"[敏感信息已隐藏]"或"HIDDEN_VALUE"等
        # 这里的作用是在API响应中提供一个占位符，告知用户有敏感值但不展示实际内容
        ret['value_masked'] = "[敏感信息已隐藏]"
        return ret