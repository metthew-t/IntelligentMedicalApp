"""
Medical Knowledge Models for the Intelligent Medical System.
Covers Diseases, Symptoms, Physical Signs, Disease-Symptom associations,
Medicines, Drug Interactions, and Evidence-based Treatment Regimens.
"""
import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel, VersionedContentModel


class Disease(VersionedContentModel):
    """
    Comprehensive Disease entity representing clinical conditions,
    diagnoses, ICD-10/11 mappings, etiology, clinical features, and management protocols.
    """
    
    class Category(models.TextChoices):
        INFECTIOUS = 'infectious', 'Infectious & Parasitic Diseases'
        RESPIRATORY = 'respiratory', 'Respiratory Diseases'
        CARDIOVASCULAR = 'cardiovascular', 'Cardiovascular Diseases'
        GASTROINTESTINAL = 'gastrointestinal', 'Gastrointestinal & Liver'
        ENDOCRINE = 'endocrine', 'Endocrine & Metabolic'
        NEUROLOGICAL = 'neurological', 'Neurological Disorders'
        GENITOURINARY = 'genitourinary', 'Renal & Genitourinary'
        HEMATOLOGY = 'hematology', 'Hematology & Oncology'
        MUSCULOSKELETAL = 'musculoskeletal', 'Musculoskeletal & Autoimmune'
        DERMATOLOGICAL = 'dermatological', 'Dermatological'
        EMERGENCY = 'emergency', 'Trauma & Acute Emergency'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=255, db_index=True, help_text="Disease common name")
    name_local = models.JSONField(
        default=dict, blank=True,
        help_text="Local names in Amharic, Afaan Oromo, Tigrinya, etc. Example: {'am': 'ወባ', 'om': 'Busaa'}"
    )
    synonyms = models.JSONField(
        default=list, blank=True,
        help_text="List of synonyms or alternative clinical names"
    )
    category = models.CharField(
        max_length=50, choices=Category.choices, default=Category.INFECTIOUS, db_index=True
    )
    icd10_code = models.CharField(max_length=20, blank=True, db_index=True, help_text="ICD-10-CM code")
    icd11_code = models.CharField(max_length=20, blank=True, db_index=True, help_text="ICD-11 code")
    
    # Clinical Descriptions
    definition = models.TextField(help_text="Concise clinical definition of the disease")
    etiology = models.TextField(blank=True, help_text="Causative agents, pathophysiology, or mechanism")
    risk_factors = models.JSONField(default=list, blank=True, help_text="List of identifiable clinical or demographic risk factors")
    complications = models.JSONField(default=list, blank=True, help_text="List of potential acute or chronic complications")
    typical_age_group = models.CharField(max_length=100, blank=True, help_text="e.g., All ages, Pediatric (<5 years), Adults >40")
    
    # Diagnostic Criteria
    diagnostic_criteria = models.JSONField(
        default=dict, blank=True,
        help_text="Structured diagnostic criteria (major criteria, minor criteria, required lab/imaging tests)"
    )
    
    # Clinical Management
    management_overview = models.TextField(blank=True, help_text="General management and therapeutic goals")
    prevention_guidance = models.TextField(blank=True, help_text="Vaccines, lifestyle, hygiene, or prophylactic measures")
    referral_criteria = models.TextField(blank=True, help_text="Criteria for immediate referral to higher level health facility")
    
    # Provenance
    source_organization = models.CharField(max_length=255, default='WHO / Ethiopian Ministry of Health')
    source_url = models.URLField(max_length=500, blank=True)
    source_version = models.CharField(max_length=50, default='STG-2024')
    jurisdiction = models.CharField(max_length=50, default='Ethiopia / Global')

    # Audit FK override to allow nullable for system/seed data
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='diseases_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='diseases_updated'
    )

    class Meta:
        db_table = 'medical_knowledge_disease'
        verbose_name = 'Disease'
        verbose_name_plural = 'Diseases'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['icd10_code']),
            models.Index(fields=['status', 'is_active']),
        ]

    def __str__(self):
        icd = f" ({self.icd10_code})" if self.icd10_code else ""
        return f"{self.name}{icd}"

    @property
    def hallmark_symptoms(self):
        """Returns symptoms/signs marked as hallmark or pathognomonic for this disease."""
        return self.disease_symptoms.filter(
            models.Q(specificity__in=['pathognomonic', 'highly_specific']) | models.Q(is_hallmark=True),
            is_active=True
        ).select_related('symptom')


