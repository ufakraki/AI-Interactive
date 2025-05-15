from rest_framework import permissions

class IsCompanyUserOrAdmin(permissions.BasePermission):
    """
    Sadece kendi şirketinin verilerine erişim izni verir.
    Superadmin ise tüm verilere erişebilir.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            if getattr(request.user, 'role', None) == 'superadmin':
                return True
            return obj.company == getattr(request.user, 'company', None)
        return False