"""
Views for the organizations app.
"""
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Organization, FacilityType, Facility, Department, Ward
from .serializers import (
    OrganizationSerializer, FacilityTypeSerializer,
    FacilitySerializer, FacilityListSerializer,
    DepartmentSerializer, DepartmentListSerializer,
    WardSerializer
)
from apps.core.permissions import IsSystemAdmin, IsHospitalAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model."""
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'city', 'region']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Only system admins can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSystemAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def facilities(self, request, pk=None):
        """Get all facilities for an organization."""
        organization = self.get_object()
        facilities = organization.facilities.filter(is_active=True)
        serializer = FacilityListSerializer(facilities, many=True)
        return Response(serializer.data)


class FacilityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for FacilityType model (read-only)."""
    queryset = FacilityType.objects.all()
    serializer_class = FacilityTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['name']


class FacilityViewSet(viewsets.ModelViewSet):
    """ViewSet for Facility model."""
    queryset = Facility.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'facility_type', 'city', 'region']
    search_fields = ['name', 'code', 'city', 'region', 'woreda']
    ordering_fields = ['name', 'created_at', 'bed_capacity']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacilityListSerializer
        return FacilitySerializer
    
    def get_permissions(self):
        """Hospital admins and above can manage facilities."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHospitalAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def departments(self, request, pk=None):
        """Get all departments for a facility."""
        facility = self.get_object()
        departments = facility.departments.filter(is_active=True)
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get facility statistics."""
        facility = self.get_object()
        departments = facility.departments.filter(is_active=True)
        
        total_beds = sum(dept.bed_count for dept in departments)
        total_wards = sum(
            dept.wards.filter(is_active=True).count()
            for dept in departments
        )
        
        return Response({
            'facility_name': facility.name,
            'departments_count': departments.count(),
            'total_beds': total_beds,
            'total_wards': total_wards,
            'bed_capacity': facility.bed_capacity,
            'staff_count': facility.staff_count,
            'license_valid': facility.is_license_valid(),
        })


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department model."""
    queryset = Department.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['facility', 'parent_department']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['facility', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer
    
    def get_permissions(self):
        """Hospital admins and above can manage departments."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHospitalAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filter by user's facilities if not admin."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            return queryset
        
        # Filter by user's facilities
        facility_ids = user.user_roles.filter(
            is_active=True,
            facility__isnull=False
        ).values_list('facility_id', flat=True)
        
        return queryset.filter(facility_id__in=facility_ids)
    
    @action(detail=True, methods=['get'])
    def wards(self, request, pk=None):
        """Get all wards for a department."""
        department = self.get_object()
        wards = department.wards.filter(is_active=True)
        serializer = WardSerializer(wards, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sub_departments(self, request, pk=None):
        """Get sub-departments."""
        department = self.get_object()
        sub_departments = department.sub_departments.filter(is_active=True)
        serializer = DepartmentListSerializer(sub_departments, many=True)
        return Response(serializer.data)


class WardViewSet(viewsets.ModelViewSet):
    """ViewSet for Ward model."""
    queryset = Ward.objects.filter(is_active=True)
    serializer_class = WardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'ward_type', 'gender_specific']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at', 'occupancy_rate']
    ordering = ['department', 'name']
    
    def get_permissions(self):
        """Hospital admins and above can manage wards."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHospitalAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filter by user's facilities if not admin."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            return queryset
        
        # Filter by user's facilities
        facility_ids = user.user_roles.filter(
            is_active=True,
            facility__isnull=False
        ).values_list('facility_id', flat=True)
        
        return queryset.filter(department__facility_id__in=facility_ids)
    
    @action(detail=True, methods=['post'])
    def update_occupancy(self, request, pk=None):
        """Update ward occupancy."""
        ward = self.get_object()
        occupied_beds = request.data.get('occupied_beds')
        
        if occupied_beds is None:
            return Response(
                {'error': 'occupied_beds is required'},
                status=400
            )
        
        if occupied_beds > ward.bed_capacity:
            return Response(
                {'error': 'Occupied beds cannot exceed capacity'},
                status=400
            )
        
        ward.occupied_beds = occupied_beds
        ward.save(update_fields=['occupied_beds'])
        
        serializer = self.get_serializer(ward)
        return Response(serializer.data)