class Symptom(BaseModel):
    """
    Symptom or Physical Sign entity.
    Distinguishes subjective patient Symptoms from objective clinician Signs (and signs/symptoms that present as both).
    """
    
    class SymptomType(models.TextChoices):
        SYMPTOM = 'symptom', 'Symptom (Subjective finding reported by patient)'
        SIGN = 'sign', 'Sign (Objective finding detected during physical exam)'
        BOTH = 'both', 'Both (Can be reported and clinically observed)'

    class BodySystem(models.TextChoices):
        GENERAL = 'general', 'General / Systemic / Constitutional'
        RESPIRATORY = 'respiratory', 'Respiratory System'
        CARDIOVASCULAR = 'cardiovascular', 'Cardiovascular System'
        GASTROINTESTINAL = 'gastrointestinal', 'Gastrointestinal System'
        NEUROLOGICAL = 'neurological', 'Nervous System & Mental State'
        DERMATOLOGICAL = 'dermatological', 'Integumentary / Skin'
        GENITOURINARY = 'genitourinary', 'Renal & Genitourinary'
        MUSCULOSKELETAL = 'musculoskeletal', 'Musculoskeletal'
        ENT = 'ent', 'Ear, Nose & Throat (ENT)'
        OPHTHALMIC = 'ophthalmic', 'Ophthalmic / Eyes'
        HEMATOLOGIC = 'hematologic', 'Hematologic / Lymphatic'

    name = models.CharField(max_length=200, db_index=True, unique=True, help_text="Standard medical name")
    name_local = models.JSONField(
        default=dict, blank=True,
        help_text="Local names in Amharic, Oromo, etc. Example: {'am': 'ትኩሳት', 'om': 'Ho’aa qaamaa'}"
    )
    synonyms = models.JSONField(
        default=list, blank=True,
        help_text="Common lay terms or synonyms, e.g. ['fever', 'high temperature', 'febrile']"
    )
    description = models.TextField(blank=True, help_text="Clinical definition, characteristics, and assessment instructions")
    category = models.CharField(max_length=100, blank=True)
    body_system = models.CharField(
        max_length=50, choices=BodySystem.choices, default=BodySystem.GENERAL, db_index=True
    )
    symptom_type = models.CharField(
        max_length=20, choices=SymptomType.choices, default=SymptomType.SYMPTOM, db_index=True
    )
    snomed_code = models.CharField(max_length=50, blank=True, help_text="SNOMED CT Concept ID")
    icon_name = models.CharField(max_length=50, blank=True, default='medical_services')
    
    # Clinical Safety & Triage
    is_red_flag = models.BooleanField(
        default=False, db_index=True,
        help_text="True if this sign/symptom represents a critical clinical danger sign requiring immediate triage"
    )
    severity_weight = models.FloatField(
        default=1.0,
        help_text="Baseline weight for differential diagnosis heuristic and ML vectorization"
    )
    
    # Audit FK override
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='symptoms_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='symptoms_updated'
    )

    class Meta:
        db_table = 'medical_knowledge_symptom'
        verbose_name = 'Symptom & Sign'
        verbose_name_plural = 'Symptoms & Signs'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['body_system']),
            models.Index(fields=['symptom_type']),
            models.Index(fields=['is_red_flag']),
        ]

    def __str__(self):
        stype = "Sign" if self.symptom_type == 'sign' else ("Symptom" if self.symptom_type == 'symptom' else "Sign/Symptom")
        flag = " [RED FLAG]" if self.is_red_flag else ""
        return f"{self.name} ({stype}){flag}"


