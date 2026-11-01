"""
URL Configuration for Intelligent Medical and Hospital Management System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import LoginView, LogoutView
from apps.decision_support.web_views import CDSSDashboardView

urlpatterns = [
    # Interactive CDSS Web Dashboard
    path('', CDSSDashboardView.as_view(), name='cdss-home'),
    path('cdss/', CDSSDashboardView.as_view(), name='cdss-dashboard'),

    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', include('health_check.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('api/v1/auth/login/', LoginView.as_view(), name='login'),
    path('api/v1/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API v1
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/patients/', include('apps.patients.urls')),
    path('api/v1/encounters/', include('apps.encounters.urls')),
    path('api/v1/medical-knowledge/', include('apps.medical_knowledge.urls')),
    path('api/v1/decision-support/', include('apps.decision_support.urls')),
    path('api/v1/prescriptions/', include('apps.prescriptions.urls')),
    path('api/v1/laboratory/', include('apps.laboratory.urls')),
    path('api/v1/imaging/', include('apps.imaging.urls')),
    path('api/v1/pharmacy/', include('apps.pharmacy.urls')),
    path('api/v1/appointments/', include('apps.appointments.urls')),
    path('api/v1/admissions/', include('apps.admissions.urls')),
    path('api/v1/nursing/', include('apps.nursing.urls')),
    path('api/v1/billing/', include('apps.billing.urls')),
    path('api/v1/referrals/', include('apps.referrals.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/data-imports/', include('apps.data_imports.urls')),
    path('api/v1/ml-governance/', include('apps.ml_governance.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom admin site configuration
admin.site.site_header = "Intelligent Medical System Administration"
admin.site.site_title = "Intelligent Medical Admin"
admin.site.index_title = "Welcome to Intelligent Medical System Administration"
