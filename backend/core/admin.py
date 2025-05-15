from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "role", "created_at")
    list_filter = ("company", "role")
    search_fields = ("first_name", "last_name", "email")
    # Sadece role ve company alanlarını sadeleştir
    fields = ("first_name", "last_name", "email", "company", "role")
    # Sadece iki rol seçeneği sun
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role":
            if getattr(request.user, 'role', None) == 'company_admin':
                kwargs['choices'] = [("user", "User")]
            else:
                kwargs['choices'] = [("company_admin", "Company Admin"), ("user", "User")]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'role') and getattr(request.user, 'role', None) == 'superadmin':
            return qs
        return qs.filter(company=getattr(request.user, 'company', None))

    def save_model(self, request, obj, form, change):
        # company_admin yeni user eklerken sadece kendi şirketine ekleyebilir ve sadece user rolü açabilir
        if getattr(request.user, 'role', None) == 'company_admin':
            obj.company = request.user.company
            obj.role = 'user'
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # superadmin her userı silebilir, company_admin sadece kendi şirketinin userını silebilir
        if obj and getattr(request.user, 'role', None) == 'company_admin':
            return obj.company == request.user.company and obj.role == 'user'
        return True

admin.site.register(User, UserAdmin)
