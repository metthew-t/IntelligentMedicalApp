"""
Models for Clinical Decision Support System (CDSS) and Machine Learning Diagnostic Engine.
Records diagnostic requests, patient symptom/sign presentation snapshots, vital signs,
ML model inferences, ranked differential diagnoses, and clinician feedback.
"""
import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class DecisionSupportRequest(BaseModel):
    """
    Diagnostic inference request snapshot containing presenting signs, symptoms,
    vital signs, patient demographics, and risk factors evaluated by the ML/CDSS engine.
    """
    
    class ProcessingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class TriageLevel(models.TextChoices):
        RESUSCITATION = 'resuscitation', 'Level 1: Resuscitation (Immediate Life Threat)'
        EMERGENCY = 'emergency', 'Level 2: Emergency (High Risk / Urgent Care within 15 min)'
        URGENT = 'urgent', 'Level 3: Urgent (Within 30-60 min)'
        LESS_URGENT = 'less_urgent', 'Level 4: Less Urgent (Routine clinic visit)'
        NON_URGENT = 'non_urgent', 'Level 5: Non-Urgent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Demographics Snapshot
    patient_demographics = models.JSONField(
        default=dict,
        help_text="Patient demographic details: {'age': 35, 'gender': 'female', 'is_pregnant': false, 'weight_kg': 65}"
    )
    
    # Clinical Presentation Inputs
    symptoms = models.JSONField(
        default=list,
        help_text="List of subjective symptoms reported by patient: [{'name': 'Fever', 'severity': 'high', 'duration_days': 4}]"
    )
    signs = models.JSONField(
        default=list,
        help_text="List of objective clinical signs detected on physical exam: [{'name': 'Splenomegaly', 'severity': 'moderate'}]"
    )
    vital_signs = models.JSONField(
        default=dict,
        help_text="Vital signs snapshot: {'temperature': 39.2, 'systolic_bp': 110, 'diastolic_bp': 70, 'heart_rate': 105, 'respiratory_rate': 22, 'spo2': 97}"
    )
    medical_history = models.JSONField(
        default=dict,
        help_text="Comorbidities, current medications, known drug allergies: {'allergies': ['penicillin'], 'chronic_conditions': ['hypertension']}"
    )
    
    # Advanced Specialist Hospital Diagnostic Modalities
    anamnesis = models.JSONField(
        default=dict, blank=True,
        help_text="Oral history taken by mouth: {'chief_complaint': 'chest pain', 'onset': 'acute', 'duration_hours': 2, 'character': 'crushing', 'radiation': 'left_arm', 'travel_history': 'none'}"
    )
    physical_exam = models.JSONField(
        default=dict, blank=True,
        help_text="Doctor's physical exam: {'cardiovascular': ['systolic_murmur'], 'respiratory': ['crackles'], 'abdominal': ['mcburney_tenderness'], 'neuro': ['neck_stiffness']}"
    )
    laboratory_results = models.JSONField(
        default=dict, blank=True,
        help_text="Tested by laboratory: {'troponin_i': 1.8, 'wbc_count': 16500, 'blood_glucose': 240, 'creatinine': 1.4, 'crp': 85, 'malaria_smear': 'positive', 'urine_ketones': 'positive'}"
    )
    diagnostic_tools = models.JSONField(
        default=dict, blank=True,
        help_text="Diagnostic & bedside tools: {'ecg': 'st_elevation_v1_v4', 'chest_xray': 'lobar_consolidation', 'ct_head': 'ischemic_infarct', 'ultrasound_pocus': 'gallstones'}"
    )
    
    # ML & Inference Engine Metadata
    engine_version = models.CharField(
        max_length=100, default='Hybrid-AI-CDSS-v2.5',
        help_text="Inference engine descriptor (e.g. Hybrid Random Forest + Bayesian Likelihood)"
    )
    model_version = models.CharField(max_length=50, default='v2.5-core50')
    triage_level = models.CharField(
        max_length=30, choices=TriageLevel.choices, default=TriageLevel.LESS_URGENT
    )
    processing_status = models.CharField(
        max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.COMPLETED
    )
    processing_time_ms = models.IntegerField(default=0, help_text="Inference execution time in milliseconds")
    error_message = models.TextField(blank=True)
    
    # User / Clinician requesting inference
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='decision_support_requests'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='decision_requests_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='decision_requests_updated'
    )

    class Meta:
        db_table = 'decision_support_request'
        verbose_name = 'CDSS Diagnostic Request'
        verbose_name_plural = 'CDSS Diagnostic Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['processing_status']),
            models.Index(fields=['triage_level']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"CDSS Request {str(self.id)[:8]} ({self.get_triage_level_display()})"


class DecisionSupportCandidate(models.Model):
    """
    Ranked differential diagnosis candidate produced by the ML diagnostic engine
    for a given clinical presentation. Includes probability score, supporting/contradicting
    signs, red flags, recommended investigations, treatment regimens, and clinician review.
    """
    
    class ConfidenceLevel(models.TextChoices):
        HIGH = 'high', 'High Confidence (>75%)'
        MODERATE = 'moderate', 'Moderate Confidence (50%-75%)'
        LOW = 'low', 'Low / Possible (25%-49%)'
        UNCERTAIN = 'uncertain', 'Uncertain / Rare Consideration (<25%)'

    class ClinicianDecision(models.TextChoices):
        CONFIRMED = 'confirmed', 'Clinically Confirmed'
        REJECTED = 'rejected', 'Clinically Ruled Out'
        DEFERRED = 'deferred', 'Deferred Pending Diagnostic Tests'
        REQUIRES_INVESTIGATION = 'requires_investigation', 'Requires Lab/Imaging Workup'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        DecisionSupportRequest, on_delete=models.CASCADE, related_name='candidates'
    )
    disease = models.ForeignKey(
        'medical_knowledge.Disease', on_delete=models.CASCADE, related_name='candidate_diagnoses'
    )
    
    # ML Scoring
    rank = models.IntegerField(help_text="Position in differential diagnosis ranking (1 = most probable)")
    probability_score = models.FloatField(default=0.0, help_text="Calibrated diagnostic probability (0.0 to 1.0)")
    confidence_level = models.CharField(
        max_length=20, choices=ConfidenceLevel.choices, default=ConfidenceLevel.MODERATE
    )
    
    # Clinical Explainability & Findings
    supporting_findings = models.JSONField(
        default=list,
        help_text="Matching signs & symptoms that strongly support this diagnosis"
    )
    contradicting_findings = models.JSONField(
        default=list,
        help_text="Clinical findings that argue against this diagnosis"
    )
    missing_information = models.JSONField(
        default=list,
        help_text="Pertinent signs/symptoms to check to verify this diagnosis"
    )
    red_flags = models.JSONField(
        default=list,
        help_text="Severe warning indicators or danger signs associated with this candidate"
    )
    
    # Recommendations
    suggested_investigations = models.JSONField(
        default=list,
        help_text="Recommended confirmatory laboratory, imaging, or bedside tests"
    )
    recommended_treatments = models.JSONField(
        default=list,
        help_text="Evidence-based first-line and supportive medications"
    )
    contraindication_alerts = models.JSONField(
        default=list,
        help_text="Alerts for drug-drug interactions or allergies against patient history"
    )
    
    # Clinician Oversight & Active Learning Loop
    clinician_decision = models.CharField(
        max_length=30, choices=ClinicianDecision.choices, blank=True, null=True
    )
    clinician_feedback = models.TextField(blank=True, help_text="Physician notes, rationale, or diagnostic comments")
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='candidate_diagnoses_decided'
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'decision_support_candidate'
        verbose_name = 'Diagnostic Candidate'
        verbose_name_plural = 'Diagnostic Candidates'
        ordering = ['rank']
        indexes = [
            models.Index(fields=['request', 'rank']),
            models.Index(fields=['disease']),
            models.Index(fields=['confidence_level']),
        ]

    def __str__(self):
        return f"#{self.rank} {self.disease.name} ({round(self.probability_score*100, 1)}%)"
