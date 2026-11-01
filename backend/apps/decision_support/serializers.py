"""
Serializers for Clinical Decision Support System (CDSS) and Machine Learning Diagnosis.
"""
from rest_framework import serializers
from apps.decision_support.models import DecisionSupportRequest, DecisionSupportCandidate
from apps.medical_knowledge.models import Disease


class DiagnosticInputSerializer(serializers.Serializer):
    """
    Input schema for requesting hybrid ML diagnostic inference.
    """
    symptoms = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        default=list,
        help_text="List of symptoms reported by the patient (e.g. ['Fever', 'Chills', 'Headache'] or [{'name': 'Fever', 'severity': 'high'}])"
    )
    signs = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        default=list,
        help_text="List of physical exam signs observed by clinician (e.g. ['Jaundice', 'Splenomegaly'])"
    )
    vital_signs = serializers.DictField(
        required=False,
        default=dict,
        help_text="Vitals: {'temperature': 39.1, 'spo2': 96, 'systolic_bp': 120, 'diastolic_bp': 80, 'heart_rate': 102, 'respiratory_rate': 20}"
    )
    demographics = serializers.DictField(
        required=False,
        default=dict,
        help_text="Patient demographics: {'age': 28, 'gender': 'female', 'is_pregnant': false, 'weight_kg': 60}"
    )
    medical_history = serializers.DictField(
        required=False,
        default=dict,
        help_text="Medical history: {'allergies': ['penicillin'], 'current_medications': ['metformin'], 'chronic_conditions': ['type_2_diabetes']}"
    )
    anamnesis = serializers.DictField(
        required=False,
        default=dict,
        help_text="Oral clinical history: {'chief_complaint': 'severe chest pain', 'onset': 'acute', 'duration_hours': 3, 'character': 'crushing', 'radiation': 'left_arm', 'travel_history': 'none'}"
    )
    physical_exam = serializers.DictField(
        required=False,
        default=dict,
        help_text="Doctor's physical exam: {'cardiovascular': ['systolic_murmur'], 'respiratory': ['crackles'], 'abdominal': ['mcburney_tenderness'], 'neuro': ['neck_stiffness']}"
    )
    laboratory_results = serializers.DictField(
        required=False,
        default=dict,
        help_text="Laboratory test values: {'troponin_i': 1.8, 'wbc_count': 16500, 'blood_glucose': 240, 'creatinine': 1.4, 'crp': 85, 'malaria_smear': 'positive', 'urine_ketones': 'positive'}"
    )
    diagnostic_tools = serializers.DictField(
        required=False,
        default=dict,
        help_text="Bedside diagnostic & imaging tools: {'ecg': 'st_elevation_v1_v4', 'chest_xray': 'lobar_consolidation', 'ct_head': 'ischemic_infarct', 'ultrasound_pocus': 'gallstones'}"
    )


class DecisionSupportCandidateSerializer(serializers.ModelSerializer):
    """Serializer for individual differential diagnosis candidates."""
    disease_id = serializers.UUIDField(source='disease.id', read_only=True)
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    icd10_code = serializers.CharField(source='disease.icd10_code', read_only=True)
    category = serializers.CharField(source='disease.get_category_display', read_only=True)
    confidence_display = serializers.CharField(source='get_confidence_level_display', read_only=True)
    clinician_decision_display = serializers.CharField(source='get_clinician_decision_display', read_only=True)

    class Meta:
        model = DecisionSupportCandidate
        fields = [
            'id', 'disease_id', 'disease_name', 'icd10_code', 'category',
            'rank', 'probability_score', 'confidence_level', 'confidence_display',
            'supporting_findings', 'contradicting_findings', 'missing_information',
            'red_flags', 'suggested_investigations', 'recommended_treatments',
            'contraindication_alerts',
            'clinician_decision', 'clinician_decision_display', 'clinician_feedback',
            'decided_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DecisionSupportRequestSerializer(serializers.ModelSerializer):
    """Serializer for CDSS diagnostic requests with nested candidates."""
    candidates = DecisionSupportCandidateSerializer(many=True, read_only=True)
    triage_level_display = serializers.CharField(source='get_triage_level_display', read_only=True)
    processing_status_display = serializers.CharField(source='get_processing_status_display', read_only=True)
    requested_by_email = serializers.CharField(source='requested_by.email', read_only=True)

    class Meta:
        model = DecisionSupportRequest
        fields = [
            'id', 'patient_demographics', 'symptoms', 'signs', 'vital_signs',
            'medical_history', 'anamnesis', 'physical_exam', 'laboratory_results', 'diagnostic_tools',
            'engine_version', 'model_version',
            'triage_level', 'triage_level_display',
            'processing_status', 'processing_status_display',
            'processing_time_ms', 'candidates',
            'requested_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClinicianFeedbackSerializer(serializers.Serializer):
    """Serializer for clinician validation feedback on a diagnostic candidate."""
    decision = serializers.ChoiceField(
        choices=DecisionSupportCandidate.ClinicianDecision.choices,
        help_text="Clinician validation: 'confirmed', 'rejected', 'deferred', 'requires_investigation'"
    )
    feedback = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Clinical justification, notes, or lab confirmation findings"
    )
