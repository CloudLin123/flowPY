"""
URL configuration for flowisePy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""
flowisePy 项目的 URL 配置。

“urlpatterns”列表将 URL 路由到视图。有关更多信息，请参阅：
https://docs.djangoproject.com/en/4.2/topics/http/urls/
例子：
函数视图
1. 添加导入:从my_app导入视图
2. 为 urlpatterns 添加一个 URL:path('', views.home, name='home')
基于类的视图
1. 添加导入：从 other_app.views 导入主页
2. 向 urlpatterns 添加一个 URL:path('', Home.as_view(), name='home')
包括另一个 URLconf
1. 导入 include() 函数:from django.urls import include, path
2. 向 urlpatterns 添加一个 URL:path('blog/', include('blog.urls'))
"""

"""
主URL配置文件
定义所有API路由和文档入口

该文件在Django启动时加载，建立URL路径与视图函数的映射关系
文档URL访问路径:
- /swagger/: 提供交互式API文档界面
- /redoc/: 提供另一种风格的API文档
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API文档设置
schema_view = get_schema_view(
    openapi.Info(
        title = "FlowisePy API",
        default_version = "v1",
        description = "FlowisePy工作流编排系统api文档",
        contact=openapi.Contact(email="531509356@qq.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),
    # 各应用的API路由
    path('', include('workflows.urls')),
    path('', include('components.urls')),
    path('', include('core.urls')),
    # API文档
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # 可能需要的认证URL，REST框架登录界面
    path('api-auth/', include('rest_framework.urls')),
]