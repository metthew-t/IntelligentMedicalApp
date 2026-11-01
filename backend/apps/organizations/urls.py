"""
URL patterns for the organizations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, FacilityTypeViewSet, FacilityViewSet,
    DepartmentViewSet, WardViewSet
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'facility-types', FacilityTypeViewSet, basename='facility-type')
router.register(r'facilities', FacilityViewSet, basename='facility')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'wards', WardViewSet, basename='ward')

urlpatterns = [
    path('', include(router.urls)),
]
