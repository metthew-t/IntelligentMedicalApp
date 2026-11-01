"""
Views and API ViewSets for Medical Knowledge App.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)
from apps.medical_knowledge.serializers import (
    DiseaseListSerializer, DiseaseDetailSerializer,
    SymptomSerializer, DiseaseSymptomSerializer,
    MedicineSerializer, DrugInteractionSerializer, DiseaseTreatmentSerializer
)


class DiseaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for medical diseases and clinical profiles.
    """
    queryset = Disease.objects.prefetch_related(
        'disease_symptoms__symptom',
        'treatments__medicine'
    ).filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'synonyms', 'icd10_code', 'icd11_code', 'definition', 'category']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return DiseaseDetailSerializer
        return DiseaseListSerializer

    @action(detail=True, methods=['get'], url_path='symptoms')
    def list_symptoms(self, request, pk=None):
        """Returns all signs and symptoms associated with this disease."""
        disease = self.get_object()
        associations = disease.disease_symptoms.select_related('symptom').filter(is_active=True)
        serializer = DiseaseSymptomSerializer(associations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='treatments')
    def list_treatments(self, request, pk=None):
        """Returns evidence-based medicines and regimens for this disease."""
        disease = self.get_object()
        treatments = disease.treatments.select_related('medicine').filter(is_active=True)
        serializer = DiseaseTreatmentSerializer(treatments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='categories')
    def list_categories(self, request):
        """Returns distinct disease categories with counts."""
        categories = []
        for code, label in Disease.Category.choices:
            count = Disease.objects.filter(category=code, is_active=True).count()
            categories.append({
                'code': code,
                'name': label,
                'count': count
            })
        return Response(categories)


class SymptomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for clinical signs and symptoms.
    Supports filtering by body system, distinguishing objective Signs vs subjective Symptoms,
    and fast autocomplete searching.
    """
    queryset = Symptom.objects.filter(is_active=True)
    serializer_class = SymptomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'synonyms', 'description', 'body_system']
    ordering_fields = ['name', 'body_system', 'severity_weight']
    ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        body_system = self.request.query_params.get('body_system')
        symptom_type = self.request.query_params.get('symptom_type') # 'sign', 'symptom', 'both'
        is_red_flag = self.request.query_params.get('is_red_flag')

        if body_system:
            qs = qs.filter(body_system=body_system)
        if symptom_type:
            if symptom_type in ['sign', 'symptom']:
                qs = qs.filter(Q(symptom_type=symptom_type) | Q(symptom_type='both'))
            else:
                qs = qs.filter(symptom_type=symptom_type)
        if is_red_flag is not None:
            qs = qs.filter(is_red_flag=is_red_flag.lower() in ['true', '1'])
        return qs

    @action(detail=False, methods=['get'], url_path='body-systems')
    def list_body_systems(self, request):
        """Returns all anatomical body systems with counts of signs & symptoms."""
        systems = []
        for code, label in Symptom.BodySystem.choices:
            signs_count = Symptom.objects.filter(body_system=code, symptom_type__in=['sign', 'both'], is_active=True).count()
            symptoms_count = Symptom.objects.filter(body_system=code, symptom_type__in=['symptom', 'both'], is_active=True).count()
            systems.append({
                'code': code,
                'name': label,
                'signs_count': signs_count,
                'symptoms_count': symptoms_count,
                'total_count': Symptom.objects.filter(body_system=code, is_active=True).count()
            })
        return Response(systems)

    @action(detail=False, methods=['get'], url_path='red-flags')
    def list_red_flags(self, request):
        """Returns all critical red flag danger signs."""
        red_flags = Symptom.objects.filter(is_red_flag=True, is_active=True).order_by('body_system', 'name')
        serializer = SymptomSerializer(red_flags, many=True)
        return Response(serializer.data)


class MedicineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for medicines, dosages, and contraindications.
    """
    queryset = Medicine.objects.filter(is_active=True)
    serializer_class = MedicineSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['generic_name', 'brand_names', 'drug_class', 'indications', 'atc_code']
    ordering_fields = ['generic_name', 'drug_class']
    ordering = ['generic_name']


class DrugInteractionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for checking drug interactions.
    """
    queryset = DrugInteraction.objects.select_related('medicine_a', 'medicine_b').filter(is_active=True)
    serializer_class = DrugInteractionSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='check')
    def check_interactions(self, request):
        """
        Check mutual drug-drug interactions for a given list of medicine IDs or generic names.
        Input: {"medicine_ids": ["uuid1", "uuid2"]} OR {"medicine_names": ["Metronidazole", "Alcohol"]}
        """
        medicine_ids = request.data.get('medicine_ids', [])
        medicine_names = request.data.get('medicine_names', [])
        
        target_med_ids = set()
        if medicine_ids:
            target_med_ids.update(medicine_ids)
        if medicine_names:
            found_ids = Medicine.objects.filter(
                Q(generic_name__in=medicine_names) | Q(brand_names__overlap=medicine_names)
            ).values_list('id', flat=True)
            target_med_ids.update(str(x) for x in found_ids)

        if len(target_med_ids) < 2:
            return Response({
                'count': 0,
                'interactions': [],
                'message': 'At least 2 medications are required to check for interactions.'
            })

        interactions = DrugInteraction.objects.filter(
            Q(medicine_a_id__in=target_med_ids, medicine_b_id__in=target_med_ids) |
            Q(medicine_b_id__in=target_med_ids, medicine_a_id__in=target_med_ids),
            is_active=True
        ).select_related('medicine_a', 'medicine_b')

        serializer = DrugInteractionSerializer(interactions, many=True)
        return Response({
            'count': interactions.count(),
            'has_contraindications': interactions.filter(severity='contraindicated').exists(),
            'interactions': serializer.data
        })


class DiseaseTreatmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for disease treatment protocols.
    """
    queryset = DiseaseTreatment.objects.select_related('disease', 'medicine').filter(is_active=True)
    serializer_class = DiseaseTreatmentSerializer
    permission_classes = [AllowAny]
