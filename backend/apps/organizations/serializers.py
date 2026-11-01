"""
Serializers for the organizations app.
"""
from rest_framework import serializers
from .models import Organization, FacilityType, Facility, Department, Ward


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    facilities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'code', 'description', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'region', 'country',
            'postal_code', 'logo', 'facilities_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_facilities_count(self, obj):
        return obj.get_facilities_count()


class FacilityTypeSerializer(serializers.ModelSerializer):
    """Serializer for FacilityType model."""
    
    class Meta:
        model = FacilityType
        fields = ['id', 'name', 'code', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class FacilitySerializer(serializers.ModelSerializer):
    """Serializer for Facility model."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    facility_type_name = serializers.CharField(source='facility_type.name', read_only=True)
    license_valid = serializers.SerializerMethodField()
    departments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Facility
        fields = [
            'id', 'organization', 'organization_name', 'facility_type',
            'facility_type_name', 'name', 'code', 'description',
            'email', 'phone', 'emergency_phone',
            'address_line1', 'address_line2', 'city', 'region',
            'woreda', 'kebele', 'country', 'postal_code',
            'latitude', 'longitude',
            'license_number', 'license_issue_date', 'license_expiry_date',
            'license_valid', 'accreditation_level',
            'bed_capacity', 'staff_count', 'operating_hours', 'is_24_7',
            'services_offered', 'departments_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'license_valid']
    
    def get_license_valid(self, obj):
        return obj.is_license_valid()
    
    def get_departments_count(self, obj):
        return obj.departments.filter(is_active=True).count()


class FacilityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing facilities."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    facility_type_name = serializers.CharField(source='facility_type.name', read_only=True)
    
    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'code', 'organization_name',
            'facility_type_name', 'city', 'region',
            'bed_capacity', 'is_active'
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    parent_department_name = serializers.CharField(
        source='parent_department.name',
        read_only=True
    )
    head_of_department_name = serializers.SerializerMethodField()
    full_hierarchy = serializers.SerializerMethodField()
    wards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'facility', 'facility_name', 'name', 'code', 'description',
            'parent_department', 'parent_department_name', 'full_hierarchy',
            'head_of_department', 'head_of_department_name',
            'phone', 'extension', 'email', 'location',
            'bed_count', 'staff_count', 'specializations',
            'wards_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_hierarchy']
    
    def get_head_of_department_name(self, obj):
        if obj.head_of_department:
            return obj.head_of_department.get_full_name()
        return None
    
    def get_full_hierarchy(self, obj):
        return obj.get_full_hierarchy()
    
    def get_wards_count(self, obj):
        return obj.wards.filter(is_active=True).count()


class DepartmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing departments."""
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'facility_name',
            'bed_count', 'staff_count', 'is_active'
        ]


class WardSerializer(serializers.ModelSerializer):
    """Serializer for Ward model."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    available_beds = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Ward
        fields = [
            'id', 'department', 'department_name', 'name', 'code',
            'description', 'ward_type', 'bed_capacity', 'occupied_beds',
            'available_beds', 'occupancy_rate', 'floor', 'building',
            'gender_specific', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available_beds(self, obj):
        return obj.get_available_beds()
    
    def get_occupancy_rate(self, obj):
        return round(obj.get_occupancy_rate(), 2)
    
    def validate(self, attrs):
        """Validate occupied beds doesn't exceed capacity."""
        occupied_beds = attrs.get('occupied_beds', 0)
        bed_capacity = attrs.get('bed_capacity', 0)
        
        if occupied_beds > bed_capacity:
            raise serializers.ValidationError(
                "Occupied beds cannot exceed bed capacity."
            )
        
        return attrs
