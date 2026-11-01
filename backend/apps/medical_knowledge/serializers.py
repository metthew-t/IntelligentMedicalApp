"""
Serializers for Medical Knowledge App.
Provides structured representation for Diseases, Symptoms, Physical Signs,
Medicines, Drug Interactions, and Evidence-based Treatments.
"""
from rest_framework import serializers
from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)


class SymptomSerializer(serializers.ModelSerializer):
    """Serializer for Symptoms and Physical Signs."""
    symptom_type_display = serializers.CharField(source='get_symptom_type_display', read_only=True)
    body_system_display = serializers.CharField(source='get_body_system_display', read_only=True)

    class Meta:
        model = Symptom
        fields = [
            'id', 'name', 'name_local', 'synonyms', 'description',
            'category', 'body_system', 'body_system_display',
            'symptom_type', 'symptom_type_display',
            'snomed_code', 'icon_name', 'is_red_flag', 'severity_weight',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiseaseSymptomSerializer(serializers.ModelSerializer):
    """Serializer for Disease-Symptom association."""
    symptom_id = serializers.UUIDField(source='symptom.id', read_only=True)
    symptom_name = serializers.CharField(source='symptom.name', read_only=True)
    symptom_type = serializers.CharField(source='symptom.symptom_type', read_only=True)
    body_system = serializers.CharField(source='symptom.body_system', read_only=True)
    is_red_flag = serializers.BooleanField(source='symptom.is_red_flag', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    specificity_display = serializers.CharField(source='get_specificity_display', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    class Meta:
        model = DiseaseSymptom
        fields = [
            'id', 'symptom_id', 'symptom_name', 'symptom_type', 'body_system',
            'is_red_flag', 'frequency', 'frequency_display',
            'specificity', 'specificity_display', 'stage', 'stage_display',
            'is_hallmark', 'notes', 'evidence_level', 'numerical_weight'
        ]


class MedicineSerializer(serializers.ModelSerializer):
    """Serializer for Medicine catalog."""
    dosage_form_display = serializers.CharField(source='get_dosage_form_display', read_only=True)
    route_display = serializers.CharField(source='get_route_of_administration_display', read_only=True)

    class Meta:
        model = Medicine
        fields = [
            'id', 'generic_name', 'brand_names', 'local_names', 'drug_class', 'atc_code',
            'dosage_form', 'dosage_form_display', 'strength', 'unit',
            'route_of_administration', 'route_display',
            'indications', 'contraindications', 'warnings', 'adverse_reactions',
            'pregnancy_category', 'breastfeeding_safety',
            'adult_dosing', 'pediatric_dosing', 'renal_adjustment', 'hepatic_adjustment',
            'maximum_dose', 'is_essential_medicine', 'formulary_status', 'restricted',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiseaseTreatmentSerializer(serializers.ModelSerializer):
    """Serializer for Disease Treatment Protocols."""
    medicine_details = MedicineSerializer(source='medicine', read_only=True)
    treatment_line_display = serializers.CharField(source='get_treatment_line_display', read_only=True)

    class Meta:
        model = DiseaseTreatment
        fields = [
            'id', 'disease', 'medicine', 'medicine_details',
            'treatment_line', 'treatment_line_display',
            'regimen_instructions', 'target_population', 'precautions'
        ]


class DrugInteractionSerializer(serializers.ModelSerializer):
    """Serializer for Drug-to-Drug Interactions."""
    medicine_a_name = serializers.CharField(source='medicine_a.generic_name', read_only=True)
    medicine_b_name = serializers.CharField(source='medicine_b.generic_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)

    class Meta:
        model = DrugInteraction
        fields = [
            'id', 'medicine_a', 'medicine_b',
            'medicine_a_name', 'medicine_b_name',
            'severity', 'severity_display',
            'interaction_type', 'interaction_type_display',
            'description', 'clinical_management', 'evidence_level', 'source'
        ]


class DiseaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for disease listing and search."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    symptoms_count = serializers.IntegerField(source='disease_symptoms.count', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'name_local', 'category', 'category_display',
            'icd10_code', 'icd11_code', 'typical_age_group',
            'symptoms_count', 'status', 'is_active'
        ]


class DiseaseDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Disease with signs, symptoms, and treatments."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    disease_symptoms = DiseaseSymptomSerializer(many=True, read_only=True)
    treatments = DiseaseTreatmentSerializer(many=True, read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'name_local', 'synonyms', 'category', 'category_display',
            'icd10_code', 'icd11_code', 'definition', 'etiology',
            'risk_factors', 'complications', 'typical_age_group',
            'diagnostic_criteria', 'management_overview', 'prevention_guidance',
            'referral_criteria', 'source_organization', 'source_url', 'source_version',
            'jurisdiction', 'version', 'status', 'disease_symptoms', 'treatments',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
