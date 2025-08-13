"""
工作流API视图
提供工作流的CRUD操作和执行功能

系统功能角色:
- 作为前端与数据库之间的桥梁
- 处理工作流的创建、查询、更新、删除
- 实现工作流执行逻辑，协调组件之间的数据流动
"""

from rest_framework import viewsets, status  # 导入DRF的viewsets，用于快速实现CRUD接口
from rest_framework.decorators import action, schema
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from workflows.models import Workflow, Edge  # 导入工作流、边的模型
from components.models import Node # 导入节点模型
from .serializers import WorkflowSerializer, NodeSerializer, EdgeSerializer  # 导入对应的序列化器

# 工作流执行引擎实现所需的库
import networkx as nx
from components.models import Component
from core.models import Credential
import json
import asyncio


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    工作流管理API
    提供工作流的创建、读取、更新、删除功能
    """
    queryset = Workflow.objects.all()  # 定义默认的查询集，获取所有Workflow对象
    serializer_class = WorkflowSerializer  # 指定序列化器，用于数据的序列化和反序列化

    @swagger_auto_schema(
        operation_description='执行指定的工作流',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'inputs': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='工作流输入参数'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='工作流执行成功',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'output': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "无效的工作流或输入参数",
            500: "工作流执行错误"
        }
    )
    @action(detail=True, methods=['post'])
    async def execute(self, request, pk=None):
        """
        执行工作流的API端点
        全项目的核心中的核心

        流程：
        1、加载工作流及其节点、边
        2、构建有向图并进行拓扑排序
        3、按顺序执行每个节点
        4、追踪中间结果并且返回最终的输出
        """
        workflow = self.get_object()
        # 获取输入参数
        input_data = request.data.get('inputs', [])
        
        # 加载工作流的节点和边
        nodes = workflow.nodes.all()
        edges = workflow.edges.all()

        # 构建工作流执行图
        G = nx.DiGraph()

        # 添加所有节点
        node_map = {} # 节点ID到对象的映射
        for node in nodes:
            G.add_node(node.node_id)
            node_map[node.node_id] = node
        
        # 添加所有边
        for edge in edges:
            G.add_edge(edge.source_node, edge.target_node)

        #TODO 确保图是无环的(如果有if或者while组件怎么办)
        if not nx.is_directed_acyclic_graph(G):
            return Response(
                {"error": '工作流有死循环，无法执行'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取拓扑排序（执行顺序）
        try:
            execution_order = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            return Response(
                {"error": '工作流结构无效，无法确定执行顺序'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 存储每个节点的执行结果
        results = {}

        # 添加工作流的输入到结果里面
        if 'start' in input_data:
            results['start'] = input_data['start']

        # 按顺序执行每个节点
        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue

            # 获取组件类型和参数
            component_type = node.componennt_type
            component_id = node.component_id
            node_params = json.loads(node.data) if node.data else {}

            try:
                # 查找组件定义
                component = Component.objects.get(name=component_id)

                # 准备输入数据
                node_inputs = {}

                # 查找所有指向当前节点的边
                incoming_edges = [e for e in edges if e.target_node == node_id]

                for edge in incoming_edges:
                    source_node = edge.source_node
                    source_output = edge.source_output or 'output' # 默认输出键，而不是值
                    target_input = edge.target_input or 'input' # 默认输入键，而不是值

                    if source_node in results:
                        # 将上一节点的输出连接到当前节点的输入
                        source_data = results[source_node]
                        if source_output in source_data:
                            node_inputs[target_input] = source_data[source_output]

                # 处理凭证需求
                if 'credential' in node_params:
                    credential_id = node_params.pop('credentialId')
                    try:
                        credential = Credential.objects.get(id=credential_id)
                        # 添加凭证值到参数
                        node_params['credential'] = json.loads(credential.value)
                    except Credential.DoesNotExist:
                        return Response(
                            {"error": f'节点 {node_id} 需要的凭证ID{credential_id} 不存在'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # 导入并且初始化组件类
                component_module = __import__(
                    f"components.implementations.{component.module_path}",
                    fromlist = [component.class_name]
                )

                component_class = getattr(component_module, component.class_name)
                component_instance = component_class()

                # 执行组件
                result = await component_instance.execute(node_inputs, node_params)

                # 存储结果
                results[node_id] = result
            
            except Component.DoesNotExist:
                return Response(
                    {"error": f'找不到组件：{component_id}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            except Exception as e:
                return Response(
                    {'error': f"节点 {node_id} 执行失败：{str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # 找到没有出边的节点作为输出
        output_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]

        # 收集所有输出节点的结果
        outputs = {}
        for node_id in output_nodes:
            if node_id in results:
                outputs[node_id] = results[node_id]

        # # 模拟执行结果
        # result = {'status': 'success', 'output': {"result": "工作流执行结果示例"}}
        return Response({
            "status": 'success',
            "output": outputs
        })


class NodeViewSet(viewsets.ModelViewSet):
    """
    节点管理API端点
    """
    queryset = Node.objects.all()  # 定义默认的查询集，获取所有Node对象
    serializer_class = NodeSerializer  # 指定序列化器，用于节点数据的序列化和反序列化

    def get_queryset(self):
        """允许通过workflow参数过滤"""
        queryset = super().get_queryset()  # 调用父类方法，获取基础的查询集
        # API视图已定义，需要在urls.py中配置正确路由，然后访问
        workflow_id = self.request.query_params.get('workflow')  # 从请求参数中获取workflow参数
        if workflow_id:  # 如果有workflow参数
            queryset = queryset.filter(workflow_id=workflow_id)  # 根据workflow_id过滤节点
        return queryset  # 返回最终的查询集（可能被过滤）

class EdgeViewSet(viewsets.ModelViewSet):
    """
    边管理API端点
    """
    queryset = Edge.objects.all()  # 定义默认的查询集，获取所有Edge对象
    serializer_class = EdgeSerializer  # 指定序列化器，用于边数据的序列化和反序列化

    def get_queryset(self):
        """允许通过workflow参数过滤"""
        queryset = super().get_queryset()  # 调用父类方法，获取基础的查询集
        workflow_id = self.request.query_params.get('workflow')  # 从请求参数中获取workflow参数
        if workflow_id:  # 如果有workflow参数
            queryset = queryset.filter(workflow_id=workflow_id)  # 根据workflow_id过滤边
        return queryset  # 返回最终的查询集（可能被过滤）

    # 说明：
    # 1. 为什么return的结果都是queryset？
    #    因为Django REST framework的ModelViewSet要求get_queryset方法返回一个QuerySet对象，作为后续数据查询、过滤、分页等操作的基础。
    #    无论是Workflow、Node还是Edge，最终都需要返回一个QuerySet，供视图集处理请求时使用。
    # 2. 三个类的实例化和命名一致会不会出故障？
    #    不会出故障。每个ViewSet都是一个独立的类，分别处理不同的模型（Workflow、Node、Edge），
    #    它们的queryset和serializer_class属性虽然命名一致，但指向的对象不同（分别是各自的模型和序列化器）。
    #    在Django的路由系统中，每个ViewSet会被单独注册到不同的URL路径下，互不影响。
    #    因此，无论实例化还是命名，都不会冲突或出错。