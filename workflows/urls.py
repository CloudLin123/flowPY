from django.urls import path, include  # 导入Django的path和include，用于URL路由配置
from rest_framework.routers import DefaultRouter  # 导入DRF的DefaultRouter，用于自动生成RESTful路由
from .api.views import WorkflowViewSet, NodeViewSet, EdgeViewSet  # 导入视图集

# 创建一个默认的路由器对象
router = DefaultRouter()
# 注册工作流的视图集，自动生成workflows相关的RESTful接口
router.register(r'workflows', WorkflowViewSet)
# 注册节点的视图集，自动生成nodes相关的RESTful接口
router.register(r'nodes', NodeViewSet)
# 注册边的视图集，自动生成edges相关的RESTful接口
router.register(r'edges', EdgeViewSet)

# 定义URL模式列表，将router自动生成的所有接口挂载到api/路径下
urlpatterns = [
    path('api/', include(router.urls))  # include(router.urls)会自动包含所有注册的路由
]

# 解释：
# 1. urlpatterns 是Django项目中用于定义URL路由的列表。它告诉Django哪些URL请求应该由哪些视图处理。
#    在这里，urlpatterns把所有通过router注册的RESTful接口都挂载到了'api/'路径下。
#    例如，访问/api/workflows/会自动路由到WorkflowViewSet对应的接口。
# 2. router.register 是DRF（Django REST framework）中用于注册视图集的方法。
#    它的作用是将某个ViewSet（如WorkflowViewSet）与一个URL前缀（如'workflows'）绑定，
#    并自动生成标准的增删改查（CRUD）接口，无需手动为每个操作编写URL。