# backend/companies/admin.py
from django.contrib import admin
from .models import Company

class CompanyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'role') and getattr(request.user, 'role', None) == 'superadmin':
            return qs
        return qs.filter(id=getattr(request.user, 'company_id', None))

# admin.site.unregister(Company)
admin.site.register(Company, CompanyAdmin)