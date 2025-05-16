from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ("first_name", "last_name", "email", "company", "role", "created_at")
    list_filter = ("company", "role")
    search_fields = ("first_name", "last_name", "email")
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('company', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'company', 'role'),
        }),
    )
    change_password_form = AdminPasswordChangeForm
    
    def get_urls(self):
        from django.urls import path
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

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
        if getattr(request.user, 'role', None) == 'company_admin':
            obj.company = request.user.company
            obj.role = 'user'
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        if obj and getattr(request.user, 'role', None) == 'company_admin':
            return obj.company == request.user.company and obj.role == 'user'
        return True

admin.site.register(User, UserAdmin)
