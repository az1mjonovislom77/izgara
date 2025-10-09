from rest_framework import permissions


class IsAdminRoleOrSuperuser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_superuser', False):
            return True
        user_role = getattr(user, 'role', None)
        user_cls = user.__class__
        admin_role_value = getattr(user_cls, 'UserRoles', None)
        if admin_role_value:
            try:
                ADMIN_VALUE = user_cls.UserRoles.ADMIN
            except Exception:
                ADMIN_VALUE = None
            return user_role == ADMIN_VALUE
        return False
