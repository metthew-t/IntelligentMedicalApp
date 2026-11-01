"""
Medical Machine Learning Model Trainer and Inference Pipeline.
Trains an ensemble Random Forest classifier on 50,000+ synthetic patient encounters
generated from the clinical medical knowledge base.

Saves model bundle with feature mappings, label encoders, and clinical evaluation metrics.
Provides real-time patient feature vectorization and probability prediction.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, top_k_accuracy_score, classification_report

from apps.decision_support.ml_engine.data_generator import SyntheticPatientGenerator


# Directory where trained models and metrics are saved
MODEL_DIR = Path(__file__).resolve().parent / 'trained_models'
MODEL_BUNDLE_PATH = MODEL_DIR / 'medical_ai_model.joblib'
METRICS_JSON_PATH = MODEL_DIR / 'model_metrics.json'


class MedicalModelTrainer:
    """
    Orchestrates the generation of 50,000+ patient encounters, model training,
    evaluation across Top-1, Top-3, and Top-5 accuracy, and bundle serialization.
    """

    def __init__(self, model_bundle_path: Optional[Path] = None):
        self.model_path = model_bundle_path or MODEL_BUNDLE_PATH
        self.metrics_path = METRICS_JSON_PATH
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        total_samples: int = 52500,
        test_size: float = 0.2,
        random_state: int = 42,
        n_estimators: int = 120,
        max_depth: int = 22,
        export_csv_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end training pipeline on 50,000+ patient records:
        1. Generates 52,500 clinical patient presentations from medical knowledge.
        2. Optionally exports full training dataset to CSV.
        3. Trains an optimized multi-class Random Forest with balanced representation.
        4. Evaluates Top-1, Top-3, and Top-5 test accuracy.
        5. Saves serialized bundle and JSON metrics report.
        """
        start_time = time.time()

        # Step 1: Generate synthetic patient data
        print(f"[ML Trainer] Generating {total_samples:,} patient encounters from medical knowledge base...")
        generator = SyntheticPatientGenerator()
        X, y, feature_names, label_names, gen_meta = generator.generate_dataset(
            total_samples=total_samples,
            random_state=random_state
        )
        gen_time = time.time() - start_time
        print(f"[ML Trainer] Generated {len(y):,} records across {len(label_names)} diseases in {gen_time:.2f}s.")

        # Step 2: Optional CSV Export
        if export_csv_path:
            print(f"[ML Trainer] Exporting dataset to CSV: {export_csv_path}...")
            generator.save_to_csv(X, y, feature_names, label_names, export_csv_path)
            print(f"[ML Trainer] Export complete.")

        # Step 3: Train / Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        print(f"[ML Trainer] Train set: {len(y_train):,} | Test set: {len(y_test):,}")

        # Step 4: Model Training
        train_start = time.time()
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=4,
            min_samples_leaf=2,
            n_jobs=1,
            random_state=random_state
        )
        clf.fit(X_train, y_train)
        training_time = time.time() - train_start
        print(f"[ML Trainer] Model trained in {training_time:.2f}s.")

        # Step 5: Comprehensive Clinical Evaluation
        y_train_pred = clf.predict(X_train)
        y_test_pred = clf.predict(X_test)
        y_test_proba = clf.predict_proba(X_test)

        train_acc = float(accuracy_score(y_train, y_train_pred))
        test_top1_acc = float(accuracy_score(y_test, y_test_pred))
        
        all_classes = np.arange(len(label_names))
        test_top3_acc = float(top_k_accuracy_score(y_test, y_test_proba, k=3, labels=all_classes))
        test_top5_acc = float(top_k_accuracy_score(y_test, y_test_proba, k=5, labels=all_classes))

        # Global Feature Importances
        importances = clf.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        top_features = [
            {'feature': feature_names[i], 'importance': round(float(importances[i]), 5)}
            for i in sorted_indices[:20]
        ]

        total_elapsed = time.time() - start_time

        metrics = {
            'model_name': 'RandomForest-Medical-Classifier',
            'version': 'v2.5-50k-plus',
            'training_timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_samples': len(y),
            'train_samples': len(y_train),
            'test_samples': len(y_test),
            'num_diseases': len(label_names),
            'num_features': len(feature_names),
            'train_accuracy': round(train_acc, 4),
            'test_top1_accuracy': round(test_top1_acc, 4),
            'test_top3_accuracy': round(test_top3_acc, 4),
            'test_top5_accuracy': round(test_top5_acc, 4),
            'generation_time_sec': round(gen_time, 2),
            'training_time_sec': round(training_time, 2),
            'total_pipeline_time_sec': round(total_elapsed, 2),
            'algorithm_hyperparameters': {
                'n_estimators': n_estimators,
                'max_depth': max_depth,
                'min_samples_split': 4,
                'min_samples_leaf': 2,
            },
            'top_20_predictive_features': top_features,
            'feature_breakdown': gen_meta.get('feature_breakdown', {})
        }

        # Step 6: Serialize Model Bundle
        bundle = {
            'model': clf,
            'feature_names': feature_names,
            'label_names': label_names,
            'symptom_names': list(generator.symptom_names),
            'n_symptoms': len(generator.symptom_names),
            'metrics': metrics,
        }

        print(f"[ML Trainer] Saving model bundle to {self.model_path}...")
        joblib.dump(bundle, self.model_path, compress=3)

        # Save metrics JSON for quick dashboard reading
        with open(self.metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

        print(f"[ML Trainer] Success! Top-1 Accuracy: {test_top1_acc*100:.2f}% | Top-3 Accuracy: {test_top3_acc*100:.2f}%")
        return metrics


class TrainedModelPredictor:
    """
    High-performance inference wrapper for the trained medical ML model.
    Loads cached model bundle from disk and evaluates patient presentations.
    """

    _cached_bundle: Optional[Dict[str, Any]] = None
    _cached_path: Optional[str] = None

    def __init__(self, bundle_path: Optional[Path] = None):
        self.bundle_path = bundle_path or MODEL_BUNDLE_PATH
        self.load()

    def load(self) -> bool:
        """Loads model bundle into memory (cached across requests)."""
        if TrainedModelPredictor._cached_bundle is not None and TrainedModelPredictor._cached_path == str(self.bundle_path):
            self.bundle = TrainedModelPredictor._cached_bundle
            return True

        if not self.bundle_path.exists():
            self.bundle = None
            return False

        try:
            self.bundle = joblib.load(self.bundle_path)
            TrainedModelPredictor._cached_bundle = self.bundle
            TrainedModelPredictor._cached_path = str(self.bundle_path)
            return True
        except Exception as e:
            print(f"[ML Predictor] Error loading model bundle: {e}")
            self.bundle = None
            return False

    @property
    def is_available(self) -> bool:
        return self.bundle is not None

    @property
    def metrics(self) -> Dict[str, Any]:
        if self.bundle:
            return self.bundle.get('metrics', {})
        return {}

    def build_feature_vector(
        self,
        symptoms: List[str],
        signs: List[str],
        vitals: Dict[str, Any],
        demographics: Dict[str, Any]
    ) -> np.ndarray:
        """
        Constructs the exact 81-dimensional float32 feature vector for a patient.
        Features layout:
        [0 .. n_symptoms-1]: binary symptom/sign flags
        [n_symptoms .. n_symptoms+6]: 7 continuous vital signs
        [n_symptoms+7 .. n_symptoms+8]: 2 demographics (age, sex)
        [n_symptoms+9 .. end]: 8 derived clinical indicators
        """
        if not self.bundle:
            raise RuntimeError("Model bundle is not loaded.")

        symptom_names = self.bundle['symptom_names']
        n_symptoms = len(symptom_names)
        n_vitals = 7
        n_demographics = 2
        n_derived = 8
        total_dim = n_symptoms + n_vitals + n_demographics + n_derived

        vec = np.zeros(total_dim, dtype=np.float32)

        # Normalize patient reported terms
        all_patient_terms = set(t.lower().strip() for t in (symptoms + signs) if t and t.strip())

        # 1. Symptom flags
        for i, sym_name in enumerate(symptom_names):
            sym_clean = sym_name.lower().strip()
            if sym_clean in all_patient_terms:
                vec[i] = 1.0
            elif any(sym_clean in term or term in sym_clean for term in all_patient_terms):
                vec[i] = 1.0

        # 2. Vital signs
        temp = float(vitals.get('temperature', 36.8) or 36.8)
        hr = float(vitals.get('heart_rate', 78.0) or 78.0)
        sbp = float(vitals.get('systolic_bp', 120.0) or 120.0)
        dbp = float(vitals.get('diastolic_bp', 78.0) or 78.0)
        rr = float(vitals.get('respiratory_rate', 16.0) or 16.0)
        spo2 = float(vitals.get('spo2', 98.0) or 98.0)
        glucose = float(vitals.get('blood_glucose', 95.0) or 95.0)

        vitals_slice = slice(n_symptoms, n_symptoms + n_vitals)
        vec[vitals_slice] = [temp, hr, sbp, dbp, rr, spo2, glucose]

        # 3. Demographics
        age = float(demographics.get('age', 35.0) or 35.0)
        gender = str(demographics.get('gender', 'male')).lower()
        sex_binary = 1.0 if gender in ['female', 'f'] else 0.0

        demo_slice = slice(n_symptoms + n_vitals, n_symptoms + n_vitals + n_demographics)
        vec[demo_slice] = [age, sex_binary]

        # 4. Derived clinical indicators
        num_symptoms_present = float(vec[:n_symptoms].sum())
        has_fever = float(temp >= 38.0)
        has_tachycardia = float(hr > 100.0)
        has_hypotension = float(sbp < 90.0)
        has_hypoxia = float(spo2 < 94.0)
        has_tachypnea = float(rr > 20.0)
        has_hyperglycemia = float(glucose > 200.0)
        has_hypoglycemia = float(glucose < 60.0)

        derived_slice = slice(n_symptoms + n_vitals + n_demographics, total_dim)
        vec[derived_slice] = [
            num_symptoms_present,
            has_fever,
            has_tachycardia,
            has_hypotension,
            has_hypoxia,
            has_tachypnea,
            has_hyperglycemia,
            has_hypoglycemia
        ]

        return vec

    def predict(
        self,
        symptoms: List[str],
        signs: List[str],
        vitals: Dict[str, Any],
        demographics: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Runs model inference on presenting clinical data.
        Returns mapping of: {disease_name: ml_probability} for all active diseases.
        """
        if not self.bundle:
            return {}

        model = self.bundle['model']
        label_names = self.bundle['label_names']

        feature_vector = self.build_feature_vector(symptoms, signs, vitals, demographics)
        X = feature_vector.reshape(1, -1)

        probas = model.predict_proba(X)[0]
        return {label_names[i]: float(probas[i]) for i in range(len(label_names))}
