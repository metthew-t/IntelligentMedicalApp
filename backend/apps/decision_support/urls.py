"""
URL routing for Decision Support App.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.decision_support.views import DecisionSupportViewSet

router = DefaultRouter()
router.register(r'', DecisionSupportViewSet, basename='decision-support')

urlpatterns = [
    path('', include(router.urls)),
]
