"""
Tests for Clinical Decision Support System (CDSS) and ML Diagnostic Engine.
Validates Diagnostic Engine, Triage, API Endpoints, and Clinician Feedback Loop.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.medical_knowledge.models import Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
from apps.decision_support.models import DecisionSupportRequest, DecisionSupportCandidate
from apps.decision_support.ml_engine import HybridDiagnosticEngine


class DecisionSupportTestCase(TestCase):
    """Test suite for Decision Support ML Engine and API."""

    def setUp(self):
        self.client = APIClient()
        self.engine = HybridDiagnosticEngine()

        # Seed test disease
        self.disease_meningitis = Disease.objects.create(
            name="Acute Bacterial Meningitis",
            category=Disease.Category.INFECTIOUS,
            icd10_code="G00.9",
            definition="Acute bacterial infection of meninges.",
            management_overview="Empiric IV antibiotics immediately.",
            status="active",
            is_active=True
        )

        # Seed test symptoms/signs
        self.sym_fever = Symptom.objects.create(
            name="High Fever (>38.5°C)",
            symptom_type=Symptom.SymptomType.BOTH,
            body_system=Symptom.BodySystem.GENERAL,
            is_red_flag=False,
            severity_weight=1.4,
            is_active=True
        )
        self.sign_neck = Symptom.objects.create(
            name="Nuchal Rigidity (Neck Stiffness)",
            symptom_type=Symptom.SymptomType.SIGN,
            body_system=Symptom.BodySystem.NEUROLOGICAL,
            is_red_flag=True,
            severity_weight=2.5,
            is_active=True
        )
        self.sym_headache = Symptom.objects.create(
            name="Severe Throbbing Headache",
            symptom_type=Symptom.SymptomType.SYMPTOM,
            body_system=Symptom.BodySystem.NEUROLOGICAL,
            is_red_flag=False,
            severity_weight=1.3,
            is_active=True
        )

        # Link symptoms
        DiseaseSymptom.objects.create(
            disease=self.disease_meningitis,
            symptom=self.sym_fever,
            frequency=DiseaseSymptom.Frequency.VERY_COMMON,
            specificity=DiseaseSymptom.Specificity.MODERATELY_SPECIFIC
        )
        DiseaseSymptom.objects.create(
            disease=self.disease_meningitis,
            symptom=self.sign_neck,
            frequency=DiseaseSymptom.Frequency.VERY_COMMON,
            specificity=DiseaseSymptom.Specificity.PATHOGNOMONIC,
            is_hallmark=True
        )

        # Seed treatment and medicine
        self.medicine_ceftriaxone = Medicine.objects.create(
            generic_name="Ceftriaxone",
            drug_class="Cephalosporin",
            dosage_form=Medicine.DosageForm.INJECTION,
            route_of_administration=Medicine.Route.IV,
            indications=["Bacterial Meningitis"],
            contraindications=["Cephalosporin allergy"],
            is_active=True
        )
        DiseaseTreatment.objects.create(
            disease=self.disease_meningitis,
            medicine=self.medicine_ceftriaxone,
            treatment_line=DiseaseTreatment.TreatmentLine.FIRST_LINE,
            regimen_instructions="2 g IV twice daily for 14 days."
        )

    def test_hybrid_engine_diagnostic_inference(self):
        """Test diagnostic prediction and red flag detection in ML engine."""
        result = self.engine.run_inference(
            symptoms=[{'name': 'High Fever (>38.5°C)'}, {'name': 'Severe Throbbing Headache'}],
            signs=[{'name': 'Nuchal Rigidity (Neck Stiffness)'}],
            vital_signs={'temperature': 39.5, 'heart_rate': 110},
            demographics={'age': 20, 'gender': 'male'},
            medical_history={}
        )

        self.assertGreater(len(result['candidates']), 0)
        top_cand = result['candidates'][0]
        self.assertEqual(top_cand['disease_name'], "Acute Bacterial Meningitis")
        self.assertEqual(result['triage_level'], "resuscitation")
        self.assertGreater(len(result['red_flags']), 0)

    def test_api_diagnose_endpoint(self):
        """Test POST /api/v1/decision-support/diagnose/ endpoint."""
        payload = {
            "symptoms": [{"name": "High Fever (>38.5°C)"}],
            "signs": [{"name": "Nuchal Rigidity (Neck Stiffness)"}],
            "vital_signs": {
                "temperature": 39.2,
                "heart_rate": 105,
                "spo2": 96
            },
            "demographics": {
                "age": 22,
                "gender": "female"
            },
            "medical_history": {}
        }
        response = self.client.post('/api/v1/decision-support/diagnose/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('candidates', response.data)
        self.assertGreater(len(response.data['candidates']), 0)
        self.assertEqual(response.data['candidates'][0]['disease_name'], "Acute Bacterial Meningitis")

    def test_api_candidate_feedback(self):
        """Test clinician feedback loop on diagnostic candidate."""
        req = DecisionSupportRequest.objects.create(
            patient_demographics={"age": 22},
            symptoms=[{"name": "High Fever (>38.5°C)"}],
            signs=[],
            vital_signs={},
            engine_version="Hybrid-AI-v2.5",
            triage_level="urgent"
        )
        candidate = DecisionSupportCandidate.objects.create(
            request=req,
            disease=self.disease_meningitis,
            rank=1,
            probability_score=0.88,
            confidence_level="high",
            supporting_findings=[]
        )

        payload = {
            "decision": "confirmed",
            "feedback": "Confirmed on lumbar puncture with elevated opening pressure and CSF pleocytosis."
        }
        response = self.client.post(
            f'/api/v1/decision-support/candidates/{candidate.id}/feedback/',
            payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        candidate.refresh_from_db()
        self.assertEqual(candidate.clinician_decision, "confirmed")
        self.assertIn("lumbar puncture", candidate.clinician_feedback)

    def test_web_cdss_dashboard_view(self):
        """Test GET /cdss/ and / web dashboard rendering."""
        response = self.client.get('/cdss/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Clinical Decision Support System (CDSS)")
        self.assertContains(response, "52,500+")

    def test_ml_model_status_api(self):
        """Test GET /api/v1/decision-support/ml-model-status/ endpoint."""
        response = self.client.get('/api/v1/decision-support/ml-model-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data.get('is_available') is not False:
            self.assertIn('total_samples', response.data)
            self.assertGreaterEqual(response.data['total_samples'], 50000)
            self.assertIn('test_top1_accuracy', response.data)
            self.assertIn('test_top3_accuracy', response.data)

    def test_trained_model_predictor_integration(self):
        """Test TrainedModelPredictor availability and feature vector generation."""
        from apps.decision_support.ml_engine.model_trainer import TrainedModelPredictor
        predictor = TrainedModelPredictor()
        if predictor.is_available:
            self.assertGreaterEqual(predictor.metrics.get('total_samples', 0), 50000)
            probas = predictor.predict(
                symptoms=['High Fever (>38.5°C)'],
                signs=['Splenomegaly'],
                vitals={'temperature': 39.2, 'heart_rate': 105},
                demographics={'age': 25, 'gender': 'female'}
            )
            self.assertIsInstance(probas, dict)
            self.assertGreater(len(probas), 0)
