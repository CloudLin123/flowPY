"""
组件应用的URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import ComponentViewSet

router = DefaultRouter()
router.register(r'components', ComponentViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]