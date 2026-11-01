"""
Global Medical Knowledge Expansion Command.
Expands the medical knowledge base with global tertiary/specialist conditions,
advanced physical signs, laboratory markers, and WHO essential medicines.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)


class Command(BaseCommand):
    help = 'Expands the medical knowledge base with comprehensive global diseases, signs, and medicines.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Expanding Global Specialist Medical Knowledge..."))
        
        with transaction.atomic():
            s_count = self.add_specialist_symptoms()
            m_count = self.add_specialist_medicines()
            d_count = self.add_specialist_diseases()

        self.stdout.write(self.style.SUCCESS(
            f"[OK] Successfully added {s_count} specialist signs, {m_count} medicines, and {d_count} global specialist diseases!"
        ))

    def add_specialist_symptoms(self):
        new_symptoms = [
            # Cardiovascular Signs
            {"name": "Janeway Lesions & Osler Nodes", "type": "sign", "system": "cardiovascular", "red_flag": False, "weight": 2.2,
             "desc": "Non-tender erythematous macules on palms/soles (Janeway) or painful nodules on digits (Osler), pathognomonic for infective endocarditis.",
             "synonyms": ["endocarditis skin signs", "osler nodes", "janeway lesions"]},
            {"name": "New or Changing Regurgitant Heart Murmur", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 2.5,
             "desc": "Audible holosystolic or early diastolic regurgitant murmur indicative of valvular pathology or endocarditis.",
             "synonyms": ["valvular murmur", "regurgitant murmur"]},
            {"name": "Tearing Interscapular Back Pain", "type": "symptom", "system": "cardiovascular", "red_flag": True, "weight": 2.8,
             "desc": "Maximal intensity ripping or tearing chest/back pain radiating between scapulae, hallmark of aortic dissection.",
             "synonyms": ["ripping chest pain", "tearing pain", "aortic dissection pain"]},
            {"name": "Beck's Triad (Muffled Heart Sounds, JVD, Hypotension)", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 3.0,
             "desc": "Classic triad of hypotension, elevated JVP, and muffled heart sounds signifying acute cardiac tamponade.",
             "synonyms": ["becks triad", "cardiac tamponade triad", "muffled heart sounds"]},
            {"name": "Unilateral Lower Extremity Swelling & Calf Tenderness", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 2.2,
             "desc": "Asymmetric leg edema >3cm, warmth, and calf pain on dorsiflexion (Homan sign) indicating DVT.",
             "synonyms": ["deep vein thrombosis sign", "calf tenderness", "unilateral leg edema"]},

            # Respiratory / Pulmonary Signs
            {"name": "Tracheal Deviation to Contralateral Side", "type": "sign", "system": "respiratory", "red_flag": True, "weight": 3.0,
             "desc": "Physical displacement of the trachea away from the affected hemithorax, definitive sign of tension pneumothorax.",
             "synonyms": ["tracheal shift", "deviated trachea", "tension pneumothorax sign"]},
            {"name": "Pulsus Paradoxus (>10 mmHg Drop in SBP on Inspiration)", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 2.4,
             "desc": "Abnormally large decrease in systolic blood pressure during inspiration, seen in tamponade and severe asthma.",
             "synonyms": ["pulsus paradoxus", "paradoxical pulse"]},
            {"name": "Bilateral Diffuse Inspiratory 'Velcro' Crackles", "type": "sign", "system": "respiratory", "red_flag": False, "weight": 1.9,
             "desc": "Dry, fine, high-pitched end-inspiratory crackles heard over lung bases, typical of idiopathic pulmonary fibrosis.",
             "synonyms": ["velcro crackles", "fibrotic crackles"]},

            # Neurological Signs
            {"name": "Thunderclap Headache (Onset < 1 Minute)", "type": "symptom", "system": "neurological", "red_flag": True, "weight": 3.0,
             "desc": "Severe headache reaching peak maximal intensity within seconds ('worst headache of life'), hallmark of subarachnoid hemorrhage.",
             "synonyms": ["worst headache of life", "thunderclap headache", "sah headache"]},
            {"name": "Ascending Symmetrical Muscle Weakness & Areflexia", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.6,
             "desc": "Progressive motor paralysis starting in lower extremities and ascending upward with loss of deep tendon reflexes, indicative of GBS.",
             "synonyms": ["ascending paralysis", "areflexia", "guillain barre weakness"]},
            {"name": "Pinpoint Pupils (Miosis) & Salivation / Lacrimation", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.8,
             "desc": "Cholinergic toxidrome (SLUDGE) with extreme miosis, bronchorrhea, and bradycardia from organophosphate poisoning.",
             "synonyms": ["pinpoint pupils", "cholinergic toxidrome", "miosis"]},

            # Gastrointestinal & Hepatic Signs
            {"name": "Positive Murphy's Sign (Inspiratory Arrest on RUQ Palpation)", "type": "sign", "system": "gastrointestinal", "red_flag": True, "weight": 2.5,
             "desc": "Sudden arrest of deep inspiration when right subcostal margin is palpated, pathognomonic for acute cholecystitis.",
             "synonyms": ["murphy sign", "cholecystitis sign"]},
            {"name": "Gross Hematemesis / Coffee-Ground Emesis", "type": "sign", "system": "gastrointestinal", "red_flag": True, "weight": 2.8,
             "desc": "Vomiting of fresh red blood or dark coffee-ground blood from esophageal varices or bleeding peptic ulcer.",
             "synonyms": ["vomiting blood", "hematemesis", "coffee ground emesis"]},
            {"name": "Asterixis (Flapping Tremor of Outstretched Hands)", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.3,
             "desc": "Intermittent loss of muscle tone causing rhythmic flap of dorsiflexed wrists, hallmark of hepatic or uremic encephalopathy.",
             "synonyms": ["flapping tremor", "liver flap", "asterixis"]},

            # Renal & Hematology Signs
            {"name": "Severe Spasmodic Flank Pain Radiating to Groin", "type": "symptom", "system": "genitourinary", "red_flag": True, "weight": 2.4,
             "desc": "Agonizing colicky pain originating in renal angle and radiating anteroinferiorly to groin and scrotum/labia.",
             "synonyms": ["renal colic", "ureteric colic", "kidney stone pain"]},
            {"name": "Dactylitis ('Hand-Foot Syndrome' in Young Children)", "type": "sign", "system": "musculoskeletal", "red_flag": False, "weight": 2.2,
             "desc": "Painful, symmetrical swelling of hands and feet in infants with sickle cell anemia due to microvascular bone infarction.",
             "synonyms": ["hand foot syndrome", "sickle cell dactylitis"]},
            {"name": "Malar 'Butterfly' Facial Rash Sparing Nasolabial Folds", "type": "sign", "system": "dermatological", "red_flag": False, "weight": 2.4,
             "desc": "Fixed erythematous maculopapular rash over cheeks and nasal bridge with characteristic sparing of nasolabial folds in SLE.",
             "synonyms": ["malar rash", "butterfly rash", "lupus rash"]},
            {"name": "Target / Bullseye Erythema Multiforme Lesions", "type": "sign", "system": "dermatological", "red_flag": True, "weight": 2.7,
             "desc": "Concentric rings with central dusky purpura and mucosal detachment, hallmark of Stevens-Johnson Syndrome.",
             "synonyms": ["targetoid lesions", "bullseye rash", "sjs rash"]},
            {"name": "Hydrophobia & Aerophobia (Spasms on Swallowing Water)", "type": "symptom", "system": "neurological", "red_flag": True, "weight": 3.0,
             "desc": "Involuntary violent laryngeal spasms triggered by attempts to drink liquids or feeling drafts of air, pathognomonic for Rabies.",
             "synonyms": ["hydrophobia", "rabies spasms", "aerophobia"]},
            {"name": "Trismus ('Lockjaw') & Risus Sardonicus", "type": "sign", "system": "neurological", "red_flag": True, "weight": 3.0,
             "desc": "Painful tonic spasms of masseter muscles preventing mouth opening with grotesque grimacing smile from Tetanus.",
             "synonyms": ["lockjaw", "trismus", "risus sardonicus"]}
        ]

        count = 0
        for item in new_symptoms:
            obj, created = Symptom.objects.get_or_create(
                name=item["name"],
                defaults={
                    "symptom_type": item["type"],
                    "body_system": item["system"],
                    "is_red_flag": item["red_flag"],
                    "severity_weight": item["weight"],
                    "description": item["desc"],
                    "synonyms": item.get("synonyms", []),
                    "is_active": True
                }
            )
            if created:
                count += 1
        return count

    def add_specialist_medicines(self):
        new_meds = [
            {"name": "Alteplase (rt-PA)", "class": "Thrombolytic / Fibrinolytic Enzyme", "form": "injection", "route": "iv",
             "indications": ["Acute Ischemic Stroke within 4.5 hours", "Massive Pulmonary Embolism"], "contra": ["Active hemorrhage", "Recent intracranial surgery", "INR > 1.7"], "preg": "C",
             "adult": "0.9 mg/kg IV (max 90 mg) infused over 60 minutes with 10% given as bolus."},
            {"name": "Atropine Sulfate", "class": "Antimuscarinic / Anticholinergic", "form": "injection", "route": "iv",
             "indications": ["Organophosphate Poisoning", "Severe Symptomatic Bradycardia"], "contra": ["Tachycardia", "Glaucoma (relative)"], "preg": "C",
             "adult": "2 to 4 mg IV bolus every 5-10 minutes until full atropinization (dry bronchial secretions)."},
            {"name": "Pralidoxime (2-PAM)", "class": "Cholinesterase Reactivator", "form": "injection", "route": "iv",
             "indications": ["Organophosphate Poisoning (within 24-48 hours)"], "contra": ["Carbamate toxicity"], "preg": "C",
             "adult": "1 to 2 g IV infusion in 100 mL NS over 15-30 minutes, repeated after 1 hour if muscle weakness persists."},
            {"name": "Enoxaparin (LMWH)", "class": "Low Molecular Weight Heparin Anticoagulant", "form": "injection", "route": "sc",
             "indications": ["Deep Vein Thrombosis", "Pulmonary Embolism", "NSTEMI"], "contra": ["Severe thrombocytopenia", "Active bleeding"], "preg": "B",
             "adult": "1 mg/kg subcutaneously every 12 hours."},
            {"name": "Vancomycin", "class": "Glycopeptide Antibacterial", "form": "injection", "route": "iv",
             "indications": ["MRSA Infections", "Infective Endocarditis", "Bacterial Meningitis Coverage"], "contra": ["Known hypersensitivity"], "preg": "C",
             "adult": "15 to 20 mg/kg IV every 8 to 12 hours targeting trough 15-20 mcg/mL."},
            {"name": "Hydroxyurea", "class": "Ribonucleotide Reductase Inhibitor", "form": "capsule", "route": "oral",
             "indications": ["Sickle Cell Disease Vaso-occlusive Prophylaxis"], "contra": ["Severe myelosuppression", "Pregnancy"], "preg": "D",
             "adult": "15 mg/kg/day orally as single daily dose."},
            {"name": "N-Acetylcysteine (NAC)", "class": "Glutathione Precursor / Antidote", "form": "injection", "route": "iv",
             "indications": ["Acetaminophen / Paracetamol Hepatotoxicity"], "contra": ["Anaphylactoid reaction (treatable with antihistamines)"], "preg": "B",
             "adult": "150 mg/kg IV over 60 min, then 50 mg/kg over 4h, then 100 mg/kg over 16h."},
            {"name": "Labetalol", "class": "Combined Alpha- and Beta-Adrenergic Blocker", "form": "injection", "route": "iv",
             "indications": ["Aortic Dissection", "Hypertensive Emergency in Pregnancy / Eclampsia"], "contra": ["Asthma", "High-degree AV block"], "preg": "C",
             "adult": "20 mg IV slow bolus over 2 minutes, followed by 40-80 mg every 10 min (max 300 mg)."}
        ]

        count = 0
        for item in new_meds:
            obj, created = Medicine.objects.get_or_create(
                generic_name=item["name"],
                defaults={
                    "drug_class": item["class"],
                    "dosage_form": item["form"],
                    "route_of_administration": item["route"],
                    "indications": item["indications"],
                    "contraindications": item["contra"],
                    "pregnancy_category": item["preg"],
                    "adult_dosing": item["adult"],
                    "is_active": True
                }
            )
            if created:
                count += 1
        return count

    def add_specialist_diseases(self):
        new_diseases = [
            {
                "name": "Acute Aortic Dissection (Stanford Type A / B)",
                "category": "cardiovascular",
                "icd10": "I71.0",
                "def": "Tear in the aortic intima with blood surging into aortic media creating a false lumen; life-threatening cardiovascular emergency.",
                "mgmt": "Immediate systolic BP reduction to 100-120 mmHg and HR < 60 with IV Labetalol / Esmolol. Emergent cardiothoracic surgery for Type A.",
                "symptoms": [
                    ("Tearing Interscapular Back Pain", "very_common", "pathognomonic", True),
                    ("Beck's Triad (Muffled Heart Sounds, JVD, Hypotension)", "common", "highly_specific", True),
                    ("Pulsus Paradoxus (>10 mmHg Drop in SBP on Inspiration)", "occasional", "highly_specific", False)
                ],
                "meds": ["Labetalol"]
            },
            {
                "name": "Infective Endocarditis (Acute / Subacute)",
                "category": "cardiovascular",
                "icd10": "I33.0",
                "def": "Microbial infection of the endothelial surface of the heart, most commonly cardiac valves, causing vegetations.",
                "mgmt": "Prolonged bactericidal IV antimicrobial therapy for 4-6 weeks (Vancomycin + Ceftriaxone or Gentamicin). Surgical valve replacement if refractory.",
                "symptoms": [
                    ("New or Changing Regurgitant Heart Murmur", "very_common", "pathognomonic", True),
                    ("Janeway Lesions & Osler Nodes", "common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Splenomegaly", "common", "moderately_specific", False)
                ],
                "meds": ["Vancomycin", "Ceftriaxone"]
            },
            {
                "name": "Tension Pneumothorax",
                "category": "respiratory",
                "icd10": "J93.0",
                "def": "One-way valve air accumulation in pleural space causing positive intrapleural pressure, mediastinal shift, and acute obstructive shock.",
                "mgmt": "Immediate needle thoracocentesis (2nd intercostal space midclavicular line or 5th ICS anterior axillary line), followed by emergent tube thoracostomy (chest tube).",
                "symptoms": [
                    ("Tracheal Deviation to Contralateral Side", "very_common", "pathognomonic", True),
                    ("Pulsus Paradoxus (>10 mmHg Drop in SBP on Inspiration)", "common", "highly_specific", False),
                    ("Dyspnea / Shortness of Breath", "very_common", "moderately_specific", False)
                ],
                "meds": []
            },
            {
                "name": "Subarachnoid Hemorrhage (Aneurysmal SAH)",
                "category": "neurological",
                "icd10": "I60.9",
                "def": "Extravasation of blood into the subarachnoid space, typically from rupture of an intracranial berry aneurysm.",
                "mgmt": "Non-contrast Head CT followed by LP if CT negative. Airway security, BP control, Nimodipine for vasospasm prevention, emergent endovascular coiling or neurosurgical clipping.",
                "symptoms": [
                    ("Thunderclap Headache (Onset < 1 Minute)", "very_common", "pathognomonic", True),
                    ("Nuchal Rigidity (Neck Stiffness)", "very_common", "highly_specific", True),
                    ("Marked Photophobia", "common", "highly_specific", False)
                ],
                "meds": []
            },
            {
                "name": "Acute Organophosphate & Carbamate Poisoning",
                "category": "emergency",
                "icd10": "T60.0",
                "def": "Inhibition of acetylcholinesterase enzyme causing acute acetylcholine hyperstimulation across muscarinic and nicotinic receptors.",
                "mgmt": "Decontamination, immediate high-dose IV Atropine until pulmonary secretions clear, and Pralidoxime (2-PAM) for cholinesterase reactivation.",
                "symptoms": [
                    ("Pinpoint Pupils (Miosis) & Salivation / Lacrimation", "very_common", "pathognomonic", True),
                    ("Profuse Diaphoresis / Night Sweats", "very_common", "highly_specific", False)
                ],
                "meds": ["Atropine Sulfate", "Pralidoxime (2-PAM)"]
            },
            {
                "name": "Acute Cholecystitis",
                "category": "gastrointestinal",
                "icd10": "K81.0",
                "def": "Acute inflammation of the gallbladder, typically initiated by cystic duct obstruction by gallstones (calculous cholecystitis).",
                "mgmt": "NPO, IV hydration, empiric broad-spectrum antibiotics (Ceftriaxone + Metronidazole), and early laparoscopic cholecystectomy within 72 hours.",
                "symptoms": [
                    ("Positive Murphy's Sign (Inspiratory Arrest on RUQ Palpation)", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "common", "moderately_specific", False)
                ],
                "meds": ["Ceftriaxone"]
            },
            {
                "name": "Deep Vein Thrombosis (Lower Extremity DVT)",
                "category": "cardiovascular",
                "icd10": "I82.40",
                "def": "Formation of a blood clot within the deep veins of the leg, carrying high risk of embolization to the pulmonary arteries.",
                "mgmt": "Compression duplex ultrasonography. Immediate therapeutic anticoagulation with LMWH (Enoxaparin) or direct oral anticoagulant (DOAC).",
                "symptoms": [
                    ("Unilateral Lower Extremity Swelling & Calf Tenderness", "very_common", "pathognomonic", True)
                ],
                "meds": ["Enoxaparin (LMWH)"]
            },
            {
                "name": "Sickle Cell Disease (Vaso-occlusive Crisis)",
                "category": "hematology",
                "icd10": "D57.0",
                "def": "Microvascular occlusion by sickled red blood cells causing severe tissue ischemia, bone marrow infarction, and excruciating pain.",
                "mgmt": "Aggressive IV hydration, oxygen therapy if hypoxic, scheduled opioid analgesia, treatment of underlying infection, and long-term Hydroxyurea.",
                "symptoms": [
                    ("Dactylitis ('Hand-Foot Syndrome' in Young Children)", "common", "pathognomonic", True),
                    ("Severe Malaise & Fatigue", "very_common", "moderately_specific", False)
                ],
                "meds": ["Hydroxyurea"]
            },
            {
                "name": "Rabies (Encephalitic / Furious Rabies)",
                "category": "infectious",
                "icd10": "A82.0",
                "def": "Fatal acute viral encephalomyelitis caused by rabies lyssavirus, transmitted through the saliva of infected mammals.",
                "mgmt": "Palliative intensive sedation. 100% preventable with immediate Post-Exposure Prophylaxis (wound washing, rabies vaccine, and rabies immunoglobulin).",
                "symptoms": [
                    ("Hydrophobia & Aerophobia (Spasms on Swallowing Water)", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "common", "moderately_specific", False)
                ],
                "meds": []
            },
            {
                "name": "Tetanus (Generalized Clostridial Tetanus)",
                "category": "infectious",
                "icd10": "A35",
                "def": "Neurotoxin (tetanospasmin)-mediated disease caused by Clostridium tetani, causing violent autonomic hyperactivity and skeletal muscle spasms.",
                "mgmt": "Human tetanus immunoglobulin (HTIG), Metronidazole, dark/quiet ICU environment, high-dose IV Diazepam/magnesium for spasms, and airway management.",
                "symptoms": [
                    ("Trismus ('Lockjaw') & Risus Sardonicus", "very_common", "pathognomonic", True)
                ],
                "meds": []
            }
        ]

        count = 0
        for item in new_diseases:
            disease_obj, created = Disease.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "icd10_code": item["icd10"],
                    "definition": item["def"],
                    "management_overview": item["mgmt"],
                    "status": "active",
                    "is_active": True
                }
            )
            if created:
                count += 1

            # Link symptoms
            for s_name, freq, spec, is_hallmark in item["symptoms"]:
                try:
                    s_obj = Symptom.objects.get(name=s_name)
                    DiseaseSymptom.objects.get_or_create(
                        disease=disease_obj,
                        symptom=s_obj,
                        defaults={
                            "frequency": freq,
                            "specificity": spec,
                            "is_hallmark": is_hallmark
                        }
                    )
                except Symptom.DoesNotExist:
                    pass

            # Link medicines
            for m_name in item["meds"]:
                try:
                    m_obj = Medicine.objects.get(generic_name=m_name)
                    DiseaseTreatment.objects.get_or_create(
                        disease=disease_obj,
                        medicine=m_obj,
                        defaults={
                            "treatment_line": "first_line",
                            "regimen_instructions": m_obj.adult_dosing
                        }
                    )
                except Medicine.DoesNotExist:
                    pass

        return count
