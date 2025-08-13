"""
组件API视图
提供获取可用组件的接口
"""
from http.client import responses
from importlib import metadata
from unicodedata import category
from urllib.request import HTTPPasswordMgrWithDefaultRealm
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from components.models import Component
from .serializers import ComponentSerializer

from .permissions import IsAdminOrReadOnly, HasComponentAccess

class ComponentViewSet(viewsets.ModelViewSet):
    """
    组件API端点
    仅提供只读操作，因为组建的定义一般不通过API修改
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'type', 'description', 'category']

    def get_queryset(self):
        """
        允许通过查询参数过滤组件
        例如 ?type=llm ，即只返回LLM类型组件
        """
        queryset = super().get_queryset()

        # 根据类型过滤
        component_type = self.request.query_params.get('type')
        if component_type:
            queryset = queryset.filter(type=component_type)

        # 根据分类的类别过滤
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    @action(detail=False, methods=['get'])
    def types(self, request):
        """
        返回所有可用的组件类型列表
        用于前端构建组件选择器
        """
        types = Component.objects.values_list('type', flat=True).distinct()
        return Response(sorted(list(types)))

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        返回所有可用的组件类别列表
        用于前端构建组件选择器
        """
        categories = Component.objects.values_list('category', flat=True).distinct()
        return Response(sorted(list(categories)))
    
    @action(detail=False, methods=['get'])
    def schema(self, request, pk=None):
        """
        返回单个组件的详细参数模式
        包含输入输出等完整描述
        """
        component = self.get_object()
        
        try:
            # 动态导入组件类
            module_path = f"components.implementations.{component.module_path}"
            class_name = component.class_name

            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)

            # 获取详细的参数架构
            if hassttr(component_class, 'get_metadata'):
                metadata = component_class.get_metadata()
                return Response({
                    'input_schema': metadata.get('input_schema', {}),
                    'output_schema': metadata.get('output_schema', {}),
                    'examples': metadata.get('examples', [])
                })

            else:
                return Response(
                    {"error": '组件类为实现get_metadate方法'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {"error": f'获取组件架构失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def register(self, request):
        """
        注册新组建或者更新现有组件
        用于动态注册新开发的组件到系统里面
        """
        # 此功能需要管理员权限
        if not request.user.is_staff:
            return Response(
                {"error": "需要管理员权限，闲杂人等滚蛋"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取请求数据
        name = request.data.get('name')
        component_type = request.data.get('type')
        module_path = request.data.get('module_path')
        class_name = request.data.get('class_name')

        if not all([name,component_type, module_path, class_name]):
            return Response(
                {"error": '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 尝试导入组件以验证其有效性
        try:
            full_path = f'components.implementations.{module_path}'
            module = __import__(full_path, fromlist=[class_name])
            component_class = getattr(module, class_name)

            # 检查组件是否实现了必要的方法
            if not hasattr(component_class, 'get_metadata'):
                return Response(
                    {"error": f'组件类{class_name}缺少get_metadata方法'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 从组件获取元数据
            metadata = component_class.get_metadata()

            # 创建或更新组件记录
            component, created = Component.objects.update_or_create(
                name = name,
                defaults = {
                    'type': component_type,
                    'module_path': module_path,
                    'class_name': class_name,
                    'description': metadata.get('description', ''),
                    'category': metadata.get('category', '未分类')
                }
            )

            serializer = self.get_serializer(component)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        except ImportError:
            return Response(
                {'error': f'无法导入模块：{module_path}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except AttributeError:
            return Response(
                {'error': f'无法在模块中找到类：{class_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': f'组件注册失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )