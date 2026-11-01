"""
URL routing for Medical Knowledge App.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.medical_knowledge.views import (
    DiseaseViewSet, SymptomViewSet, MedicineViewSet,
    DrugInteractionViewSet, DiseaseTreatmentViewSet
)

router = DefaultRouter()
router.register(r'diseases', DiseaseViewSet, basename='disease')
router.register(r'symptoms', SymptomViewSet, basename='symptom')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'drug-interactions', DrugInteractionViewSet, basename='drug-interaction')
router.register(r'treatments', DiseaseTreatmentViewSet, basename='treatment')

urlpatterns = [
    path('', include(router.urls)),
]
