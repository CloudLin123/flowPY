"""API权限控制类"""
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    只允许管理员修改组件，其他用户只读
    """
    def has_permission(self, request, view):
        # 对于只读请求允许所有用户
        if request.method in permissions.SAFE_METHODS:
            return True

        # 只有管理员可编辑
        return request.user and request.user.is_staff

class HasComponentAccess(permissions.BasePermission):
    """
    组件访问权限限制
    可以扩展实现更细粒度的访问控制
    """
    def has_object_permission(self, request, view, obj):
        # 目前所有已认证用户都可以访问所有组件
        # 可以根据需要扩展为基于角色或组的访问控制
        return request.user and request.user.is_authenticated
        