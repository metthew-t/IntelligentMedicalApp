"""
Tests for Medical Knowledge Module.
Validates Disease, Symptom, Medicine, DrugInteraction, and Treatment models & APIs.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)


class MedicalKnowledgeModelTestCase(TestCase):
    """Test case for medical knowledge models."""

    def setUp(self):
        self.client = APIClient()
        self.disease = Disease.objects.create(
            name="Test Malaria Condition",
            category=Disease.Category.INFECTIOUS,
            icd10_code="B50.0",
            definition="Test infectious condition caused by protozoa.",
            status="active",
            is_active=True
        )
        self.symptom_fever = Symptom.objects.create(
            name="Test Fever",
            symptom_type=Symptom.SymptomType.BOTH,
            body_system=Symptom.BodySystem.GENERAL,
            is_red_flag=False,
            severity_weight=1.5,
            is_active=True
        )
        self.sign_spleno = Symptom.objects.create(
            name="Test Splenomegaly",
            symptom_type=Symptom.SymptomType.SIGN,
            body_system=Symptom.BodySystem.GENERAL,
            is_red_flag=False,
            severity_weight=1.8,
            is_active=True
        )
        self.link = DiseaseSymptom.objects.create(
            disease=self.disease,
            symptom=self.symptom_fever,
            frequency=DiseaseSymptom.Frequency.VERY_COMMON,
            specificity=DiseaseSymptom.Specificity.HIGHLY_SPECIFIC,
            is_hallmark=True
        )
        self.med_a = Medicine.objects.create(
            generic_name="Test Artemether",
            drug_class="Antimalarial",
            dosage_form=Medicine.DosageForm.TABLET,
            route_of_administration=Medicine.Route.ORAL,
            is_active=True
        )
        self.med_b = Medicine.objects.create(
            generic_name="Test Azithromycin",
            drug_class="Macrolide",
            dosage_form=Medicine.DosageForm.TABLET,
            route_of_administration=Medicine.Route.ORAL,
            is_active=True
        )
        self.interaction = DrugInteraction.objects.create(
            medicine_a=self.med_a,
            medicine_b=self.med_b,
            severity=DrugInteraction.Severity.MAJOR,
            interaction_type=DrugInteraction.InteractionType.PHARMACODYNAMIC,
            description="QT prolongation risk"
        )
        self.treatment = DiseaseTreatment.objects.create(
            disease=self.disease,
            medicine=self.med_a,
            treatment_line=DiseaseTreatment.TreatmentLine.FIRST_LINE,
            regimen_instructions="Take with food for 3 days."
        )

    def test_disease_creation(self):
        """Test disease model properties and hallmark associations."""
        self.assertEqual(str(self.disease), "Test Malaria Condition (B50.0)")
        self.assertEqual(self.disease.disease_symptoms.count(), 1)
        self.assertTrue(self.disease.disease_symptoms.first().is_hallmark)

    def test_symptom_and_numerical_weight(self):
        """Test symptom classification and computed heuristic weight."""
        self.assertEqual(self.symptom_fever.symptom_type, "both")
        self.assertEqual(self.sign_spleno.symptom_type, "sign")
        # Numerical weight calculation
        weight = self.link.numerical_weight
        self.assertGreater(weight, 1.0)

    def test_medicine_and_interaction(self):
        """Test medicine catalog and interaction severity."""
        self.assertEqual(self.interaction.severity, "major")
        self.assertEqual(self.treatment.treatment_line, "first_line")

    def test_api_disease_list(self):
        """Test GET /api/v1/medical-knowledge/diseases/"""
        response = self.client.get('/api/v1/medical-knowledge/diseases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_symptom_list_and_filter(self):
        """Test GET /api/v1/medical-knowledge/symptoms/ with type filter."""
        response = self.client.get('/api/v1/medical-knowledge/symptoms/?symptom_type=sign')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_check_drug_interactions(self):
        """Test POST /api/v1/medical-knowledge/drug-interactions/check/"""
        payload = {
            "medicine_ids": [str(self.med_a.id), str(self.med_b.id)]
        }
        response = self.client.post('/api/v1/medical-knowledge/drug-interactions/check/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['interactions'][0]['severity'], 'major')