class DiseaseSymptom(models.Model):
    """
    Association between a Disease and a Symptom or Sign.
    Stores clinical frequency, diagnostic specificity, stage of presentation, and diagnostic weights.
    """
    
    class Frequency(models.TextChoices):
        VERY_COMMON = 'very_common', 'Very Common (>80% of cases)'
        COMMON = 'common', 'Common (50% - 80% of cases)'
        OCCASIONAL = 'occasional', 'Occasional (20% - 49% of cases)'
        RARE = 'rare', 'Rare (<20% of cases)'

    class Specificity(models.TextChoices):
        PATHOGNOMONIC = 'pathognomonic', 'Pathognomonic (Conclusive hallmark)'
        HIGHLY_SPECIFIC = 'highly_specific', 'Highly Specific'
        MODERATELY_SPECIFIC = 'moderately_specific', 'Moderately Specific'
        NON_SPECIFIC = 'non_specific', 'Non-Specific'

    class Stage(models.TextChoices):
        EARLY = 'early', 'Early / Prodromal'
        MID = 'mid', 'Established / Active'
        LATE = 'late', 'Late / Complicated'
        ANY = 'any', 'Any Stage'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease = models.ForeignKey(
        Disease, on_delete=models.CASCADE, related_name='disease_symptoms'
    )
    symptom = models.ForeignKey(
        Symptom, on_delete=models.CASCADE, related_name='disease_associations'
    )
    
    frequency = models.CharField(
        max_length=20, choices=Frequency.choices, default=Frequency.COMMON
    )
    specificity = models.CharField(
        max_length=30, choices=Specificity.choices, default=Specificity.MODERATELY_SPECIFIC
    )
    stage = models.CharField(
        max_length=20, choices=Stage.choices, default=Stage.ANY
    )
    is_hallmark = models.BooleanField(
        default=False, help_text="True if this is a cardinal / key diagnostic hallmark sign for this disease"
    )
    notes = models.TextField(blank=True, help_text="Clinical nuances, e.g., 'characteristically relapsing every 48 hours'")
    evidence_level = models.CharField(max_length=10, default='A', help_text="Grade of clinical evidence (A, B, C)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medical_knowledge_diseasesymptom'
        verbose_name = 'Disease Symptom/Sign Link'
        verbose_name_plural = 'Disease Symptom/Sign Links'
        unique_together = ('disease', 'symptom')
        indexes = [
            models.Index(fields=['disease', 'symptom']),
            models.Index(fields=['frequency']),
            models.Index(fields=['specificity']),
        ]

    def __str__(self):
        return f"{self.disease.name} -> {self.symptom.name} ({self.get_frequency_display()})"

    @property
    def numerical_weight(self):
        """Computes heuristic Bayesian likelihood weight for ML scoring."""
        freq_weights = {
            'very_common': 1.0,
            'common': 0.75,
            'occasional': 0.40,
            'rare': 0.15,
        }
        spec_multipliers = {
            'pathognomonic': 3.5,
            'highly_specific': 2.0,
            'moderately_specific': 1.2,
            'non_specific': 0.8,
        }
        f_val = freq_weights.get(self.frequency, 0.5)
        s_val = spec_multipliers.get(self.specificity, 1.0)
        return round(f_val * s_val * self.symptom.severity_weight, 3)


class Medicine(BaseModel):
    """
    Standardized pharmaceutical medicine catalog with drug classes, dosage formulations,
    indications, contraindications, and safety guidelines.
    """
    
    class DosageForm(models.TextChoices):
        TABLET = 'tablet', 'Tablet'
        CAPSULE = 'capsule', 'Capsule'
        SYRUP = 'syrup', 'Syrup'
        SUSPENSION = 'suspension', 'Suspension'
        INJECTION = 'injection', 'Injection'
        INFUSION = 'infusion', 'IV Infusion'
        OINTMENT = 'ointment', 'Ointment'
        CREAM = 'cream', 'Cream'
        DROPS = 'drops', 'Drops'
        INHALER = 'inhaler', 'Inhaler / Nebulizer'
        SUPPOSITORY = 'suppository', 'Suppository'
        OTHER = 'other', 'Other'

    class Route(models.TextChoices):
        ORAL = 'oral', 'Oral'
        IV = 'iv', 'Intravenous (IV)'
        IM = 'im', 'Intramuscular (IM)'
        SUBCUTANEOUS = 'subcutaneous', 'Subcutaneous (SC)'
        INHALATION = 'inhalation', 'Inhalation'
        TOPICAL = 'topical', 'Topical'
        RECTAL = 'rectal', 'Rectal'
        OPHTHALMIC = 'ophthalmic', 'Ophthalmic'
        OTHER = 'other', 'Other'

    generic_name = models.CharField(max_length=255, db_index=True, help_text="International Nonproprietary Name (INN)")
    brand_names = models.JSONField(default=list, blank=True, help_text="Common brand names")
    local_names = models.JSONField(default=dict, blank=True)
    drug_class = models.CharField(max_length=100, db_index=True, help_text="Pharmacological class, e.g. Fluoroquinolone, Beta-blocker")
    atc_code = models.CharField(max_length=20, blank=True, db_index=True, help_text="Anatomical Therapeutic Chemical (ATC) code")
    
    dosage_form = models.CharField(max_length=50, choices=DosageForm.choices, default=DosageForm.TABLET)
    strength = models.CharField(max_length=100, blank=True, help_text="e.g. 500 mg, 20 mg/120 mg")
    unit = models.CharField(max_length=50, blank=True, help_text="mg, ml, mcg, IU")
    route_of_administration = models.CharField(max_length=50, choices=Route.choices, default=Route.ORAL)
    
    # Clinical Guidance
    indications = models.JSONField(default=list, blank=True, help_text="List of clinical indications")
    contraindications = models.JSONField(default=list, blank=True, help_text="List of absolute and relative contraindications")
    warnings = models.JSONField(default=list, blank=True, help_text="Black box warnings and precautions")
    adverse_reactions = models.JSONField(default=list, blank=True, help_text="Common and serious adverse reactions")
    pregnancy_category = models.CharField(max_length=5, blank=True, help_text="FDA Pregnancy Category: A, B, C, D, X")
    breastfeeding_safety = models.CharField(max_length=100, blank=True)
    
    # Dosing Guidelines
    adult_dosing = models.TextField(blank=True, help_text="Standard adult dosage and frequency")
    pediatric_dosing = models.TextField(blank=True, help_text="Pediatric dosage (weight-based mg/kg/day)")
    renal_adjustment = models.TextField(blank=True, help_text="Dosing adjustment for renal impairment (eGFR / CrCl)")
    hepatic_adjustment = models.TextField(blank=True, help_text="Dosing adjustment for hepatic impairment")
    maximum_dose = models.CharField(max_length=200, blank=True)
    
    # Essential Drug List status
    is_essential_medicine = models.BooleanField(default=True, help_text="Part of National Essential Medicines List (NEML)")
    formulary_status = models.CharField(max_length=50, default='General Formulary')
    restricted = models.BooleanField(default=False, help_text="Requires specialist authorization")

    # Audit FK override
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='medicines_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='medicines_updated'
    )

    class Meta:
        db_table = 'medical_knowledge_medicine'
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'
        ordering = ['generic_name']
        indexes = [
            models.Index(fields=['generic_name']),
            models.Index(fields=['drug_class']),
            models.Index(fields=['atc_code']),
        ]

    def __str__(self):
        strength_str = f" {self.strength}" if self.strength else ""
        return f"{self.generic_name}{strength_str} ({self.get_dosage_form_display()})"


