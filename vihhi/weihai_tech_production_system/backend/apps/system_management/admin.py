from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Department, Role, PermissionItem, RegistrationRequest
from .services_registration import finalize_approval


@admin.register(PermissionItem)
class PermissionItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'module', 'action', 'is_active')
    list_filter = ('module', 'is_active')
    search_fields = ('code', 'name', 'description')
    ordering = ('module', 'action')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_time')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    filter_horizontal = ('custom_permissions', 'permissions')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'leader', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('order',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username',
        'get_full_name',
        'user_type',
        'department',
        'position',
        'is_active',
        'is_staff',
    )
    list_filter = ('user_type', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    filter_horizontal = ('roles',)
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            '组织信息',
            {
                'fields': (
                    'phone',
                    'department',
                    'position',
                    'user_type',
                    'client_type',
                    'avatar',
                    'roles',
                    'profile_completed',
                )
            },
        ),
    )


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'client_type', 'status', 'submitted_time')
    list_filter = ('client_type', 'status')
    search_fields = ('username', 'phone')
    readonly_fields = ('submitted_time', 'processed_time', 'processed_by')

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            try:
                previous_status = RegistrationRequest.objects.only('status').get(pk=obj.pk).status
            except RegistrationRequest.DoesNotExist:
                previous_status = None

        super().save_model(request, obj, form, change)

        if obj.status == RegistrationRequest.STATUS_APPROVED:
            if previous_status != RegistrationRequest.STATUS_APPROVED or obj.processed_time is None:
                finalize_approval(obj, processed_by=request.user)

