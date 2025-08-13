from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import CredentialViewSet

router = DefaultRouter()
router.register(r'credentials', CredentialViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]