class DrugInteraction(models.Model):
    """
    Documented clinical interaction between two medicines with severity rating and management guidance.
    """
    
    class Severity(models.TextChoices):
        CONTRAINDICATED = 'contraindicated', 'Contraindicated (Do Not Co-administer / Life-Threatening)'
        MAJOR = 'major', 'Major Interaction (Significant clinical risk, consider alternatives)'
        MODERATE = 'moderate', 'Moderate Interaction (Monitor patient and adjust dosing)'
        MINOR = 'minor', 'Minor Interaction (Minimal clinical significance)'

    class InteractionType(models.TextChoices):
        PHARMACODYNAMIC = 'pharmacodynamic', 'Pharmacodynamic (Synergistic toxicity or antagonism)'
        PHARMACOKINETIC = 'pharmacokinetic', 'Pharmacokinetic (CYP enzyme inhibition/induction)'
        ADDITIVE_TOXICITY = 'additive_toxicity', 'Additive Toxicity'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine_a = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='interactions_as_a'
    )
    medicine_b = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='interactions_as_b'
    )
    severity = models.CharField(
        max_length=30, choices=Severity.choices, default=Severity.MODERATE, db_index=True
    )
    interaction_type = models.CharField(
        max_length=50, choices=InteractionType.choices, default=InteractionType.PHARMACODYNAMIC
    )
    description = models.TextField(help_text="Detailed mechanism and clinical manifestations of the interaction")
    clinical_management = models.TextField(blank=True, help_text="Recommended clinical action or alternative regimen")
    evidence_level = models.CharField(max_length=20, default='Established')
    source = models.CharField(max_length=255, default='Standard Treatment Guidelines / Lexicomp')
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medical_knowledge_druginteraction'
        verbose_name = 'Drug Interaction'
        verbose_name_plural = 'Drug Interactions'
        indexes = [
            models.Index(fields=['medicine_a', 'medicine_b']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.medicine_a.generic_name} + {self.medicine_b.generic_name}"


class DiseaseTreatment(models.Model):
    """
    Evidence-based clinical treatment regimen linking a Disease to a recommended Medicine.
    """
    
    class TreatmentLine(models.TextChoices):
        FIRST_LINE = 'first_line', 'First-Line / Primary Treatment'
        SECOND_LINE = 'second_line', 'Second-Line / Alternative'
        ADJUNCT = 'adjunct', 'Adjunct / Supportive Therapy'
        PROPHYLAXIS = 'prophylaxis', 'Prophylaxis / Prevention'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease = models.ForeignKey(
        Disease, on_delete=models.CASCADE, related_name='treatments'
    )
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='disease_treatments'
    )
    treatment_line = models.CharField(
        max_length=30, choices=TreatmentLine.choices, default=TreatmentLine.FIRST_LINE
    )
    regimen_instructions = models.TextField(help_text="Exact dose, duration, and clinical administration instructions")
    target_population = models.CharField(max_length=100, default='Adults and Children > 5kg')
    precautions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medical_knowledge_diseasetreatment'
        verbose_name = 'Disease Treatment Protocol'
        verbose_name_plural = 'Disease Treatment Protocols'
        unique_together = ('disease', 'medicine', 'treatment_line')
        indexes = [
            models.Index(fields=['disease', 'treatment_line']),
        ]

    def __str__(self):
        return f"{self.disease.name} -> {self.medicine.generic_name} ({self.get_treatment_line_display()})"
