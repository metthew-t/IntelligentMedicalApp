"""
Synthetic Patient Data Generator for ML Training.
Generates 50,000+ realistic synthetic patient encounters based on the medical knowledge base.
Each encounter includes: symptoms (binary), vital signs, demographics, and confirmed diagnosis.

Uses disease-symptom frequency relationships, category-based vital profiles,
and disease-specific demographic distributions to create realistic training data.
"""
import numpy as np
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class SyntheticPatientGenerator:
    """
    Generates synthetic patient encounter data for training the ML diagnostic classifier.
    Leverages the curated Disease-Symptom relationships stored in the medical knowledge base.
    """

    # Symptom frequency -> probability of appearing in a patient with that disease
    FREQUENCY_PROBABILITIES = {
        'very_common': (0.82, 0.97),   # 82-97% chance of being present
        'common':      (0.55, 0.80),   # 55-80%
        'occasional':  (0.25, 0.50),   # 25-50%
        'rare':        (0.05, 0.20),   # 5-20%
    }

    # Baseline noise: probability of including an UNRELATED symptom
    NOISE_PROB_BASE = 0.025

    # ----- Normal / Healthy Vital Sign Baselines -----
    NORMAL_VITALS = {
        'temperature':    (36.8, 0.3),
        'heart_rate':     (78,  10),
        'systolic_bp':    (120, 10),
        'diastolic_bp':   (78,  8),
        'respiratory_rate':(16, 2),
        'spo2':           (98,  1),
        'blood_glucose':  (95,  12),
    }

    # ----- Disease Category -> Abnormal Vital Profile -----
    CATEGORY_VITAL_PROFILES = {
        'infectious': {
            'temperature':    (39.2, 0.8),
            'heart_rate':     (102, 15),
            'systolic_bp':    (108, 15),
            'diastolic_bp':   (68, 12),
            'respiratory_rate':(20, 3),
            'spo2':           (96, 2),
            'blood_glucose':  (110, 25),
        },
        'respiratory': {
            'temperature':    (38.3, 1.0),
            'heart_rate':     (95, 15),
            'systolic_bp':    (118, 15),
            'diastolic_bp':   (75, 10),
            'respiratory_rate':(24, 5),
            'spo2':           (92, 4),
            'blood_glucose':  (100, 15),
        },
        'cardiovascular': {
            'temperature':    (37.0, 0.4),
            'heart_rate':     (95, 25),
            'systolic_bp':    (145, 30),
            'diastolic_bp':   (90, 15),
            'respiratory_rate':(20, 4),
            'spo2':           (95, 3),
            'blood_glucose':  (105, 20),
        },
        'gastrointestinal': {
            'temperature':    (37.5, 0.8),
            'heart_rate':     (88, 15),
            'systolic_bp':    (115, 15),
            'diastolic_bp':   (72, 10),
            'respiratory_rate':(17, 3),
            'spo2':           (97, 1.5),
            'blood_glucose':  (98, 15),
        },
        'endocrine': {
            'temperature':    (37.2, 0.6),
            'heart_rate':     (100, 18),
            'systolic_bp':    (122, 18),
            'diastolic_bp':   (78, 12),
            'respiratory_rate':(20, 4),
            'spo2':           (97, 2),
            'blood_glucose':  (200, 120),
        },
        'neurological': {
            'temperature':    (37.8, 1.2),
            'heart_rate':     (88, 20),
            'systolic_bp':    (140, 25),
            'diastolic_bp':   (85, 15),
            'respiratory_rate':(18, 3),
            'spo2':           (96, 2),
            'blood_glucose':  (110, 25),
        },
        'genitourinary': {
            'temperature':    (37.8, 0.9),
            'heart_rate':     (90, 14),
            'systolic_bp':    (130, 18),
            'diastolic_bp':   (82, 12),
            'respiratory_rate':(17, 2),
            'spo2':           (97, 1.5),
            'blood_glucose':  (100, 18),
        },
        'musculoskeletal': {
            'temperature':    (37.1, 0.5),
            'heart_rate':     (80, 12),
            'systolic_bp':    (125, 15),
            'diastolic_bp':   (78, 10),
            'respiratory_rate':(16, 2),
            'spo2':           (98, 1),
            'blood_glucose':  (98, 15),
        },
        'hematology': {
            'temperature':    (37.3, 0.7),
            'heart_rate':     (100, 18),
            'systolic_bp':    (108, 15),
            'diastolic_bp':   (68, 10),
            'respiratory_rate':(19, 3),
            'spo2':           (95, 3),
            'blood_glucose':  (100, 15),
        },
        'dermatological': {
            'temperature':    (37.2, 0.5),
            'heart_rate':     (78, 10),
            'systolic_bp':    (120, 12),
            'diastolic_bp':   (78, 8),
            'respiratory_rate':(16, 2),
            'spo2':           (98, 1),
            'blood_glucose':  (95, 12),
        },
        'emergency': {
            'temperature':    (37.5, 1.0),
            'heart_rate':     (110, 25),
            'systolic_bp':    (100, 30),
            'diastolic_bp':   (65, 20),
            'respiratory_rate':(22, 5),
            'spo2':           (93, 5),
            'blood_glucose':  (120, 40),
        },
    }

    # ----- Disease-Specific Vital & Demographic Overrides -----
    DISEASE_OVERRIDES = {
        # Infectious
        'malaria': {
            'vitals': {'temperature': (39.5, 0.7), 'heart_rate': (110, 12)},
            'age': (3, 65, 25, 15), 'male_ratio': 0.55,
        },
        'typhoid fever': {
            'vitals': {'temperature': (39.8, 0.5), 'heart_rate': (85, 12)},  # relative bradycardia
            'age': (5, 55, 22, 12), 'male_ratio': 0.52,
        },
        'dengue fever': {
            'vitals': {'temperature': (39.3, 0.6), 'systolic_bp': (100, 15)},
            'age': (5, 60, 28, 15), 'male_ratio': 0.50,
        },
        'cholera': {
            'vitals': {'heart_rate': (120, 15), 'systolic_bp': (85, 15)},
            'age': (2, 70, 25, 18), 'male_ratio': 0.50,
        },
        'bacterial meningitis': {
            'vitals': {'temperature': (39.8, 0.6), 'heart_rate': (115, 15)},
            'age': (1, 50, 18, 15), 'male_ratio': 0.55,
        },
        'hiv/aids': {
            'age': (18, 65, 35, 10), 'male_ratio': 0.45,
        },
        'tuberculosis': {
            'vitals': {'temperature': (38.0, 0.6)},
            'age': (15, 70, 35, 15), 'male_ratio': 0.60,
        },
        'visceral leishmaniasis': {
            'vitals': {'temperature': (39.0, 0.8)},
            'age': (2, 40, 15, 10), 'male_ratio': 0.60,
        },
        'acute viral hepatitis': {
            'age': (15, 60, 30, 12), 'male_ratio': 0.55,
        },
        'urinary tract infection': {
            'vitals': {'temperature': (38.2, 0.7)},
            'age': (18, 75, 40, 18), 'male_ratio': 0.20,
        },
        # Respiratory
        'community-acquired pneumonia': {
            'vitals': {'temperature': (39.0, 0.7), 'spo2': (91, 4), 'respiratory_rate': (26, 5)},
            'age': (2, 85, 50, 22), 'male_ratio': 0.52,
        },
        'acute asthma exacerbation': {
            'vitals': {'spo2': (90, 5), 'respiratory_rate': (28, 6), 'heart_rate': (110, 15)},
            'age': (5, 65, 25, 18), 'male_ratio': 0.45,
        },
        'copd exacerbation': {
            'vitals': {'spo2': (88, 5), 'respiratory_rate': (24, 5)},
            'age': (45, 85, 65, 10), 'male_ratio': 0.60,
        },
        'pulmonary embolism': {
            'vitals': {'heart_rate': (115, 18), 'spo2': (89, 5), 'respiratory_rate': (26, 5)},
            'age': (25, 80, 55, 15), 'male_ratio': 0.45,
        },
        'pleural effusion': {
            'vitals': {'spo2': (93, 3), 'respiratory_rate': (22, 4)},
            'age': (30, 80, 58, 15), 'male_ratio': 0.55,
        },
        # Cardiovascular
        'acute stemi': {
            'vitals': {'heart_rate': (95, 25), 'systolic_bp': (100, 30), 'spo2': (94, 3)},
            'age': (40, 85, 62, 12), 'male_ratio': 0.72,
        },
        'congestive heart failure': {
            'vitals': {'heart_rate': (100, 18), 'systolic_bp': (135, 25), 'spo2': (92, 4), 'respiratory_rate': (22, 4)},
            'age': (45, 90, 68, 12), 'male_ratio': 0.55,
        },
        'hypertensive crisis': {
            'vitals': {'systolic_bp': (210, 25), 'diastolic_bp': (130, 15), 'heart_rate': (100, 18)},
            'age': (35, 80, 58, 12), 'male_ratio': 0.48,
        },
        'atrial fibrillation': {
            'vitals': {'heart_rate': (140, 25)},
            'age': (50, 90, 72, 10), 'male_ratio': 0.55,
        },
        'deep vein thrombosis': {
            'age': (25, 80, 55, 18), 'male_ratio': 0.45,
        },
        # Gastrointestinal
        'acute appendicitis': {
            'vitals': {'temperature': (38.2, 0.6), 'heart_rate': (95, 12)},
            'age': (10, 45, 25, 10), 'male_ratio': 0.55,
        },
        'peptic ulcer disease': {
            'age': (25, 70, 45, 15), 'male_ratio': 0.60,
        },
        'acute pancreatitis': {
            'vitals': {'heart_rate': (105, 15), 'temperature': (38.0, 0.7)},
            'age': (30, 70, 50, 12), 'male_ratio': 0.60,
        },
        'acute gastroenteritis': {
            'vitals': {'heart_rate': (95, 12)},
            'age': (2, 75, 25, 20), 'male_ratio': 0.50,
        },
        'hepatic cirrhosis': {
            'vitals': {'systolic_bp': (105, 15)},
            'age': (35, 75, 55, 10), 'male_ratio': 0.65,
        },
        'intestinal obstruction': {
            'vitals': {'heart_rate': (105, 15)},
            'age': (20, 80, 55, 18), 'male_ratio': 0.50,
        },
        # Endocrine
        'diabetic ketoacidosis': {
            'vitals': {'blood_glucose': (450, 120), 'respiratory_rate': (28, 5), 'heart_rate': (115, 15), 'systolic_bp': (95, 15)},
            'age': (12, 65, 30, 15), 'male_ratio': 0.48,
        },
        'thyroid storm': {
            'vitals': {'heart_rate': (145, 20), 'temperature': (39.5, 0.8), 'systolic_bp': (160, 20)},
            'age': (20, 60, 38, 12), 'male_ratio': 0.25,
        },
        'hypoglycemia': {
            'vitals': {'blood_glucose': (38, 12), 'heart_rate': (105, 15)},
            'age': (15, 80, 55, 18), 'male_ratio': 0.50,
        },
        'addisonian crisis': {
            'vitals': {'systolic_bp': (80, 12), 'heart_rate': (115, 15), 'blood_glucose': (55, 15)},
            'age': (20, 60, 40, 12), 'male_ratio': 0.40,
        },
        # Neurological
        'ischemic stroke': {
            'vitals': {'systolic_bp': (170, 25), 'diastolic_bp': (100, 15)},
            'age': (45, 90, 68, 12), 'male_ratio': 0.55,
        },
        'status epilepticus': {
            'vitals': {'heart_rate': (120, 18), 'temperature': (38.5, 0.8)},
            'age': (5, 70, 30, 20), 'male_ratio': 0.55,
        },
        'migraine with aura': {
            'age': (15, 55, 32, 10), 'male_ratio': 0.30,
        },
        # Renal
        'acute kidney injury': {
            'vitals': {'systolic_bp': (100, 20), 'heart_rate': (100, 15)},
            'age': (30, 85, 60, 15), 'male_ratio': 0.55,
        },
        'nephrotic syndrome': {
            'age': (3, 60, 25, 18), 'male_ratio': 0.55,
        },
        # Musculoskeletal
        'rheumatoid arthritis': {
            'age': (25, 70, 45, 12), 'male_ratio': 0.30,
        },
        'acute gout': {
            'age': (30, 75, 52, 12), 'male_ratio': 0.80,
        },
        # Hematological
        'severe anemia': {
            'vitals': {'heart_rate': (110, 15), 'systolic_bp': (100, 12)},
            'age': (5, 80, 35, 20), 'male_ratio': 0.45,
        },
        'sickle cell crisis': {
            'vitals': {'heart_rate': (115, 15), 'spo2': (93, 3)},
            'age': (5, 45, 20, 10), 'male_ratio': 0.50,
        },
        'disseminated intravascular coagulation': {
            'vitals': {'heart_rate': (125, 18), 'systolic_bp': (85, 18), 'temperature': (38.5, 1.0)},
            'age': (20, 75, 50, 15), 'male_ratio': 0.50,
        },
    }

    # Default demographic profiles if no override is given
    DEFAULT_DEMOGRAPHICS = {
        'age': (5, 80, 40, 18),    # min, max, mean, std
        'male_ratio': 0.50,
    }

    # Physiologically valid ranges (for clipping)
    VITAL_RANGES = {
        'temperature':     (34.0, 42.5),
        'heart_rate':      (30, 220),
        'systolic_bp':     (50, 260),
        'diastolic_bp':    (30, 160),
        'respiratory_rate':(6, 50),
        'spo2':            (60, 100),
        'blood_glucose':   (15, 800),
    }

    def __init__(self):
        """Initialize - knowledge base loaded from DB at generation time."""
        self.diseases = []
        self.symptoms = []
        self.symptom_names = []
        self.symptom_id_to_idx = {}
        self.disease_symptom_map = {}
        self.disease_categories = {}
        self.disease_names = []
        self._loaded = False

    def _load_knowledge_base(self):
        """Load all diseases, symptoms, and their relationships from the database."""
        from apps.medical_knowledge.models import Disease, Symptom, DiseaseSymptom

        # Load all active symptoms, ordered consistently
        self.symptoms = list(Symptom.objects.filter(is_active=True).order_by('name'))
        self.symptom_names = [s.name for s in self.symptoms]
        self.symptom_id_to_idx = {str(s.id): idx for idx, s in enumerate(self.symptoms)}

        # Load all active diseases with symptom associations
        self.diseases = list(Disease.objects.filter(is_active=True).order_by('name'))
        self.disease_names = [d.name for d in self.diseases]

        for disease in self.diseases:
            self.disease_categories[disease.name] = disease.category
            associations = list(DiseaseSymptom.objects.filter(
                disease=disease, is_active=True
            ).select_related('symptom'))
            self.disease_symptom_map[disease.name] = associations

        self._loaded = True

    def _get_disease_profile(self, disease_name: str, category: str) -> dict:
        """Get vital profile and demographics for a specific disease."""
        # Start with category-level profile
        category_key = category  # Category field value matches our profile keys
        vital_profile = dict(self.CATEGORY_VITAL_PROFILES.get(
            category_key, self.CATEGORY_VITAL_PROFILES.get('infectious', self.NORMAL_VITALS)
        ))
        demographics = dict(self.DEFAULT_DEMOGRAPHICS)

        # Apply disease-specific overrides
        override = self.DISEASE_OVERRIDES.get(disease_name.lower(), {})
        if 'vitals' in override:
            vital_profile.update(override['vitals'])
        if 'age' in override:
            demographics['age'] = override['age']
        if 'male_ratio' in override:
            demographics['male_ratio'] = override['male_ratio']

        return {'vitals': vital_profile, 'demographics': demographics}

    def _generate_symptom_vector(
        self,
        disease_associations: list,
        num_symptoms: int,
        rng: np.random.Generator
    ) -> np.ndarray:
        """Generate binary symptom feature vector for one patient encounter."""
        vector = np.zeros(num_symptoms, dtype=np.float32)

        # 1. Include disease-linked symptoms based on frequency probabilities
        for assoc in disease_associations:
            sym_id = str(assoc.symptom.id)
            if sym_id not in self.symptom_id_to_idx:
                continue
            idx = self.symptom_id_to_idx[sym_id]

            freq = assoc.frequency
            prob_range = self.FREQUENCY_PROBABILITIES.get(freq, (0.30, 0.60))
            inclusion_prob = rng.uniform(prob_range[0], prob_range[1])

            # Hallmark / pathognomonic symptoms have a boosted probability
            if assoc.is_hallmark or assoc.specificity == 'pathognomonic':
                inclusion_prob = min(0.99, inclusion_prob + 0.10)

            if rng.random() < inclusion_prob:
                vector[idx] = 1.0

        # 2. Add noise: random unrelated symptoms
        for idx in range(num_symptoms):
            if vector[idx] == 0.0 and rng.random() < self.NOISE_PROB_BASE:
                vector[idx] = 1.0

        # 3. Ensure at least 2 symptoms are present
        unset_assocs = [
            a for a in disease_associations
            if str(a.symptom.id) in self.symptom_id_to_idx and vector[self.symptom_id_to_idx[str(a.symptom.id)]] == 0.0
        ]
        while vector.sum() < 2:
            if unset_assocs:
                assoc = unset_assocs.pop(int(rng.integers(0, len(unset_assocs))))
                vector[self.symptom_id_to_idx[str(assoc.symptom.id)]] = 1.0
            else:
                rand_idx = int(rng.integers(0, num_symptoms))
                vector[rand_idx] = 1.0

        return vector

    def _generate_vitals(
        self,
        vital_profile: dict,
        rng: np.random.Generator
    ) -> np.ndarray:
        """Generate realistic vital signs for one patient encounter."""
        vital_keys = ['temperature', 'heart_rate', 'systolic_bp', 'diastolic_bp',
                      'respiratory_rate', 'spo2', 'blood_glucose']
        vitals = np.zeros(len(vital_keys), dtype=np.float32)

        for i, key in enumerate(vital_keys):
            mean, std = vital_profile.get(key, self.NORMAL_VITALS[key])
            value = rng.normal(mean, std)
            # Clip to physiologically valid ranges
            vmin, vmax = self.VITAL_RANGES[key]
            vitals[i] = np.clip(value, vmin, vmax)

        return vitals

    def _generate_demographics(
        self,
        demo_profile: dict,
        rng: np.random.Generator
    ) -> np.ndarray:
        """Generate age and sex for one patient encounter."""
        age_min, age_max, age_mean, age_std = demo_profile['age']
        age = rng.normal(age_mean, age_std)
        age = np.clip(age, age_min, age_max)

        sex = 1.0 if rng.random() < demo_profile['male_ratio'] else 0.0  # 1=male, 0=female

        return np.array([age, sex], dtype=np.float32)

    def _compute_derived_features(
        self,
        vitals: np.ndarray,
        symptom_vector: np.ndarray
    ) -> np.ndarray:
        """Compute derived clinical indicator features."""
        temp, hr, sbp, dbp, rr, spo2, glucose = vitals
        return np.array([
            float(symptom_vector.sum()),    # num_symptoms_present
            float(temp >= 38.0),            # has_fever
            float(hr > 100),               # has_tachycardia
            float(sbp < 90),               # has_hypotension
            float(spo2 < 94),              # has_hypoxia
            float(rr > 20),               # has_tachypnea
            float(glucose > 200),          # has_hyperglycemia
            float(glucose < 60),           # has_hypoglycemia
        ], dtype=np.float32)

    def generate_dataset(
        self,
        total_samples: int = 52500,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, List[str], List[str], dict]:
        """
        Generate the full synthetic training dataset.

        Args:
            total_samples: Total number of patient encounters to generate (default 52,500)
            random_state: Random seed for reproducibility

        Returns:
            X: Feature matrix (n_samples x n_features) as float32 ndarray
            y: Label vector (n_samples,) as int32 ndarray (disease index)
            feature_names: List of feature names
            label_names: List of disease names (y[i] maps to label_names[y[i]])
            metadata: Dict with generation statistics
        """
        if not self._loaded:
            self._load_knowledge_base()

        rng = np.random.default_rng(random_state)
        num_diseases = len(self.diseases)
        num_symptoms = len(self.symptoms)

        if num_diseases == 0 or num_symptoms == 0:
            raise ValueError(
                f"Medical knowledge base is empty (diseases={num_diseases}, "
                f"symptoms={num_symptoms}). Run `python manage.py init_medical_data` first."
            )

        # Determine samples per disease
        # Higher prevalence diseases get more cases, but minimum 500 per disease
        base_per_disease = total_samples // num_diseases
        samples_per_disease = {}

        # Assign based on number of symptoms (diseases with more symptoms tend to be more common)
        total_sym_count = sum(len(self.disease_symptom_map.get(d.name, [])) for d in self.diseases)
        for disease in self.diseases:
            n_assocs = len(self.disease_symptom_map.get(disease.name, []))
            if total_sym_count > 0:
                weight = max(0.5, n_assocs / max(1, total_sym_count / num_diseases))
            else:
                weight = 1.0
            count = max(500, int(base_per_disease * weight))
            # Add random variation (+/- 15%)
            count = int(count * rng.uniform(0.85, 1.15))
            samples_per_disease[disease.name] = count

        # Adjust to reach total_samples
        current_total = sum(samples_per_disease.values())
        if current_total < total_samples:
            # Distribute remaining across diseases randomly
            remaining = total_samples - current_total
            for _ in range(remaining):
                d_name = rng.choice(self.disease_names)
                samples_per_disease[d_name] += 1
        elif current_total > total_samples:
            # Trim from largest
            excess = current_total - total_samples
            for _ in range(excess):
                largest = max(samples_per_disease, key=samples_per_disease.get)
                samples_per_disease[largest] -= 1

        # Feature dimensions
        n_vital_features = 7
        n_demo_features = 2
        n_derived_features = 8
        n_features = num_symptoms + n_vital_features + n_demo_features + n_derived_features

        # Build feature names
        feature_names = list(self.symptom_names)  # Binary symptom features
        feature_names += ['vital_temperature', 'vital_heart_rate', 'vital_systolic_bp',
                         'vital_diastolic_bp', 'vital_respiratory_rate', 'vital_spo2',
                         'vital_blood_glucose']
        feature_names += ['demo_age', 'demo_sex']
        feature_names += ['derived_num_symptoms', 'derived_has_fever', 'derived_has_tachycardia',
                         'derived_has_hypotension', 'derived_has_hypoxia', 'derived_has_tachypnea',
                         'derived_has_hyperglycemia', 'derived_has_hypoglycemia']

        actual_total = sum(samples_per_disease.values())
        X = np.zeros((actual_total, n_features), dtype=np.float32)
        y = np.zeros(actual_total, dtype=np.int32)

        label_names = list(self.disease_names)

        idx = 0
        disease_stats = {}

        for disease_idx, disease in enumerate(self.diseases):
            n_cases = samples_per_disease[disease.name]
            associations = self.disease_symptom_map.get(disease.name, [])
            profile = self._get_disease_profile(disease.name, disease.category)

            for case_i in range(n_cases):
                # Generate symptom vector
                sym_vec = self._generate_symptom_vector(associations, num_symptoms, rng)

                # Generate vitals
                vitals = self._generate_vitals(profile['vitals'], rng)

                # Generate demographics
                demographics = self._generate_demographics(profile['demographics'], rng)

                # Compute derived features
                derived = self._compute_derived_features(vitals, sym_vec)

                # Assemble feature vector
                X[idx, :num_symptoms] = sym_vec
                X[idx, num_symptoms:num_symptoms + n_vital_features] = vitals
                X[idx, num_symptoms + n_vital_features:num_symptoms + n_vital_features + n_demo_features] = demographics
                X[idx, num_symptoms + n_vital_features + n_demo_features:] = derived
                y[idx] = disease_idx
                idx += 1

            disease_stats[disease.name] = {
                'count': n_cases,
                'category': disease.category,
                'n_symptom_links': len(associations),
            }

        # Shuffle dataset
        shuffle_idx = rng.permutation(actual_total)
        X = X[shuffle_idx]
        y = y[shuffle_idx]

        metadata = {
            'total_samples': actual_total,
            'num_diseases': num_diseases,
            'num_symptoms': num_symptoms,
            'num_features': n_features,
            'disease_stats': disease_stats,
            'random_state': random_state,
            'feature_breakdown': {
                'symptom_features': num_symptoms,
                'vital_features': n_vital_features,
                'demographic_features': n_demo_features,
                'derived_features': n_derived_features,
            }
        }

        return X, y, feature_names, label_names, metadata

    def save_to_csv(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        label_names: List[str],
        filepath: str
    ) -> str:
        """Save generated dataset to CSV file."""
        df = pd.DataFrame(X, columns=feature_names)
        df['disease_label'] = [label_names[yi] for yi in y]
        df['disease_index'] = y
        df.to_csv(filepath, index=False)
        return filepath
