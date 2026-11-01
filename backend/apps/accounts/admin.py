"""
Django admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Role, Permission, RolePermission, UserRole, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'is_active', 'is_staff', 'account_status', 'last_login'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'mfa_enabled', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'profile_photo',
                      'language_preference', 'timezone')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                      'groups', 'user_permissions')
        }),
        ('Security', {
            'fields': ('must_change_password', 'password_changed_at',
                      'failed_login_attempts', 'locked_until',
                      'mfa_enabled', 'mfa_secret')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'last_activity', 'date_joined')
        }),
    )
    
    readonly_fields = [
        'date_joined', 'last_login', 'last_activity',
        'failed_login_attempts', 'password_changed_at'
    ]
    
    def account_status(self, obj):
        """Display account status with color coding."""
        if obj.is_account_locked():
            return format_html(
                '<span style="color: red;">🔒 Locked</span>'
            )
        elif not obj.is_active:
            return format_html(
                '<span style="color: orange;">⚠️ Inactive</span>'
            )
        return format_html(
            '<span style="color: green;">✓ Active</span>'
        )
    account_status.short_description = 'Status'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    list_display = ['name', 'code', 'is_system_role', 'users_count', 'permissions_count', 'created_at']
    list_filter = ['is_system_role', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at']
    
    def users_count(self, obj):
        """Count of users with this role."""
        return obj.user_assignments.filter(is_active=True).count()
    users_count.short_description = 'Active Users'
    
    def permissions_count(self, obj):
        """Count of permissions for this role."""
        return obj.role_permissions.count()
    permissions_count.short_description = 'Permissions'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of system roles."""
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for Permission model."""
    list_display = ['code', 'name', 'resource_type', 'action', 'roles_count', 'created_at']
    list_filter = ['resource_type', 'action', 'created_at']
    search_fields = ['code', 'name', 'resource_type', 'action']
    readonly_fields = ['created_at']
    
    def roles_count(self, obj):
        """Count of roles with this permission."""
        return obj.permission_roles.count()
    roles_count.short_description = 'Roles'


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin interface for RolePermission model."""
    list_display = ['role', 'permission', 'granted_at']
    list_filter = ['role', 'granted_at']
    search_fields = ['role__name', 'permission__code']
    readonly_fields = ['granted_at']
    autocomplete_fields = ['role', 'permission']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for UserRole model."""
    list_display = [
        'user', 'role', 'facility', 'is_active',
        'expires_status', 'granted_by', 'granted_at'
    ]
    list_filter = ['is_active', 'role', 'granted_at']
    search_fields = ['user__email', 'user__username', 'role__name']
    readonly_fields = ['granted_at', 'granted_by']
    autocomplete_fields = ['user', 'role', 'facility', 'granted_by']
    
    def expires_status(self, obj):
        """Display expiration status."""
        if not obj.expires_at:
            return format_html('<span style="color: green;">No expiration</span>')
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html(
            '<span style="color: orange;">Expires: {}</span>',
            obj.expires_at.strftime('%Y-%m-%d')
        )
    expires_status.short_description = 'Expiration'
    
    def save_model(self, request, obj, form, change):
        """Set granted_by to current user on creation."""
        if not change:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin interface for LoginAttempt model."""
    list_display = [
        'username', 'user', 'ip_address', 'success_status',
        'attempted_at'
    ]
    list_filter = ['success', 'attempted_at']
    search_fields = ['username', 'user__email', 'ip_address']
    readonly_fields = ['attempted_at']
    date_hierarchy = 'attempted_at'
    
    def success_status(self, obj):
        """Display success status with color coding."""
        if obj.success:
            return format_html('<span style="color: green;">✓ Success</span>')
        return format_html(
            '<span style="color: red;">✗ Failed: {}</span>',
            obj.failure_reason[:50]
        )
    success_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing."""
        return False
