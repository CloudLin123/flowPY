from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import Credential
from .serializers import CredentialSerializer
import json
import requests

class CredentialViewSet(viewsets.ModelViewSet):
    """
    凭证管理API端点
    提供凭证的CRUD操作以及验证功能
    """
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        验证凭证是否有效

        基于凭证类型执行不同的验证逻辑
        - openai: 尝试调用OpenAI API
        - huggingface: 验证令牌是否可以访问HF API
        - 其他类型：实现特定的验证逻辑
        """
        credential = self.get_object() # 获取当前凭证对象
        credential_type = credential.credential_type # 获取凭证类型
        value = json.loads(credential.value) # 解析凭证值

        # 根据凭证类型实现不同的验证逻辑
        if credential_type == 'openai':
            api_key = value.get('api_key')
            if not api_key:
                return Response(
                    {'valid': False, 'error': '缺少API密钥'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                # 尝试调用OpenAI API的模型列表接口
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    'content-type': 'application/json'
                }
                response = requests.get('https://api.openai.com/v1/models', headers=headers)

                if response.status_code == 200:
                    return Response({"valid": True})
                else:
                    return Response(
                        {'valid':False, 'error': f"API响应: {response.status_code}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Exception as e:
                return Response(
                    {"valid": False,"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif credential_type == "huggingface":
            token = value.get('token')
            if not token:
                return Response(
                    {"valid": False, "error": "缺少huggingface令牌"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # 验证Huggingface令牌
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get("https://huggingface.co/api/whoami", headers=headers)

                if response.status_code == 200:
                    return Response({"valid": True})
                else:
                    return Response(
                        {"valid": False, "error": '无效令牌，请检查api'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Exception as e:
                return Response(
                    {"valid": False, "error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # 添加其他凭证类型的验证逻辑
        # 例如：本地模型、向量数据库

        # 如果是未知凭证类型，默认有效（或者直接提示用户，让用户注意）
        return Response({"valid": True, "warning": "此凭证无法验证其有效性，请您注意"})
