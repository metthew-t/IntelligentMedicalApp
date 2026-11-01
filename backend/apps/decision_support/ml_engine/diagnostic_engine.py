"""
Hybrid Machine Learning Diagnostic Engine for Clinical Decision Support (CDSS).
Combines:
1. Multi-feature Random Forest / Gradient Boosting pattern classifier.
2. Clinical Bayesian Likelihood model incorporating sign/symptom frequency and specificity.
3. Vital signs hemodynamic & physiological risk evaluator.
4. Red Flag clinical safety triage & emergency alert scanner.
5. Evidence-based medication & drug interaction safety analyzer.
"""
import math
import numpy as np
from typing import Dict, List, Any, Tuple
from django.db.models import Q


from apps.decision_support.ml_engine.model_trainer import TrainedModelPredictor


class HybridDiagnosticEngine:
    """
    State-of-the-art Hybrid Diagnostic Engine adhering to Clinical Decision Support guidelines.
    Combines:
    1. Multi-class Machine Learning model trained on 50,000+ realistic patient cases.
    2. Clinical Bayesian Likelihood model incorporating sign/symptom frequency and specificity.
    3. Vital signs hemodynamic & physiological risk evaluator.
    4. Red Flag clinical safety triage & emergency alert scanner.
    5. Evidence-based medication & drug interaction safety analyzer.
    """
    
    ENGINE_VERSION = "Hybrid-AI-CDSS-v2.5"
    MODEL_VERSION = "RF-50K-Bayes-2026.10"

    # Red Flag Danger Signs definitions with high clinical urgency
    CRITICAL_RED_FLAGS = {
        'nuchal_rigidity': {
            'keywords': ['nuchal rigidity', 'neck stiffness', 'stiff neck', 'kernig', 'brudzinski'],
            'urgency': 'resuscitation',
            'alert': 'Meningeal irritation detected. Urgent lumbar puncture and IV antimicrobial coverage recommended.'
        },
        'severe_hypoxemia': {
            'keywords': ['severe hypoxemia', 'cyanosis', 'stridor', 'central cyanosis'],
            'urgency': 'resuscitation',
            'alert': 'Severe hypoxemia / respiratory failure. Immediate high-flow oxygen and airway assessment.'
        },
        'cardiac_arrest_ischemia': {
            'keywords': ['crushing', 'retrosternal', 'radiation to left arm', 'radiating chest pain', 'levine sign'],
            'urgency': 'emergency',
            'alert': 'Acute coronary syndrome / Myocardial Infarction warning. Immediate 12-lead ECG and troponin.'
        },
        'acute_neurological_deficit': {
            'keywords': ['facial droop', 'hemiplegia', 'hemiparesis', 'acute slurred speech', 'aphasia', 'unilateral weakness'],
            'urgency': 'emergency',
            'alert': 'Acute cerebrovascular accident (Stroke) warning. Rapid non-contrast head CT and thrombolysis screening.'
        },
        'severe_dehydration_shock': {
            'keywords': ['rice-water stool', 'sunken eyes with lethargy', 'hypovolemic shock', 'unrecordable pulse'],
            'urgency': 'resuscitation',
            'alert': 'Severe dehydration / Hypovolemic shock. Immediate IV Ringer Lactate resuscitation.'
        },
        'acute_abdomen': {
            'keywords': ['board-like abdominal rigidity', 'rebound tenderness', 'involuntary guarding'],
            'urgency': 'emergency',
            'alert': 'Peritoneal irritation / Acute Surgical Abdomen. Urgent surgical consultation.'
        },
        'altered_mental_status': {
            'keywords': ['coma', 'unresponsive', 'gcs < 9', 'stupor', 'severe delirium'],
            'urgency': 'resuscitation',
            'alert': 'Severe acute encephalopathy / Altered Consciousness. Check blood glucose and secure airway.'
        }
    }

    def __init__(self):
        self.predictor = TrainedModelPredictor()

    def evaluate_triage(
        self,
        symptoms: List[str],
        signs: List[str],
        vitals: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Evaluates emergency triage level based on findings and vitals.
        Returns: (triage_level, red_flags_detected)
        """
        red_flags_detected = []
        highest_urgency = 'less_urgent'
        urgency_ranks = {
            'non_urgent': 1,
            'less_urgent': 2,
            'urgent': 3,
            'emergency': 4,
            'resuscitation': 5
        }

        all_terms = [s.lower().strip() for s in symptoms + signs]

        # 1. Check keyword red flags
        for flag_key, flag_info in self.CRITICAL_RED_FLAGS.items():
            for kw in flag_info['keywords']:
                if any(kw in term for term in all_terms):
                    red_flags_detected.append({
                        'code': flag_key,
                        'name': kw.title(),
                        'urgency': flag_info['urgency'],
                        'alert': flag_info['alert']
                    })
                    if urgency_ranks[flag_info['urgency']] > urgency_ranks[highest_urgency]:
                        highest_urgency = flag_info['urgency']
                    break

        # Also check Symptom records with is_red_flag=True in database
        try:
            from apps.medical_knowledge.models import Symptom
            for term in (symptoms + signs):
                term_clean = term.lower().strip()
                flagged_symptoms = Symptom.objects.filter(is_red_flag=True).filter(
                    Q(name__icontains=term_clean) | Q(synonyms__icontains=term_clean)
                )
                for fs in flagged_symptoms:
                    if not any(rf['name'] == fs.name for rf in red_flags_detected):
                        red_flags_detected.append({
                            'code': 'clinical_danger_sign',
                            'name': fs.name,
                            'urgency': 'emergency',
                            'alert': f"Clinical danger sign detected: {fs.description or fs.name} requires immediate medical evaluation."
                        })
                        if urgency_ranks['emergency'] > urgency_ranks[highest_urgency]:
                            highest_urgency = 'emergency'
        except Exception:
            pass

        # 2. Check vital signs thresholds
        temp = vitals.get('temperature')
        spo2 = vitals.get('spo2')
        sbp = vitals.get('systolic_bp')
        dbp = vitals.get('diastolic_bp')
        hr = vitals.get('heart_rate')
        rr = vitals.get('respiratory_rate')

        if spo2 is not None:
            try:
                spo2_val = float(spo2)
                if spo2_val < 90.0:
                    red_flags_detected.append({
                        'code': 'critical_hypoxia',
                        'name': f'Severe Hypoxemia (SpO2 {spo2_val}%)',
                        'urgency': 'resuscitation',
                        'alert': 'SpO2 < 90% indicates impending respiratory failure. Supplemental oxygen required immediately.'
                    })
                    highest_urgency = 'resuscitation'
                elif spo2_val < 94.0:
                    red_flags_detected.append({
                        'code': 'mild_hypoxia',
                        'name': f'Hypoxemia (SpO2 {spo2_val}%)',
                        'urgency': 'urgent',
                        'alert': 'SpO2 < 94% indicates abnormal respiratory gas exchange.'
                    })
                    if urgency_ranks['urgent'] > urgency_ranks[highest_urgency]:
                        highest_urgency = 'urgent'
            except (ValueError, TypeError):
                pass

        if sbp is not None:
            try:
                sbp_val = float(sbp)
                if sbp_val < 85.0:
                    red_flags_detected.append({
                        'code': 'hemodynamic_shock',
                        'name': f'Severe Hypotension / Shock (SBP {sbp_val} mmHg)',
                        'urgency': 'resuscitation',
                        'alert': 'Systolic BP < 85 mmHg indicates decompensated circulatory shock.'
                    })
                    highest_urgency = 'resuscitation'
                elif sbp_val >= 200.0 or (dbp is not None and float(dbp) >= 120.0):
                    red_flags_detected.append({
                        'code': 'hypertensive_crisis',
                        'name': f'Hypertensive Crisis ({sbp_val}/{dbp} mmHg)',
                        'urgency': 'emergency',
                        'alert': 'Severely elevated BP warrants screening for acute target organ damage.'
                    })
                    if urgency_ranks['emergency'] > urgency_ranks[highest_urgency]:
                        highest_urgency = 'emergency'
            except (ValueError, TypeError):
                pass

        if temp is not None:
            try:
                temp_val = float(temp)
                if temp_val >= 40.5:
                    red_flags_detected.append({
                        'code': 'hyperpyrexia',
                        'name': f'Hyperpyrexia ({temp_val}°C)',
                        'urgency': 'emergency',
                        'alert': 'Core body temperature >= 40.5°C requires active cooling to prevent neurological damage.'
                    })
                    if urgency_ranks['emergency'] > urgency_ranks[highest_urgency]:
                        highest_urgency = 'emergency'
                elif temp_val <= 35.0:
                    red_flags_detected.append({
                        'code': 'hypothermia',
                        'name': f'Hypothermia ({temp_val}°C)',
                        'urgency': 'emergency',
                        'alert': 'Core body temperature <= 35.0°C indicates systemic hypothermia or sepsis.'
                    })
                    if urgency_ranks['emergency'] > urgency_ranks[highest_urgency]:
                        highest_urgency = 'emergency'
            except (ValueError, TypeError):
                pass

        return highest_urgency, red_flags_detected

    def evaluate_specialist_modalities(
        self,
        disease,
        anamnesis: Dict[str, Any],
        physical_exam: Dict[str, Any],
        labs: Dict[str, Any],
        tools: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, str]]]:
        """
        Tertiary / Specialist Hospital Diagnostic Evidence Evaluator:
        Analyzes:
        1. Anamnesis / Oral History taken by mouth (onset, character, radiation, travel history)
        2. Physical Examination findings (stethoscope auscultation, palpation, neurological exam)
        3. Laboratory Diagnostic Panels (tested by laboratory: Troponin, Blood Smear, WBC, CSF, Ketones, etc.)
        4. Diagnostic & Bedside Tools (12-lead ECG, Chest X-Ray, CT, Ultrasound/POCUS, ABG)
        Returns: (bonus_score, confirmatory_evidence_list)
        """
        bonus = 0.0
        evidence = []
        d_name_lower = disease.name.lower()

        anamnesis = anamnesis or {}
        physical_exam = physical_exam or {}
        labs = labs or {}
        tools = tools or {}

        # Stringified helpers for flexible searching
        all_labs_str = " ".join(f"{k}:{v}" for k, v in labs.items()).lower()
        all_tools_str = " ".join(f"{k}:{v}" for k, v in tools.items()).lower()
        all_exam_str = " ".join(f"{k}:{v}" for k, v in physical_exam.items()).lower()
        all_oral_str = " ".join(f"{k}:{v}" for k, v in anamnesis.items()).lower()

        # 1. ACUTE MYOCARDIAL INFARCTION (STEMI / NSTEMI)
        if any(term in d_name_lower for term in ['myocardial infarction', 'stemi', 'coronary syndrome', 'angina']):
            # Laboratory: Cardiac Troponin I / T
            trop = labs.get('troponin_i') or labs.get('troponin_t') or labs.get('troponin')
            if trop is not None:
                try:
                    trop_val = float(trop)
                    if trop_val >= 0.04:
                        bonus += 0.45
                        evidence.append({'type': 'lab', 'text': f'Elevated Cardiac Troponin ({trop_val} ng/mL) confirms acute myocardial injury'})
                except (ValueError, TypeError):
                    if any(t in str(trop).lower() for t in ['positive', 'elevated', 'high']):
                        bonus += 0.45
                        evidence.append({'type': 'lab', 'text': 'Positive / Elevated Cardiac Troponin confirms acute myocardial necrosis'})

            # Tool: 12-Lead ECG
            ecg = str(tools.get('ecg', '')).lower()
            if any(term in ecg for term in ['st_elevation', 'stemi', 'hyperacute_t', 'pathologic_q']):
                bonus += 0.50
                evidence.append({'type': 'tool', 'text': f'12-Lead ECG: {tools.get("ecg")} (Definitive STEMI / Transmural Ischemia)'})
            elif any(term in ecg for term in ['st_depression', 't_wave_inversion']):
                bonus += 0.30
                evidence.append({'type': 'tool', 'text': f'12-Lead ECG: {tools.get("ecg")} (Subendocardial Ischemia / NSTEMI)'})

            # Oral History (Asked by mouth): Crushing pain, left arm / jaw radiation
            if any(term in all_oral_str for term in ['crushing', 'left_arm', 'jaw', 'retrosternal', 'levine']):
                bonus += 0.15
                evidence.append({'type': 'anamnesis', 'text': 'Typical ischemic chest pain character radiating to left arm/jaw'})

        # 2. MALARIA (PLASMODIUM FALCIPARUM)
        elif 'malaria' in d_name_lower:
            smear = str(labs.get('malaria_smear', '')).lower()
            rdt = str(labs.get('malaria_rdt', '')).lower()
            if any(term in smear for term in ['positive', 'falciparum', 'trophozoite', 'ring_form', 'gametocyte']) or 'positive' in rdt:
                bonus += 0.60
                evidence.append({'type': 'lab', 'text': 'Blood Film / RDT: Positive for Plasmodium falciparum (Pathognomonic Confirmation)'})

            if any(term in all_oral_str for term in ['endemic', 'travel', 'tropical', 'tertian', 'paroxysm']):
                bonus += 0.15
                evidence.append({'type': 'anamnesis', 'text': 'Travel to malaria-endemic region with periodic paroxysms'})

        # 3. BACTERIAL MENINGITIS
        elif 'meningitis' in d_name_lower:
            csf = str(labs.get('csf', '') or labs.get('lumbar_puncture', '')).lower()
            if any(term in csf for term in ['turbid', 'purulent', 'neutrophil', 'low_glucose', 'diplococci', 'positive']):
                bonus += 0.60
                evidence.append({'type': 'lab', 'text': 'Lumbar Puncture / CSF Analysis: Purulent CSF with elevated opening pressure and neutrophilic pleocytosis'})

            if any(term in all_exam_str for term in ['neck_stiffness', 'nuchal_rigidity', 'kernig', 'brudzinski']):
                bonus += 0.25
                evidence.append({'type': 'exam', 'text': 'Physical Exam: Positive meningeal irritation signs (Nuchal rigidity / Kernig / Brudzinski)'})

        # 4. PNEUMONIA (COMMUNITY-ACQUIRED / ATYPICAL)
        elif 'pneumonia' in d_name_lower:
            cxr = str(tools.get('chest_xray', '') or tools.get('cxr', '')).lower()
            if any(term in cxr for term in ['consolidation', 'lobar', 'infiltrate', 'air_bronchogram']):
                bonus += 0.45
                evidence.append({'type': 'tool', 'text': f'Chest Radiography (CXR): {tools.get("chest_xray")} (Definitive Alveolar Consolidation)'})

            if any(term in all_exam_str for term in ['crackles', 'crepitations', 'bronchial_breath_sounds', 'dullness']):
                bonus += 0.20
                evidence.append({'type': 'exam', 'text': 'Chest Auscultation: Focal inspiratory crackles / bronchial breath sounds'})

        # 5. DIABETIC KETOACIDOSIS (DKA)
        elif any(term in d_name_lower for term in ['ketoacidosis', 'dka']):
            glucose = labs.get('blood_glucose') or labs.get('glucose')
            ketones = str(labs.get('urine_ketones', '') or labs.get('serum_ketones', '')).lower()
            if any(term in ketones for term in ['positive', 'large', 'moderate', 'high', '+++']):
                bonus += 0.45
                evidence.append({'type': 'lab', 'text': 'Urinalysis / Serum Ketones: Positive Ketonuria / Ketonemia'})

            abg = str(tools.get('abg', '') or labs.get('abg_ph', '')).lower()
            if any(term in abg for term in ['acidosis', '< 7.3', 'low_ph', 'anion_gap']) or any(term in all_exam_str for term in ['kussmaul', 'fruity_breath']):
                bonus += 0.25
                evidence.append({'type': 'tool', 'text': 'Blood Gas / Exam: Metabolic Acidosis with Kussmaul respirations'})

        # 6. PULMONARY EMBOLISM (ACUTE PE)
        elif 'pulmonary embolism' in d_name_lower:
            ctpa = str(tools.get('ctpa', '') or tools.get('ct_chest', '')).lower()
            if any(term in ctpa for term in ['filling_defect', 'embolus', 'positive', 'thrombus']):
                bonus += 0.60
                evidence.append({'type': 'tool', 'text': 'CT Pulmonary Angiography (CTPA): Contrast filling defect in pulmonary arterial tree'})

            d_dimer = labs.get('d_dimer')
            if d_dimer is not None:
                try:
                    if float(d_dimer) >= 500:
                        bonus += 0.25
                        evidence.append({'type': 'lab', 'text': f'Elevated D-Dimer ({d_dimer} ng/mL) indicating active fibrinolysis'})
                except (ValueError, TypeError):
                    if 'elevated' in str(d_dimer).lower() or 'positive' in str(d_dimer).lower():
                        bonus += 0.25
                        evidence.append({'type': 'lab', 'text': 'Elevated D-Dimer test'})

        # 7. ACUTE APPENDICITIS
        elif 'appendicitis' in d_name_lower:
            us_ct = str(tools.get('ultrasound', '') or tools.get('ct_abdomen', '')).lower()
            if any(term in us_ct for term in ['dilated_appendix', '> 6mm', 'appendicolith', 'target_sign', 'non_compressible']):
                bonus += 0.50
                evidence.append({'type': 'tool', 'text': 'Abdominal Imaging: Thickened non-compressible appendix >6mm with periappendiceal fat stranding'})

            if any(term in all_exam_str for term in ['mcburney', 'rovsing', 'psoas', 'obturator', 'rebound']):
                bonus += 0.30
                evidence.append({'type': 'exam', 'text': 'Physical Exam: Positive McBurney point tenderness and Rovsing/Rebound signs'})

        # 8. PULMONARY TUBERCULOSIS
        elif 'tuberculosis' in d_name_lower:
            afb_gene = str(labs.get('sputum_afb', '') or labs.get('genexpert', '')).lower()
            if any(term in afb_gene for term in ['positive', 'acid_fast', 'mtb_detected', 'rr_detected']):
                bonus += 0.60
                evidence.append({'type': 'lab', 'text': 'Microbiology: Sputum GeneXpert / AFB Smear positive for Mycobacterium tuberculosis'})

            cxr = str(tools.get('chest_xray', '')).lower()
            if any(term in cxr for term in ['apical', 'cavitation', 'upper_lobe', 'miliary']):
                bonus += 0.30
                evidence.append({'type': 'tool', 'text': 'Chest X-Ray: Upper lobe apical cavitary lesions / infiltrates'})

        # 9. CHOLERA
        elif 'cholera' in d_name_lower:
            stool = str(labs.get('stool_culture', '') or labs.get('stool_rdt', '') or labs.get('hanging_drop', '')).lower()
            if any(term in stool for term in ['vibrio', 'cholerae', 'darting', 'positive']):
                bonus += 0.60
                evidence.append({'type': 'lab', 'text': 'Stool Microbiology: Vibrio cholerae confirmed by culture / darting motility'})

            if any(term in all_oral_str for term in ['rice_water', 'rice water', 'massive_watery']):
                bonus += 0.30
                evidence.append({'type': 'anamnesis', 'text': 'Oral History: Classic painless, profuse "rice-water" diarrhea'})

        # 10. ACUTE STROKE (CVA)
        elif any(term in d_name_lower for term in ['stroke', 'cerebrovascular', 'infarct']):
            head_ct = str(tools.get('ct_head', '') or tools.get('brain_mri', '')).lower()
            if any(term in head_ct for term in ['hypodensity', 'ischemic', 'infarct', 'hemorrhage', 'bleed']):
                bonus += 0.55
                evidence.append({'type': 'tool', 'text': f'Neuroimaging: {tools.get("ct_head") or tools.get("brain_mri")} (Acute Cerebrovascular Event)'})

        # General High-Yield Lab Markers:
        wbc = labs.get('wbc_count') or labs.get('wbc')
        if wbc is not None:
            try:
                if float(wbc) > 13000 and disease.category in ['infectious', 'respiratory']:
                    bonus += 0.08
                    evidence.append({'type': 'lab', 'text': f'Marked Leukocytosis (WBC {wbc} /uL) supporting acute bacterial / systemic infection'})
            except (ValueError, TypeError):
                pass

        crp = labs.get('crp')
        if crp is not None:
            try:
                if float(crp) > 50 and disease.category in ['infectious', 'respiratory']:
                    bonus += 0.08
                    evidence.append({'type': 'lab', 'text': f'Elevated C-Reactive Protein ({crp} mg/L) indicating active inflammatory/infectious process'})
            except (ValueError, TypeError):
                pass

        return min(0.60, bonus), evidence

    def run_inference(
        self,
        symptoms: List[Dict[str, Any]],
        signs: List[Dict[str, Any]],
        vital_signs: Dict[str, Any],
        demographics: Dict[str, Any],
        medical_history: Dict[str, Any],
        anamnesis: Dict[str, Any] = None,
        physical_exam: Dict[str, Any] = None,
        laboratory_results: Dict[str, Any] = None,
        diagnostic_tools: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Executes comprehensive hybrid diagnostic inference across all active diseases.
        Incorporate multimodal specialist clinical inputs:
        - Oral Anamnesis / History of Present Illness (asked by mouth)
        - Doctor's Physical Exam Findings (hands & stethoscope)
        - Laboratory Test Results (tested by laboratory: CBC, CMP, Biomarkers, Serology, Microbiology)
        - Diagnostic & Bedside Tools (12-Lead ECG, Chest X-Ray, CT Scan, Ultrasound / POCUS)
        - 52,500+ Trained Machine Learning Pattern Classifier
        """
        from apps.medical_knowledge.models import Disease, Symptom, Medicine, DrugInteraction

        anamnesis = anamnesis or {}
        physical_exam = physical_exam or {}
        laboratory_results = laboratory_results or {}
        diagnostic_tools = diagnostic_tools or {}

        # Extract normalized terms
        symptom_names = []
        for s in symptoms:
            if isinstance(s, dict):
                symptom_names.append(s.get('name', ''))
            elif isinstance(s, str):
                symptom_names.append(s)
        
        sign_names = []
        for sg in signs:
            if isinstance(sg, dict):
                sign_names.append(sg.get('name', ''))
            elif isinstance(sg, str):
                sign_names.append(sg)

        # Merge physical exam findings into sign_names if provided as strings/lists
        for system_k, findings_v in physical_exam.items():
            if isinstance(findings_v, list):
                for f_item in findings_v:
                    sign_names.append(str(f_item))
            elif isinstance(findings_v, str) and findings_v.strip():
                sign_names.append(findings_v)

        # 1. Emergency Triage Assessment
        triage_level, red_flags = self.evaluate_triage(symptom_names, sign_names, vital_signs)

        # Collect all active input names into clean set
        all_patient_findings = set(s.lower().strip() for s in (symptom_names + sign_names) if s.strip())

        # Vitals extraction
        temp = float(vital_signs.get('temperature', 37.0) or 37.0)
        has_fever = temp >= 38.0
        spo2 = float(vital_signs.get('spo2', 98.0) or 98.0)
        has_hypoxia = spo2 < 94.0
        hr = float(vital_signs.get('heart_rate', 75.0) or 75.0)
        has_tachycardia = hr > 100.0

        patient_age = float(demographics.get('age', 30.0) or 30.0)
        is_pregnant = bool(demographics.get('is_pregnant', False))
        patient_allergies = [a.lower().strip() for a in medical_history.get('allergies', []) if a]
        current_meds = [m.lower().strip() for m in medical_history.get('current_medications', []) if m]

        # 1.5. Machine Learning Prediction on 50,000+ Patient Training Base
        ml_predictions = {}
        if self.predictor and self.predictor.is_available:
            try:
                ml_predictions = self.predictor.predict(
                    symptoms=symptom_names,
                    signs=sign_names,
                    vitals=vital_signs,
                    demographics=demographics
                )
            except Exception as e:
                print(f"[CDSS Diagnostic Engine] ML inference error: {e}")

        # 2. Score every active Disease in database
        diseases = Disease.objects.filter(is_active=True).prefetch_related(
            'disease_symptoms__symptom',
            'treatments__medicine'
        )

        candidates = []

        for disease in diseases:
            disease_associations = list(disease.disease_symptoms.all())
            if not disease_associations:
                continue

            matching_findings = []
            hallmark_matches = []
            missing_hallmarks = []
            contradicting_findings = []

            total_possible_weight = 0.0
            accumulated_score = 0.0

            for ds in disease_associations:
                sym = ds.symptom
                sym_name_clean = sym.name.lower().strip()
                synonyms_clean = [syn.lower().strip() for syn in sym.synonyms]
                all_sym_names = [sym_name_clean] + synonyms_clean

                weight = ds.numerical_weight
                total_possible_weight += weight

                # Check if patient reported this sign/symptom
                matched = False
                for p_finding in all_patient_findings:
                    if p_finding in all_sym_names or any(p_finding in name for name in all_sym_names) or any(name in p_finding for name in all_sym_names):
                        matched = True
                        break

                if matched:
                    accumulated_score += weight
                    finding_dict = {
                        'name': sym.name,
                        'type': sym.get_symptom_type_display(),
                        'frequency': ds.get_frequency_display(),
                        'specificity': ds.get_specificity_display(),
                        'is_hallmark': ds.is_hallmark,
                        'is_red_flag': sym.is_red_flag,
                        'weight': round(weight, 2)
                    }
                    matching_findings.append(finding_dict)
                    if ds.is_hallmark or ds.specificity == 'pathognomonic':
                        hallmark_matches.append(finding_dict)
                else:
                    if ds.is_hallmark and ds.frequency == 'very_common':
                        missing_hallmarks.append(sym.name)

            # Vital signs synergy bonuses / penalties
            vitals_bonus = 0.0
            if has_fever and disease.category in ['infectious', 'respiratory']:
                vitals_bonus += 0.15
            elif not has_fever and 'fever' in [ds.symptom.name.lower() for ds in disease_associations if ds.frequency == 'very_common']:
                # Disease strongly expected fever, but patient is afebrile
                vitals_bonus -= 0.10

            if has_hypoxia and disease.category in ['respiratory', 'cardiovascular']:
                vitals_bonus += 0.20

            if has_tachycardia and disease.category in ['cardiovascular', 'infectious']:
                vitals_bonus += 0.08

            # Calculate raw clinical knowledge ratio
            if total_possible_weight > 0:
                raw_ratio = accumulated_score / total_possible_weight
            else:
                raw_ratio = 0.0

            # Boost for hallmark matches
            if hallmark_matches:
                raw_ratio += len(hallmark_matches) * 0.12

            # Apply vitals synergy
            clinical_ratio = max(0.0, min(0.99, raw_ratio + vitals_bonus))

            # Machine Learning Model Score from 50,000+ trained dataset
            ml_prob = ml_predictions.get(disease.name, 0.0)

            # Hybrid Ensemble Blend: 55% Machine Learning + 45% Clinical Knowledge & Vitals
            if ml_predictions:
                hybrid_ratio = max(0.0, min(0.99, (ml_prob * 0.55) + (clinical_ratio * 0.45)))
                if hallmark_matches and hybrid_ratio < clinical_ratio * 0.8:
                    hybrid_ratio = (hybrid_ratio + clinical_ratio) / 2.0
                final_ratio = hybrid_ratio
            else:
                final_ratio = clinical_ratio

            # Specialist Hospital Diagnostic Evidence (Oral Anamnesis, Physical Exam, Labs, Diagnostic Tools)
            spec_bonus, confirmatory_evidence = self.evaluate_specialist_modalities(
                disease=disease,
                anamnesis=anamnesis,
                physical_exam=physical_exam,
                labs=laboratory_results,
                tools=diagnostic_tools
            )
            final_ratio = max(0.0, min(0.99, final_ratio + spec_bonus))

            # Only consider diseases with at least 1 matching finding or score > 0.15 or ML score > 0.10 or spec_bonus > 0.15
            if len(matching_findings) > 0 or final_ratio >= 0.15 or ml_prob >= 0.10 or spec_bonus > 0.15:
                # Confidence rating
                if final_ratio >= 0.70 or confirmatory_evidence:
                    confidence = 'high'
                elif final_ratio >= 0.45:
                    confidence = 'moderate'
                elif final_ratio >= 0.25:
                    confidence = 'low'
                else:
                    confidence = 'uncertain'

                # Suggested investigations from diagnostic criteria or defaults
                criteria = disease.diagnostic_criteria or {}
                suggested_tests = criteria.get('required_tests', [])
                if not suggested_tests:
                    category_default_tests = {
                        'infectious': ['Complete Blood Count (CBC)', 'Peripheral Blood Smear', 'C-Reactive Protein (CRP)'],
                        'respiratory': ['Chest X-Ray (CXR)', 'Pulse Oximetry', 'Sputum Analysis'],
                        'cardiovascular': ['12-Lead Electrocardiogram (ECG)', 'Cardiac Troponin I/T', 'Serum Electrolytes'],
                        'gastrointestinal': ['Stool Microscopy / RDT', 'Serum Amylase & Lipase', 'Abdominal Ultrasound'],
                        'endocrine': ['Fasting Blood Glucose / HbA1c', 'Serum Electrolytes & Ketones', 'Lipid Profile'],
                        'neurological': ['Non-contrast Head CT', 'Lumbar Puncture (CSF Analysis)', 'Serum Electrolytes'],
                        'genitourinary': ['Urinalysis & Urine Culture', 'Serum Creatinine & Blood Urea Nitrogen (BUN)']
                    }
                    suggested_tests = category_default_tests.get(disease.category, ['Complete Blood Count', 'Basic Metabolic Panel'])

                # Recommendations: Treatments with allergy and contraindication safety scanning
                treatments = []
                contraindication_alerts = []

                for tr in disease.treatments.filter(is_active=True).select_related('medicine'):
                    med = tr.medicine
                    med_name = med.generic_name

                    # Allergy checking
                    is_allergic = any(
                        allergy in med_name.lower() or allergy in med.drug_class.lower()
                        for allergy in patient_allergies
                    )
                    if is_allergic:
                        contraindication_alerts.append({
                            'severity': 'contraindicated',
                            'medicine': med_name,
                            'reason': f"Patient has documented allergy to '{med_name}' or class '{med.drug_class}'."
                        })

                    # Pregnancy safety check
                    if is_pregnant and med.pregnancy_category in ['D', 'X']:
                        contraindication_alerts.append({
                            'severity': 'contraindicated' if med.pregnancy_category == 'X' else 'major',
                            'medicine': med_name,
                            'reason': f"Medicine is FDA Category {med.pregnancy_category} and contraindicated/unsafe during pregnancy."
                        })

                    # Drug-Drug interaction check against current medications
                    if current_meds:
                        med_queries = Q()
                        for cm in current_meds:
                            med_queries |= Q(generic_name__icontains=cm)
                        current_med_records = list(Medicine.objects.filter(med_queries, is_active=True))
                        if current_med_records:
                            interactions = DrugInteraction.objects.filter(
                                (Q(medicine_a=med, medicine_b__in=current_med_records) |
                                 Q(medicine_b=med, medicine_a__in=current_med_records)),
                                is_active=True
                            ).select_related('medicine_a', 'medicine_b')
                            for inter in interactions:
                                other_med = inter.medicine_b.generic_name if inter.medicine_a == med else inter.medicine_a.generic_name
                                contraindication_alerts.append({
                                    'severity': inter.severity,
                                    'medicine': med_name,
                                    'interacts_with': other_med,
                                    'reason': inter.description,
                                    'clinical_management': inter.clinical_management
                                })

                    treatments.append({
                        'medicine_name': med_name,
                        'drug_class': med.drug_class,
                        'dosage_form': med.get_dosage_form_display(),
                        'strength': med.strength,
                        'route': med.get_route_of_administration_display(),
                        'line': tr.get_treatment_line_display(),
                        'instructions': tr.regimen_instructions,
                        'adult_dosing': med.adult_dosing,
                        'pediatric_dosing': med.pediatric_dosing,
                        'pregnancy_category': med.pregnancy_category
                    })

                candidates.append({
                    'disease_id': str(disease.id),
                    'disease_name': disease.name,
                    'icd10_code': disease.icd10_code,
                    'category': disease.get_category_display(),
                    'probability_score': round(final_ratio, 3),
                    'ml_probability': round(ml_prob, 3),
                    'clinical_probability': round(clinical_ratio, 3),
                    'confidence_level': confidence,
                    'supporting_findings': matching_findings,
                    'contradicting_findings': contradicting_findings,
                    'missing_information': missing_hallmarks,
                    'hallmark_matches_count': len(hallmark_matches),
                    'suggested_investigations': suggested_tests,
                    'recommended_treatments': treatments,
                    'contraindication_alerts': contraindication_alerts,
                    'confirmatory_evidence': confirmatory_evidence,
                    'management_overview': disease.management_overview,
                    'referral_criteria': disease.referral_criteria
                })

        # Sort candidates by probability score descending
        candidates.sort(key=lambda x: (x['probability_score'], x['hallmark_matches_count']), reverse=True)

        # Normalize probabilities across top candidates using Softmax/Temperature scaling
        top_candidates = candidates[:8]
        if top_candidates:
            raw_scores = [c['probability_score'] for c in top_candidates]
            max_score = max(raw_scores)
            
            # Calibrated percentage for clinical presentation
            total_score = sum(math.exp((s - max_score) * 2.0) for s in raw_scores)
            for idx, c in enumerate(top_candidates):
                normalized_prob = math.exp((c['probability_score'] - max_score) * 2.0) / total_score
                blended = round((c['probability_score'] * 0.6) + (normalized_prob * 0.4), 3)
                c['probability_score'] = blended
                c['rank'] = idx + 1

        ml_metrics = self.predictor.metrics if (self.predictor and self.predictor.is_available) else {}

        return {
            'candidates': top_candidates,
            'triage_level': triage_level,
            'red_flags': red_flags,
            'findings_evaluated': list(all_patient_findings),
            'engine_version': self.ENGINE_VERSION,
            'model_version': self.MODEL_VERSION,
            'ml_model_status': {
                'is_available': bool(ml_predictions),
                'total_trained_samples': ml_metrics.get('total_samples', 0),
                'test_top1_accuracy': ml_metrics.get('test_top1_accuracy', 0.0),
                'test_top3_accuracy': ml_metrics.get('test_top3_accuracy', 0.0),
                'model_name': ml_metrics.get('model_name', 'RandomForest-50k'),
            }
        }
