"""
Django admin configuration for organizations app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Organization, FacilityType, Facility, Department, Ward


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model."""
    list_display = ['name', 'code', 'city', 'region', 'facilities_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'region', 'country', 'created_at']
    search_fields = ['name', 'code', 'email', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'region', 'country', 'postal_code')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def facilities_count(self, obj):
        """Count of facilities."""
        count = obj.get_facilities_count()
        return format_html('<strong>{}</strong>', count)
    facilities_count.short_description = 'Facilities'


@admin.register(FacilityType)
class FacilityTypeAdmin(admin.ModelAdmin):
    """Admin interface for FacilityType model."""
    list_display = ['name', 'code', 'facilities_count', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']
    
    def facilities_count(self, obj):
        """Count of facilities."""
        return obj.facilities.count()
    facilities_count.short_description = 'Facilities'


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    """Admin interface for Facility model."""
    list_display = [
        'name', 'code', 'facility_type', 'city', 'region',
        'bed_capacity', 'license_status', 'is_active'
    ]
    list_filter = [
        'is_active', 'facility_type', 'region', 'accreditation_level',
        'is_24_7', 'created_at'
    ]
    search_fields = ['name', 'code', 'license_number', 'city', 'woreda']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['organization', 'facility_type']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'facility_type', 'name', 'code', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'emergency_phone')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'region',
                'woreda', 'kebele', 'country', 'postal_code',
                'latitude', 'longitude'
            )
        }),
        ('Licensing & Accreditation', {
            'fields': (
                'license_number', 'license_issue_date', 'license_expiry_date',
                'accreditation_level'
            )
        }),
        ('Capacity & Operations', {
            'fields': (
                'bed_capacity', 'staff_count', 'operating_hours',
                'is_24_7', 'services_offered'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def license_status(self, obj):
        """Display license status."""
        if not obj.license_number:
            return format_html('<span style="color: gray;">No License</span>')
        if obj.is_license_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')
    license_status.short_description = 'License'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    list_display = [
        'name', 'code', 'facility', 'head_of_department',
        'bed_count', 'staff_count', 'is_active'
    ]
    list_filter = ['is_active', 'facility', 'created_at']
    search_fields = ['name', 'code', 'facility__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['facility', 'parent_department', 'head_of_department']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('facility', 'name', 'code', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent_department', 'head_of_department')
        }),
        ('Contact Information', {
            'fields': ('phone', 'extension', 'email', 'location')
        }),
        ('Capacity & Specialization', {
            'fields': ('bed_count', 'staff_count', 'specializations')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    """Admin interface for Ward model."""
    list_display = [
        'name', 'code', 'department', 'ward_type',
        'bed_capacity', 'occupied_beds', 'occupancy_display', 'is_active'
    ]
    list_filter = ['is_active', 'ward_type', 'gender_specific', 'department__facility']
    search_fields = ['name', 'code', 'department__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['department']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'name', 'code', 'description', 'ward_type')
        }),
        ('Capacity', {
            'fields': ('bed_capacity', 'occupied_beds')
        }),
        ('Location', {
            'fields': ('floor', 'building', 'gender_specific')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def occupancy_display(self, obj):
        """Display occupancy rate with color coding."""
        rate = obj.get_occupancy_rate()
        if rate >= 90:
            color = 'red'
        elif rate >= 75:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    occupancy_display.short_description = 'Occupancy'
