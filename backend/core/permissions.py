from rest_framework import permissions
from companies.models import Company

class IsCompanyUserOrAdmin(permissions.BasePermission):
    """
    Sadece kendi şirketinin verilerine erişim izni verir.
    Superadmin tüm verilere erişebilir.
    Company admin ve company user sadece kendi şirketinin verilerine erişebilir.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Superadmin has all permissions
        if user_role == 'superadmin':
            return True
            
        # Both company_admin and regular users need a company association
        return bool(getattr(user, 'company', None))

    def has_object_permission(self, request, view, obj):
        user = request.user
        user_role = getattr(user, 'role', None)
        user_company = getattr(user, 'company', None)

        # Superadmin can do anything
        if user_role == 'superadmin':
            return True

        # For Company model directly
        if isinstance(obj, Company):
            return obj.id == user_company.id if user_company else False

        # For objects with company field
        if hasattr(obj, 'company'):
            return obj.company == user_company
            
        return False
