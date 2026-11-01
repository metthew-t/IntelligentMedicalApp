"""
Views and API ViewSets for Clinical Decision Support System (CDSS).
Provides diagnostic inference, symptom checking, emergency triage, and clinician feedback.
"""
import time
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.decision_support.models import DecisionSupportRequest, DecisionSupportCandidate
from apps.decision_support.serializers import (
    DiagnosticInputSerializer,
    DecisionSupportRequestSerializer,
    DecisionSupportCandidateSerializer,
    ClinicianFeedbackSerializer
)
from apps.decision_support.ml_engine import HybridDiagnosticEngine
from apps.medical_knowledge.models import Disease


class DecisionSupportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Clinical Decision Support and Machine Learning Diagnostics.
    """
    queryset = DecisionSupportRequest.objects.prefetch_related(
        'candidates__disease'
    ).all().order_by('-created_at')
    serializer_class = DecisionSupportRequestSerializer
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = HybridDiagnosticEngine()

    @action(detail=False, methods=['post'], url_path='diagnose')
    def diagnose(self, request):
        """
        Primary Diagnostic Endpoint:
        Executes hybrid ML diagnostic inference based on presenting symptoms,
        physical exam signs, vital signs, demographics, and medical history.
        Saves the diagnostic snapshot and candidates in the database for clinical auditing.
        """
        serializer = DiagnosticInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start_time = time.time()

        symptoms = data.get('symptoms', [])
        signs = data.get('signs', [])
        vital_signs = data.get('vital_signs', {})
        demographics = data.get('demographics', {})
        medical_history = data.get('medical_history', {})
        anamnesis = data.get('anamnesis', {})
        physical_exam = data.get('physical_exam', {})
        laboratory_results = data.get('laboratory_results', {})
        diagnostic_tools = data.get('diagnostic_tools', {})

        # Run hybrid inference engine
        inference_result = self.engine.run_inference(
            symptoms=symptoms,
            signs=signs,
            vital_signs=vital_signs,
            demographics=demographics,
            medical_history=medical_history,
            anamnesis=anamnesis,
            physical_exam=physical_exam,
            laboratory_results=laboratory_results,
            diagnostic_tools=diagnostic_tools
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Record in database
        user = request.user if request.user and request.user.is_authenticated else None

        req_record = DecisionSupportRequest.objects.create(
            patient_demographics=demographics,
            symptoms=symptoms,
            signs=signs,
            vital_signs=vital_signs,
            medical_history=medical_history,
            anamnesis=anamnesis,
            physical_exam=physical_exam,
            laboratory_results=laboratory_results,
            diagnostic_tools=diagnostic_tools,
            engine_version=inference_result['engine_version'],
            model_version=inference_result['model_version'],
            triage_level=inference_result['triage_level'],
            processing_status=DecisionSupportRequest.ProcessingStatus.COMPLETED,
            processing_time_ms=elapsed_ms,
            requested_by=user,
            created_by=user,
            updated_by=user
        )

        candidates_to_create = []
        for c in inference_result['candidates']:
            try:
                disease = Disease.objects.get(id=c['disease_id'])
                candidate_obj = DecisionSupportCandidate(
                    request=req_record,
                    disease=disease,
                    rank=c['rank'],
                    probability_score=c['probability_score'],
                    confidence_level=c['confidence_level'],
                    supporting_findings=c['supporting_findings'],
                    contradicting_findings=c.get('contradicting_findings', []),
                    missing_information=c.get('missing_information', []),
                    red_flags=inference_result['red_flags'],
                    suggested_investigations=c.get('suggested_investigations', []),
                    recommended_treatments=c.get('recommended_treatments', []),
                    contraindication_alerts=c.get('contraindication_alerts', [])
                )
                candidates_to_create.append(candidate_obj)
            except Disease.DoesNotExist:
                continue

        if candidates_to_create:
            DecisionSupportCandidate.objects.bulk_create(candidates_to_create)

        # Return full response
        full_serializer = DecisionSupportRequestSerializer(req_record)
        response_data = full_serializer.data
        response_data['red_flags'] = inference_result['red_flags']
        response_data['ml_model_status'] = inference_result.get('ml_model_status', {})

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='quick-check')
    def quick_check(self, request):
        """
        Fast in-memory symptom & sign check for real-time differential ranking.
        Does not persist to database.
        """
        serializer = DiagnosticInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start_time = time.time()

        inference_result = self.engine.run_inference(
            symptoms=data.get('symptoms', []),
            signs=data.get('signs', []),
            vital_signs=data.get('vital_signs', {}),
            demographics=data.get('demographics', {}),
            medical_history=data.get('medical_history', {}),
            anamnesis=data.get('anamnesis', {}),
            physical_exam=data.get('physical_exam', {}),
            laboratory_results=data.get('laboratory_results', {}),
            diagnostic_tools=data.get('diagnostic_tools', {})
        )

        inference_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
        return Response(inference_result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='candidates/(?P<candidate_id>[^/.]+)/feedback')
    def candidate_feedback(self, request, candidate_id=None):
        """
        Allows clinician to record diagnostic feedback on a specific candidate
        (Confirmed, Rejected, Deferred, Requires Workup) for clinical safety & ML active learning.
        """
        try:
            candidate = DecisionSupportCandidate.objects.get(id=candidate_id)
        except DecisionSupportCandidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClinicianFeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        decision = serializer.validated_data['decision']
        feedback = serializer.validated_data.get('feedback', '')

        candidate.clinician_decision = decision
        candidate.clinician_feedback = feedback
        candidate.decided_by = request.user if request.user and request.user.is_authenticated else None
        candidate.decided_at = timezone.now()
        candidate.save(update_fields=['clinician_decision', 'clinician_feedback', 'decided_by', 'decided_at'])

        return Response(DecisionSupportCandidateSerializer(candidate).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Returns analytics on diagnostic activity, top predicted conditions,
        and clinician confirmation rate.
        """
        total_requests = DecisionSupportRequest.objects.count()
        total_candidates = DecisionSupportCandidate.objects.count()
        confirmed_count = DecisionSupportCandidate.objects.filter(clinician_decision='confirmed').count()
        rejected_count = DecisionSupportCandidate.objects.filter(clinician_decision='rejected').count()

        # Top 5 most frequently predicted top diagnoses
        top_diagnoses = []
        top_candidates = DecisionSupportCandidate.objects.filter(rank=1).values('disease__name').distinct()[:5]
        for item in top_candidates:
            d_name = item['disease__name']
            count = DecisionSupportCandidate.objects.filter(rank=1, disease__name=d_name).count()
            top_diagnoses.append({'disease': d_name, 'count': count})

        return Response({
            'total_diagnostic_inferences': total_requests,
            'total_candidates_generated': total_candidates,
            'clinician_confirmed_diagnoses': confirmed_count,
            'clinician_rejected_diagnoses': rejected_count,
            'top_first_line_diagnoses': top_diagnoses,
            'ml_model_status': self.engine.predictor.metrics if (self.engine.predictor and self.engine.predictor.is_available) else {'is_available': False}
        })

    @action(detail=False, methods=['get'], url_path='ml-model-status')
    def ml_model_status(self, request):
        """
        Returns machine learning model training metadata, sample size (50,000+),
        top accuracy metrics, and top predictive features.
        """
        if self.engine.predictor and self.engine.predictor.is_available:
            return Response(self.engine.predictor.metrics, status=status.HTTP_200_OK)
        return Response({
            'is_available': False,
            'message': 'ML Model not yet trained. Run `python manage.py train_medical_ai` to train on 52,500 patient encounters.'
        }, status=status.HTTP_200_OK)
