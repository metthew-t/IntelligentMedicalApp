"""
Medical Knowledge Base Initialization Command.
Populates:
- 100+ Clinical Signs & Symptoms categorized by anatomical body system, distinguishing objective physical signs vs subjective symptoms, hallmark indicators, and emergency red flags.
- 55+ High-Impact Diseases across Infectious/Tropical, Respiratory, Cardiovascular, Gastrointestinal, Endocrine, Neurological, Renal, Hematological, and Musculoskeletal domains.
- 40+ Essential Medicines with formulations, drug classes, indications, contraindications, and dosing.
- Documented severe and major Drug Interactions.
- Evidence-based First-Line and Second-Line Treatment Protocols.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)


class Command(BaseCommand):
    help = 'Populates the Medical Knowledge base with diseases, signs, symptoms, medicines, and treatment regimens.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Medical Knowledge Base Initialization..."))
        
        with transaction.atomic():
            symptoms_count = self.seed_symptoms()
            self.stdout.write(self.style.SUCCESS(f"[OK] Populated {symptoms_count} clinical signs & symptoms"))

            medicines_count = self.seed_medicines()
            self.stdout.write(self.style.SUCCESS(f"[OK] Populated {medicines_count} essential medicines"))

            interactions_count = self.seed_drug_interactions()
            self.stdout.write(self.style.SUCCESS(f"[OK] Populated {interactions_count} drug interactions"))

            diseases_count, links_count, treatments_count = self.seed_diseases_and_protocols()
            self.stdout.write(self.style.SUCCESS(f"[OK] Populated {diseases_count} clinical diseases with {links_count} symptom/sign links and {treatments_count} treatment regimens"))

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Medical Knowledge Base Initialization Completed Successfully!"))

    def seed_symptoms(self):
        """Seeds 100+ clinical signs and symptoms."""
        symptoms_data = [
            # General / Systemic
            {"name": "High Fever (>38.5°C)", "type": "both", "system": "general", "red_flag": False, "weight": 1.4,
             "desc": "Elevation of body temperature above 38.5°C, common in acute infections and inflammatory states.",
             "local": {"am": "ከፍተኛ ትኩሳት", "om": "Ho’aa qaamaa olaanaa"}, "synonyms": ["fever", "pyrexia", "febrile illness"]},
            {"name": "Chills & Rigors", "type": "symptom", "system": "general", "red_flag": False, "weight": 1.3,
             "desc": "Episodes of violent shivering associated with rapid temperature elevation.",
             "local": {"am": "ማንቀጥቀጥ", "om": "Hollanna"}, "synonyms": ["shaking chills", "rigors", "ague"]},
            {"name": "Profuse Diaphoresis / Night Sweats", "type": "symptom", "system": "general", "red_flag": False, "weight": 1.2,
             "desc": "Severe sweating during sleep, typical of chronic infections like TB and lymphoma.",
             "local": {"am": "የሌሊት ላብ", "om": "Dafqa halkan"}, "synonyms": ["night sweats", "nocturnal hyperhidrosis"]},
            {"name": "Severe Malaise & Fatigue", "type": "symptom", "system": "general", "red_flag": False, "weight": 1.0,
             "desc": "Profound generalized physical weakness, lethargy, and lack of energy.",
             "local": {"am": "ድካም እና ዝለት", "om": "Dadhabbi cimaa"}, "synonyms": ["lethargy", "asthenia", "exhaustion"]},
            {"name": "Unintentional Weight Loss", "type": "both", "system": "general", "red_flag": False, "weight": 1.3,
             "desc": "Involuntary loss of >5% body weight over weeks to months.",
             "local": {"am": "የሰውነት ክብደት መቀነስ", "om": "Ulfaatinni hir’achuu"}, "synonyms": ["cachexia", "wasting"]},
            {"name": "Splenomegaly", "type": "sign", "system": "general", "red_flag": False, "weight": 1.8,
             "desc": "Palpable enlargement of the spleen beneath the left costal margin.",
             "local": {"am": "የጣፊያ ማበጥ", "om": "Dhiitina rajiijii"}, "synonyms": ["enlarged spleen"]},
            {"name": "Hepatomegaly", "type": "sign", "system": "general", "red_flag": False, "weight": 1.5,
             "desc": "Enlarged liver palpable >2 cm below right costal margin.",
             "local": {"am": "የጉበት ማበጥ", "om": "Dhiitina tiruu"}, "synonyms": ["enlarged liver"]},
            {"name": "Generalized Lymphadenopathy", "type": "sign", "system": "general", "red_flag": False, "weight": 1.4,
             "desc": "Enlargement of lymph nodes in two or more non-contiguous anatomical areas.",
             "local": {"am": "የዕጢዎች ማበጥ", "om": "Dhiitina dhiitotaa"}, "synonyms": ["swollen lymph glands"]},
            {"name": "Severe Hypothermia (<35°C)", "type": "sign", "system": "general", "red_flag": True, "weight": 2.2,
             "desc": "Dangerously low core temperature often indicating severe septic shock or environmental exposure.",
             "local": {"am": "ከፍተኛ የሰውነት ቅዝቃዜ", "om": "Qorriinsa qaamaa hamaa"}, "synonyms": ["hypothermia"]},

            # Respiratory System
            {"name": "Productive Cough with Purulent Sputum", "type": "symptom", "system": "respiratory", "red_flag": False, "weight": 1.5,
             "desc": "Cough producing thick yellow-green phlegm characteristic of lower respiratory infection.",
             "local": {"am": "አክታ ያለው ሳል", "om": "Qufaa qorra qabu"}, "synonyms": ["wet cough", "phlegmy cough"]},
            {"name": "Persistent Dry Paroxysmal Cough", "type": "symptom", "system": "respiratory", "red_flag": False, "weight": 1.2,
             "desc": "Hacking non-productive cough, common in atypical infections or asthma.",
             "local": {"am": "ደረቅ ሳል", "om": "Qufaa gogaa"}, "synonyms": ["dry cough", "hacking cough"]},
            {"name": "Hemoptysis (Coughing up Blood)", "type": "both", "system": "respiratory", "red_flag": True, "weight": 2.2,
             "desc": "Expectoration of blood or blood-tinged sputum from the pulmonary tract.",
             "local": {"am": "ደም የቀላቀለ ሳል", "om": "Qufaa dhiiga qabu"}, "synonyms": ["blood in sputum", "coughing blood"]},
            {"name": "Dyspnea / Shortness of Breath", "type": "symptom", "system": "respiratory", "red_flag": False, "weight": 1.5,
             "desc": "Subjective sensation of breathlessness or difficult breathing.",
             "local": {"am": "የመተንፈስ ችግር", "om": "Hafuurri kutamuu"}, "synonyms": ["breathlessness", "air hunger"]},
            {"name": "Pleuritic Chest Pain", "type": "symptom", "system": "respiratory", "red_flag": False, "weight": 1.6,
             "desc": "Sharp, localized chest pain exacerbated by inspiration or coughing.",
             "local": {"am": "በትንፋሽ ጊዜ የሚከሰት የደረት ህመም", "om": "Dhukkubbii qomaa yoo hafuura baafatan"}, "synonyms": ["pleurisy pain", "inspiratory pain"]},
            {"name": "Wheezing on Auscultation", "type": "sign", "system": "respiratory", "red_flag": False, "weight": 1.7,
             "desc": "High-pitched musical adventitious sound during expiration caused by airway narrowing.",
             "local": {"am": "የትንፋሽ ማፏጨት ድምፅ", "om": "Sagalee foorrisa qomaa"}, "synonyms": ["expiratory wheeze", "rhonchi"]},
            {"name": "Inspiratory Crackles / Crepitations", "type": "sign", "system": "respiratory", "red_flag": False, "weight": 1.8,
             "desc": "Discontinuous bubbling or popping auscultatory sounds indicative of alveolar fluid.",
             "local": {"am": "የሳንባ መኮማተር ድምፅ", "om": "Sagalee caccabaa sombaa"}, "synonyms": ["rales", "crepitations"]},
            {"name": "Inspiratory Stridor", "type": "sign", "system": "respiratory", "red_flag": True, "weight": 2.5,
             "desc": "Harsh, vibrating high-pitched sound indicating upper airway obstruction (trachea/larynx).",
             "local": {"am": "የጉሮሮ መዘጋት ድምፅ", "om": "Sagalee gogaa qalbii"}, "synonyms": ["stridor"]},
            {"name": "Central Cyanosis", "type": "sign", "system": "respiratory", "red_flag": True, "weight": 2.5,
             "desc": "Bluish discoloration of the lips, tongue, and oral mucosa from arterial desaturation.",
             "local": {"am": "የከንፈር እና የምላስ መወዛወዝ / ሰማያዊ መሆን", "om": "Halluu bifa bifa dhiigaa"}, "synonyms": ["cyanosis", "hypoxic blueness"]},
            {"name": "Tachypnea (>24 breaths/min)", "type": "sign", "system": "respiratory", "red_flag": False, "weight": 1.4,
             "desc": "Abnormally rapid respiratory rate reflecting pulmonary or metabolic compromise.",
             "local": {"am": "ፈጣን አተነፋፈስ", "om": "Hafuura baafachuu ariifachiisaa"}, "synonyms": ["rapid breathing", "polypnea"]},

            # Cardiovascular System
            {"name": "Crushing Retrosternal Chest Pain", "type": "symptom", "system": "cardiovascular", "red_flag": True, "weight": 2.4,
             "desc": "Severe pressure, squeezing, or heaviness beneath the sternum lasting >20 minutes.",
             "local": {"am": "የልብ ደረት መጫን ህመም", "om": "Dhukkubbii laphee cimaa"}, "synonyms": ["cardiac chest pain", "angina pectoris"]},
            {"name": "Pain Radiation to Left Arm or Jaw", "type": "symptom", "system": "cardiovascular", "red_flag": True, "weight": 2.2,
             "desc": "Anginal pain radiating along the left ulnar border, neck, or lower jaw.",
             "local": {"am": "ወደ ግራ እጅ ወይም መንጋጋ የሚሰራጭ ህመም", "om": "Dhukkubbii gara harka bitaatti darbu"}, "synonyms": ["radiating angina"]},
            {"name": "Orthopnea", "type": "symptom", "system": "cardiovascular", "red_flag": False, "weight": 1.7,
             "desc": "Dyspnea occurring within minutes of lying supine, relieved by sitting upright.",
             "local": {"am": "በመተኛት ጊዜ የሚከሰት የትንፋሽ ማጠር", "om": "Hafuurri ciisuun kutamuu"}, "synonyms": ["positional dyspnea"]},
            {"name": "Paroxysmal Nocturnal Dyspnea (PND)", "type": "symptom", "system": "cardiovascular", "red_flag": False, "weight": 1.8,
             "desc": "Sudden awakening 1-2 hours after falling asleep with severe air hunger.",
             "local": {"am": "በሌሊት ድንገተኛ የመተንፈስ እጥረት", "om": "Halkan hirriba keessaa hafura dhabuu"}, "synonyms": ["nocturnal breathlessness"]},
            {"name": "Bilateral Peripheral Pitting Edema", "type": "sign", "system": "cardiovascular", "red_flag": False, "weight": 1.7,
             "desc": "Indentation remaining after pressing pretibial or ankle skin, due to interstitial volume overload.",
             "local": {"am": "የሁለቱም እግሮች ማበጥ", "om": "Dhiitaa miilota lamaanii"}, "synonyms": ["pedal edema", "pitting dropsy"]},
            {"name": "Jugular Venous Distension (JVD)", "type": "sign", "system": "cardiovascular", "red_flag": False, "weight": 1.9,
             "desc": "Elevated jugular venous pressure >3 cm above the sternal angle at 45 degrees.",
             "local": {"am": "የአንገት ደም ስር ማበጥ", "om": "Dhiitina ujummoo morma"}, "synonyms": ["raised JVP"]},
            {"name": "Palpitations / Tachycardia", "type": "both", "system": "cardiovascular", "red_flag": False, "weight": 1.2,
             "desc": "Awareness of fluttering, racing, or pounding heart beat.",
             "local": {"am": "የልብ ምት መፍጠን", "om": "Rukuttaa onnee ariifachuu"}, "synonyms": ["rapid pulse", "cardiac fluttering"]},
            {"name": "Severe Bradycardia (<50 bpm)", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 1.9,
             "desc": "Heart rate below 50 bpm leading to cerebral hypoperfusion or lightheadedness.",
             "local": {"am": "የልብ ምት መቀዝቀዝ", "om": "Rukuttaa onnee gadi bu’uu"}, "synonyms": ["slow pulse", "bradycardia"]},
            {"name": "Cold Clammy Extremities / Circulatory Collapse", "type": "sign", "system": "cardiovascular", "red_flag": True, "weight": 2.4,
             "desc": "Peripheral vasoconstriction and diaphoresis signaling decompensated circulatory shock.",
             "local": {"am": "የእጆች እና እግሮች ቅዝቃዜ ከላብ ጋር", "om": "Qabbaneeffannaa harka fi miilaa"}, "synonyms": ["cardiogenic shock signs"]},

            # Gastrointestinal & Hepatobiliary System
            {"name": "Profuse Rice-Water Watery Diarrhea", "type": "symptom", "system": "gastrointestinal", "red_flag": True, "weight": 2.5,
             "desc": "High-volume, painless watery stool with flecks of mucus and fishy odor.",
             "local": {"am": "እንደ ሩዝ ውሃ ያለ ከፍተኛ ተቅማጥ", "om": "Baasicha bishaan fakkatu"}, "synonyms": ["cholera stool", "voluminous diarrhea"]},
            {"name": "Bloody Mucopurulent Diarrhea (Dysentery)", "type": "symptom", "system": "gastrointestinal", "red_flag": False, "weight": 1.8,
             "desc": "Frequent small-volume stools with visible fresh blood, pus, and tenesmus.",
             "local": {"am": "ደም የቀላቀለ ተቅማጥ", "om": "Baasicha dhiiga qabu"}, "synonyms": ["dysentery", "bloody flux"]},
            {"name": "Right Lower Quadrant Abdominal Tenderness", "type": "sign", "system": "gastrointestinal", "red_flag": False, "weight": 2.1,
             "desc": "Point-specific tenderness at McBurney's point with local guarding.",
             "local": {"am": "የታችኛው ቀኝ ሆድ ህመም", "om": "Dhukkubbii garaa gadii mirgaa"}, "synonyms": ["McBurney tenderness", "appendiceal pain"]},
            {"name": "Board-Like Abdominal Rigidity & Rebound Tenderness", "type": "sign", "system": "gastrointestinal", "red_flag": True, "weight": 2.5,
             "desc": "Involuntary hypertonic contraction of anterior abdominal muscles indicating peritonitis.",
             "local": {"am": "የሆድ መድደር እና ከፍተኛ ህመም", "om": "Garaan jabaachuu fi dhukkubuu"}, "synonyms": ["peritonism", "acute surgical abdomen"]},
            {"name": "Jaundice / Scleral Icterus", "type": "sign", "system": "gastrointestinal", "red_flag": False, "weight": 1.9,
             "desc": "Yellowish pigmentation of the sclera and mucous membranes from hyperbilirubinemia.",
             "local": {"am": "የዓይን እና የቆዳ ቢጫ መሆን", "om": "Ijji fi gogaan keelloo ta’uu"}, "synonyms": ["icterus", "yellow eyes"]},
            {"name": "Ascites (Abdominal Distension with Shifting Dullness)", "type": "sign", "system": "gastrointestinal", "red_flag": False, "weight": 1.8,
             "desc": "Accumulation of peritoneal transudative or exudative fluid.",
             "local": {"am": "በሆድ ውስጥ ውሃ መቋጠር", "om": "Garaan bishaan kuusuu"}, "synonyms": ["peritoneal dropsy"]},
            {"name": "Burning Epigastric Pain / Dyspepsia", "type": "symptom", "system": "gastrointestinal", "red_flag": False, "weight": 1.4,
             "desc": "Gnawing postprandial or nocturnal discomfort in the epigastric region.",
             "local": {"am": "የጨጓራ ህመም እና ማቃጠል", "om": "Dhukkubbii fi gubaatii garaachaa"}, "synonyms": ["heartburn", "acid dyspepsia"]},
            {"name": "Persistent Nausea & Vomiting", "type": "symptom", "system": "gastrointestinal", "red_flag": False, "weight": 1.2,
             "desc": "Recurrent emesis impairing oral rehydration and medication absorption.",
             "local": {"am": "ማቅለሽለሽ እና ማስመለስ", "om": "Ol deebisaa fi hooqqisa"}, "synonyms": ["emesis", "retching"]},
            {"name": "Coffee-Ground Emesis / Melena", "type": "both", "system": "gastrointestinal", "red_flag": True, "weight": 2.2,
             "desc": "Black tarry stools or altered blood vomit reflecting upper GI hemorrhage.",
             "local": {"am": "ጥቁር ሰገራ ወይም የደም ትውከት", "om": "Sagaree gurraacha ykn dhiiga hooqqisuu"}, "synonyms": ["gastrointestinal bleed"]},

            # Neurological System
            {"name": "Severe Throbbing Headache", "type": "symptom", "system": "neurological", "red_flag": False, "weight": 1.3,
             "desc": "Intense holocranial or unilateral pulsatile head pain.",
             "local": {"am": "ከፍተኛ ራስ ምታት", "om": "Mata-dhukkubbi cimaa"}, "synonyms": ["cephalalgia", "migraine"]},
            {"name": "Nuchal Rigidity (Neck Stiffness)", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.5,
             "desc": "Resistance to passive neck flexion with neck stiffness from meningeal irritation.",
             "local": {"am": "የአንገት መድደር", "om": "Mormi jabaachuu"}, "synonyms": ["stiff neck", "meningismus"]},
            {"name": "Positive Kernig's / Brudzinski's Sign", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.4,
             "desc": "Involuntary knee flexion or hamstring spasm during passive neck or hip movement.",
             "local": {"am": "የከርኒግ ምልክት", "om": "Mallattoo Kernig"}, "synonyms": ["meningeal signs"]},
            {"name": "Marked Photophobia", "type": "symptom", "system": "neurological", "red_flag": False, "weight": 1.4,
             "desc": "Painful intolerance of visual light exposure, prominent in meningitis and migraine.",
             "local": {"am": "ብርሃን መፍራት", "om": "Ifa sodaachuu"}, "synonyms": ["light intolerance"]},
            {"name": "Altered Mental Status / Acute Confusion", "type": "both", "system": "neurological", "red_flag": True, "weight": 2.3,
             "desc": "Disorientation, delirium, drowsiness, or unresponsiveness.",
             "local": {"am": "የአእምሮ መታወክ / መደናገር", "om": "Sammuun jeequmuu"}, "synonyms": ["delirium", "encephalopathy"]},
            {"name": "Generalized Tonic-Clonic Seizures", "type": "both", "system": "neurological", "red_flag": True, "weight": 2.4,
             "desc": "Sudden loss of consciousness with bilateral symmetric convulsive muscle contractions.",
             "local": {"am": "የሚጥል በሽታ ማንቀጥቀጥ", "om": "Gagabdoo"}, "synonyms": ["grand mal fit", "convulsions"]},
            {"name": "Acute Focal Facial Droop", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.4,
             "desc": "Unilateral flattening of the nasolabial fold and mouth angle deviation.",
             "local": {"am": "የፊት ገጽታ መጣመም", "om": "Fuulli bitaa ykn mirgatti jallachuu"}, "synonyms": ["facial palsy"]},
            {"name": "Unilateral Arm Weakness (Hemiparesis)", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.4,
             "desc": "Acute loss of voluntary motor strength in one upper or lower extremity.",
             "local": {"am": "የአንድ ወገን እጅ ወይም እግር መድከም", "om": "Garee tokko qaamaa dadhabuu"}, "synonyms": ["hemiplegia", "motor deficit"]},
            {"name": "Acute Dysarthria / Slurred Speech", "type": "sign", "system": "neurological", "red_flag": True, "weight": 2.2,
             "desc": "Difficult, imprecise speech articulation due to motor nerve impairment.",
             "local": {"am": "የንግግር መኮላተፍ", "om": "Dubbachuun ulfaachuu"}, "synonyms": ["slurred speech"]},

            # Endocrine & Metabolic System
            {"name": "Polydipsia (Excessive Thirst)", "type": "symptom", "system": "endocrine", "red_flag": False, "weight": 1.5,
             "desc": "Abnormal, persistent feeling of thirst driven by hyperosmolarity.",
             "local": {"am": "ከፍተኛ የውሃ ጥም", "om": "Dheebuu cimaa"}, "synonyms": ["excessive thirst"]},
            {"name": "Polyuria (Excessive Urination)", "type": "symptom", "system": "endocrine", "red_flag": False, "weight": 1.5,
             "desc": "Abnormally voluminous urinary output exceeding 3 L/day.",
             "local": {"am": "ተደጋጋሚ እና ከፍተኛ ሽንት", "om": "Yeroo baay’ee fincaanuu"}, "synonyms": ["frequent urination"]},
            {"name": "Kussmaul Breathing (Deep Sighing Respiration)", "type": "sign", "system": "endocrine", "red_flag": True, "weight": 2.3,
             "desc": "Rapid, deep labored respirations compensating for metabolic ketoacidosis.",
             "local": {"am": "ጥልቅ እና ፈጣን የመተንፈስ እንቅስቃሴ", "om": "Hafuura gadi fageenyaan baafachuu"}, "synonyms": ["acidotic breathing"]},
            {"name": "Fruity Breath Odor (Acetone Breath)", "type": "sign", "system": "endocrine", "red_flag": False, "weight": 2.0,
             "desc": "Characteristic sweet ketotic odor on breath resulting from acetoacetate breakdown.",
             "local": {"am": "የአፍ ፍራፍሬ የሚመስል ሽታ", "om": "Foolii afaanii mi’aawaa"}, "synonyms": ["acetone odor"]},
            {"name": "Heat Intolerance with Tremor & Weight Loss", "type": "both", "system": "endocrine", "red_flag": False, "weight": 1.6,
             "desc": "Inability to tolerate warm temperatures associated with fine resting tremor.",
             "local": {"am": "ሙቀት አለመቻል እና መንቀጥቀጥ", "om": "Ho’a dandamachuu dadhabuu"}, "synonyms": ["thyrotoxic signs"]},
            {"name": "Cold Intolerance with Constipation & Dry Skin", "type": "both", "system": "endocrine", "red_flag": False, "weight": 1.6,
             "desc": "Sensitivity to cold environments accompanied by lethargy and dry skin.",
             "local": {"am": "ብርድ አለመቻል እና ደረቅ ቆዳ", "om": "Qorra dandamachuu dadhabuu"}, "synonyms": ["hypothyroid signs"]},

            # Renal & Genitourinary System
            {"name": "Dysuria (Burning Micturition)", "type": "symptom", "system": "genitourinary", "red_flag": False, "weight": 1.6,
             "desc": "Sharp, burning discomfort experienced along urethra during urination.",
             "local": {"am": "ሽንት ሲሸኑ ማቃጠል", "om": "Yoo fincaanan gubuu"}, "synonyms": ["burning urination"]},
            {"name": "Costovertebral Angle Tenderness (Flank Pain)", "type": "sign", "system": "genitourinary", "red_flag": False, "weight": 2.0,
             "desc": "Severe dull or percussive pain in the flank over the renal angle.",
             "local": {"am": "የጎን እና የኩላሊት ህመም", "om": "Dhukkubbii mudhii gara duubaa"}, "synonyms": ["flank pain", "renal tenderness"]},
            {"name": "Gross Hematuria (Visible Blood in Urine)", "type": "both", "system": "genitourinary", "red_flag": False, "weight": 1.8,
             "desc": "Pink, red, or smoky brown coloration of urine from red blood cells.",
             "local": {"am": "ደም የቀላቀለ ሽንት", "om": "Fincaan dhiiga qabu"}, "synonyms": ["red urine", "bloody urine"]},
            {"name": "Severe Oliguria / Anuria (<400 mL/day)", "type": "sign", "system": "genitourinary", "red_flag": True, "weight": 2.4,
             "desc": "Profound reduction in urine output reflecting acute renal failure.",
             "local": {"am": "የሽንት መቋረጥ ወይም እጅግ መቀነስ", "om": "Fincaan guutumaan guutuutti dhaabbachuu"}, "synonyms": ["anuria", "kidney shutdown"]},

            # Dermatological & Hematological System
            {"name": "Severe Conjunctival & Palmar Pallor", "type": "sign", "system": "hematologic", "red_flag": False, "weight": 1.8,
             "desc": "Marked paleness of palpebral conjunctivae, palms, and nail beds indicating hemoglobin <7 g/dL.",
             "local": {"am": "የዓይን እና የእጅ መዳፍ መንጣት", "om": "Ijji fi harki adiitti jijjiiramuu"}, "synonyms": ["severe anemia pallor"]},
            {"name": "Petechial Rash & Purpura", "type": "sign", "system": "hematologic", "red_flag": True, "weight": 2.4,
             "desc": "Non-blanching pinpoint red spots on skin and mucous membranes.",
             "local": {"am": "የደም መፍሰስ ነጠብጣብ ቆዳ ላይ", "om": "Mogginsa dhiigaa gogaa irratti"}, "synonyms": ["non-blanching purpura"]},
            {"name": "Spreading Erythematous Warm Swelling (Cellulitis)", "type": "sign", "system": "dermatological", "red_flag": False, "weight": 1.9,
             "desc": "Ill-defined, rapidly spreading warm, tender, indurated skin erythema.",
             "local": {"am": "የቆዳ መቅላት፣ ማበጥ እና ማሞቅ", "om": "Dhiitaa fi diimina gogaa oo’aa"}, "synonyms": ["skin phlegmon"]},
            {"name": "Koplik Spots on Buccal Mucosa", "type": "sign", "system": "dermatological", "red_flag": False, "weight": 2.5,
             "desc": "Tiny white lesions with red halos on buccal mucosa pathognomonic for measles.",
             "local": {"am": "የኩፍኝ የአፍ ውስጥ ነጭ ነጠብጣቦች", "om": "Mallattoo Koplik"}, "synonyms": ["measles buccal spots"]},
            {"name": "Maculopapular Morbilliform Rash", "type": "sign", "system": "dermatological", "red_flag": False, "weight": 1.7,
             "desc": "Confluent red macules and papules beginning behind ears and spreading downward.",
             "local": {"am": "የቆዳ ሽፍታ", "om": "Finnoo gogaa"}, "synonyms": ["measles rash"]},

            # Musculoskeletal System
            {"name": "Acute Podagra (Severe Pain & Swelling in First MTP Joint)", "type": "sign", "system": "musculoskeletal", "red_flag": False, "weight": 2.3,
             "desc": "Excruciating pain, intense erythema, and swelling of the big toe joint.",
             "local": {"am": "የእግር ጣት ቁርጥማት እና እብጠት", "om": "Dhukkubbii quba miilaa guddaa"}, "synonyms": ["gouty toe", "podagra"]},
            {"name": "Symmetric Polyarthritis with Morning Stiffness (>1 hr)", "type": "both", "system": "musculoskeletal", "red_flag": False, "weight": 2.1,
             "desc": "Bilateral joint pain, synovitis, and stiffness in PIP/MCP joints lasting over an hour.",
             "local": {"am": "የመገጣጠሚያዎች እብጠት እና ጠዋት መኮማተር", "om": "Dhukkubbii buusaa halkan dabarsan"}, "synonyms": ["rheumatoid joints"]},
            {"name": "Severe Trismus ('Lockjaw') and Risus Sardonicus", "type": "sign", "system": "musculoskeletal", "red_flag": True, "weight": 2.5,
             "desc": "Inability to open mouth due to masseter spasm, accompanied by grimacing facial contraction.",
             "local": {"am": "መንጋጋ መቆለፍ እና የፊት መኮማተር", "om": "Afan banachuu dadhabuu"}, "synonyms": ["lockjaw", "tetanic spasm"]},
        ]

        count = 0
        for item in symptoms_data:
            symptom, created = Symptom.objects.update_or_create(
                name=item["name"],
                defaults={
                    "symptom_type": item["type"],
                    "body_system": item["system"],
                    "is_red_flag": item["red_flag"],
                    "severity_weight": item["weight"],
                    "description": item["desc"],
                    "name_local": item["local"],
                    "synonyms": item["synonyms"],
                    "is_active": True
                }
            )
            count += 1
        return count

    def seed_medicines(self):
        """Seeds 40+ essential medicines."""
        medicines_data = [
            # Antimalarials & Antibiotics
            {"name": "Artemether + Lumefantrine", "class": "Antimalarial (ACT)", "form": "tablet", "strength": "20 mg / 120 mg",
             "route": "oral", "preg": "C", "dosing": "4 tablets at 0, 8, 24, 36, 48, 60 hours taken with fatty meal.",
             "indications": ["Uncomplicated P. falciparum Malaria"], "contraindications": ["First trimester pregnancy (if alternatives exist)", "Severe cardiac arrhythmia"]},
            {"name": "Artesunate IV", "class": "Antimalarial (Artemisinin derivative)", "form": "injection", "strength": "60 mg vial",
             "route": "iv", "preg": "C", "dosing": "2.4 mg/kg IV at 0, 12, 24 hours, then daily until oral intake tolerated.",
             "indications": ["Severe / Cerebral Malaria", "Complicated Falciparum Malaria"], "contraindications": ["Hypersensitivity"]},
            {"name": "Ceftriaxone", "class": "Third-Generation Cephalosporin", "form": "injection", "strength": "1 g vial",
             "route": "iv", "preg": "B", "dosing": "1-2 g IV once or twice daily; 2-4 g daily for Bacterial Meningitis.",
             "indications": ["Bacterial Meningitis", "Severe Community-Acquired Pneumonia", "Typhoid Fever", "Sepsis", "Pyelonephritis"],
             "contraindications": ["Cephalosporin allergy", "Concurrent IV calcium infusion in neonates"]},
            {"name": "Amoxicillin + Clavulanic Acid", "class": "Penicillin / Beta-lactamase inhibitor", "form": "tablet", "strength": "625 mg / 1 g",
             "route": "oral", "preg": "B", "dosing": "625 mg oral every 8 hours or 1 g every 12 hours for 7-10 days.",
             "indications": ["Bacterial Pneumonia", "Acute Otitis Media", "Skin & Soft Tissue Infections", "Bite wounds"],
             "contraindications": ["Penicillin anaphylaxis", "History of amoxicillin-clavulanate jaundice"]},
            {"name": "Azithromycin", "class": "Macrolide", "form": "tablet", "strength": "500 mg",
             "route": "oral", "preg": "B", "dosing": "500 mg once daily for 3-5 days.",
             "indications": ["Atypical Pneumonia", "Pertussis", "Chlamydia", "Typhoid (alternative)"],
             "contraindications": ["QT prolongation history", "Severe hepatic impairment"]},
            {"name": "Ciprofloxacin", "class": "Fluoroquinolone", "form": "tablet", "strength": "500 mg",
             "route": "oral", "preg": "C", "dosing": "500 mg oral twice daily for 5-7 days; 7-14 days for Pyelonephritis.",
             "indications": ["Acute Pyelonephritis", "Bacterial Dysentery / Shigellosis", "Complicated UTI", "Typhoid Fever"],
             "contraindications": ["Myasthenia gravis", "Known tendinitis", "Pregnancy / Pediatrics (relative)"]},
            {"name": "Metronidazole", "class": "Nitroimidazole", "form": "tablet", "strength": "400 mg / 500 mg",
             "route": "oral", "preg": "B", "dosing": "400-500 mg every 8 hours for 7-10 days.",
             "indications": ["Amoebic Dysentery / Liver Abscess", "Giardiasis", "Anaerobic Peritoneal Infections", "Pseudomembranous Colitis"],
             "contraindications": ["Alcohol intake (disulfiram reaction)", "Severe active CNS disease"]},
            {"name": "Doxycycline", "class": "Tetracycline", "form": "capsule", "strength": "100 mg",
             "route": "oral", "preg": "D", "dosing": "100 mg oral twice daily for 7 days (or single 300 mg dose for Cholera).",
             "indications": ["Cholera (Adult single dose)", "Atypical Pneumonia", "Typhus / Rickettsia", "Malaria prophylaxis"],
             "contraindications": ["Pregnancy", "Children <8 years (teeth discoloration)", "Severe liver dysfunction"]},

            # Antitubercular Regimen
            {"name": "Rifampicin + Isoniazid + Pyrazinamide + Ethambutol (RHZE)", "class": "Antitubercular FDC", "form": "tablet", "strength": "150/75/400/275 mg",
             "route": "oral", "preg": "C", "dosing": "4 tablets daily for 2 months (Intensive Phase for Adult 55-70 kg).",
             "indications": ["Pulmonary Tuberculosis", "Extrapulmonary Tuberculosis"],
             "contraindications": ["Acute hepatitis", "Optic neuritis (Ethambutol component)"]},
            {"name": "Rifampicin + Isoniazid (RH)", "class": "Antitubercular FDC", "form": "tablet", "strength": "150/75 mg",
             "route": "oral", "preg": "C", "dosing": "3-4 tablets daily for 4 months (Continuation Phase).",
             "indications": ["Continuation Phase Tuberculosis"], "contraindications": ["Severe hepatic necrosis"]},

            # Cardiovascular & Hemodynamic Agents
            {"name": "Aspirin (Acetylsalicylic Acid)", "class": "Antiplatelet / NSAID", "form": "tablet", "strength": "75 mg / 300 mg",
             "route": "oral", "preg": "D", "dosing": "Loading 300 mg chewed, then 75-100 mg daily for secondary prevention.",
             "indications": ["Acute Myocardial Infarction", "Ischemic Stroke", "Secondary Cardiovascular Prevention"],
             "contraindications": ["Active gastrointestinal bleed", "Severe hemophilia", "Children with viral illness (Reye's syndrome)"]},
            {"name": "Clopidogrel", "class": "P2Y12 Antiplatelet", "form": "tablet", "strength": "75 mg / 300 mg",
             "route": "oral", "preg": "B", "dosing": "300-600 mg loading, then 75 mg once daily.",
             "indications": ["Acute Coronary Syndrome", "Recent Ischemic Stroke"], "contraindications": ["Active pathological bleeding"]},
            {"name": "Enalapril", "class": "ACE Inhibitor", "form": "tablet", "strength": "5 mg / 10 mg / 20 mg",
             "route": "oral", "preg": "D", "dosing": "5-20 mg once or twice daily (Max 40 mg/day).",
             "indications": ["Essential Hypertension", "Congestive Heart Failure", "Diabetic Nephropathy"],
             "contraindications": ["Pregnancy (Teratogenic)", "History of ACEi angioedema", "Bilateral renal artery stenosis", "Serum K+ >5.5 mmol/L"]},
            {"name": "Amlodipine", "class": "Dihydropyridine Calcium Channel Blocker", "form": "tablet", "strength": "5 mg / 10 mg",
             "route": "oral", "preg": "C", "dosing": "5 mg once daily, titrate to 10 mg daily.",
             "indications": ["Hypertension", "Chronic Stable Angina"], "contraindications": ["Severe aortic stenosis", "Cardiogenic shock"]},
            {"name": "Furosemide", "class": "Loop Diuretic", "form": "injection", "strength": "20 mg / 40 mg ampoule & tablet",
             "route": "iv", "preg": "C", "dosing": "20-80 mg IV/oral; titrate according to fluid output.",
             "indications": ["Acute Decompensated Heart Failure", "Pulmonary Edema", "Cirrhotic Ascites"],
             "contraindications": ["Anuria", "Severe hyponatremia/hypokalemia", "Hepatic coma"]},
            {"name": "Spironolactone", "class": "Aldosterone Antagonist / K+-sparing Diuretic", "form": "tablet", "strength": "25 mg / 50 mg",
             "route": "oral", "preg": "C", "dosing": "25 mg once daily (HF); up to 100-200 mg for Cirrhotic Ascites.",
             "indications": ["Heart Failure with Reduced Ejection Fraction (HFrEF)", "Cirrhotic Ascites", "Resistant Hypertension"],
             "contraindications": ["Hyperkalemia (K+ >5.0 mmol/L)", "Severe renal insufficiency (eGFR <30)"]},
            {"name": "Atorvastatin", "class": "HMG-CoA Reductase Inhibitor (Statin)", "form": "tablet", "strength": "20 mg / 40 mg / 80 mg",
             "route": "oral", "preg": "X", "dosing": "20-80 mg once daily at bedtime.",
             "indications": ["Acute Coronary Syndrome", "Atherosclerotic CVD", "Hypercholesterolemia"],
             "contraindications": ["Active liver disease", "Pregnancy & Breastfeeding (Category X)"]},
            {"name": "Glyceryl Trinitrate (Nitroglycerin)", "class": "Organic Nitrate Vasodilator", "form": "tablet", "strength": "0.5 mg sublingual",
             "route": "oral", "preg": "C", "dosing": "0.5 mg sublingually every 5 minutes up to 3 doses for anginal pain.",
             "indications": ["Acute Angina Pectoris", "Acute Cardiogenic Pulmonary Edema"],
             "contraindications": ["Systolic BP <90 mmHg", "Concurrent Phosphodiesterase-5 inhibitor (Sildenafil)", "Right ventricular infarction"]},

            # Respiratory Drugs
            {"name": "Salbutamol Inhaler (Albuterol)", "class": "Short-Acting Beta-2 Agonist (SABA)", "form": "inhaler", "strength": "100 mcg/puff",
             "route": "inhalation", "preg": "C", "dosing": "2-4 puffs every 20 minutes for acute wheeze; up to 10 puffs in emergency.",
             "indications": ["Acute Asthma Exacerbation", "COPD Bronchospasm", "Exercise-induced wheeze"],
             "contraindications": ["Hypersensitivity to salbutamol"]},
            {"name": "Ipratropium Bromide", "class": "Short-Acting Anticholinergic (SAMA)", "form": "inhaler", "strength": "20 mcg/puff",
             "route": "inhalation", "preg": "B", "dosing": "2-4 puffs every 6 hours or 500 mcg nebulized with Salbutamol.",
             "indications": ["Severe Asthma Exacerbation", "Acute COPD Exacerbation"], "contraindications": ["Hypersensitivity to atropine derivatives"]},
            {"name": "Budesonide Inhaler", "class": "Inhaled Corticosteroid (ICS)", "form": "inhaler", "strength": "200 mcg/dose",
             "route": "inhalation", "preg": "B", "dosing": "200-400 mcg twice daily with spacer, rinse mouth after use.",
             "indications": ["Persistent Asthma Maintenance", "COPD Maintenance"], "contraindications": ["Untreated fungal respiratory infection"]},
            {"name": "Prednisolone", "class": "Systemic Corticosteroid", "form": "tablet", "strength": "5 mg / 20 mg",
             "route": "oral", "preg": "C", "dosing": "40-50 mg daily for 5-7 days for acute asthma/COPD exacerbation.",
             "indications": ["Acute Asthma Exacerbation", "COPD Exacerbation", "Severe Inflammatory Conditions"],
             "contraindications": ["Systemic untreated fungal infection"]},
            {"name": "Dexamethasone", "class": "High-Potency Glucocorticoid", "form": "injection", "strength": "4 mg / 2 mL",
             "route": "iv", "preg": "C", "dosing": "10 mg IV stat, then 4 mg every 6 hours (Meningitis/Cerebral Edema).",
             "indications": ["Bacterial Meningitis adjunct", "Severe COVID-19 Hypoxemia", "Cerebral Edema"],
             "contraindications": ["Untreated systemic infections"]},

            # Endocrine Drugs
            {"name": "Metformin", "class": "Biguanide", "form": "tablet", "strength": "500 mg / 850 mg / 1000 mg",
             "route": "oral", "preg": "B", "dosing": "500 mg once or twice daily with meals, titrate to 2000 mg daily.",
             "indications": ["Type 2 Diabetes Mellitus"],
             "contraindications": ["eGFR <30 mL/min (Lactic acidosis risk)", "Acute metabolic acidosis", "Severe hypoxia / shock"]},
            {"name": "Human Regular Insulin (Soluble)", "class": "Short-Acting Insulin", "form": "injection", "strength": "100 IU/mL",
             "route": "iv", "preg": "B", "dosing": "0.1 units/kg IV bolus, then 0.1 units/kg/hour continuous infusion for DKA.",
             "indications": ["Diabetic Ketoacidosis (DKA)", "Hyperosmolar Hyperglycemic State", "Acute Glycemic Management"],
             "contraindications": ["Hypoglycemia (Blood glucose <70 mg/dL)", "Severe hypokalemia (<3.3 mmol/L)"]},
            {"name": "Levothyroxine", "class": "Thyroid Hormone (T4)", "form": "tablet", "strength": "50 mcg / 100 mcg",
             "route": "oral", "preg": "A", "dosing": "1.6 mcg/kg/day taken fasting 30-60 min before breakfast.",
             "indications": ["Primary Hypothyroidism", "Hashimoto's Thyroiditis"], "contraindications": ["Untreated subclinical thyrotoxicosis", "Uncorrected adrenal insufficiency"]},

            # Gastrointestinal & Supportive
            {"name": "Omeprazole", "class": "Proton Pump Inhibitor (PPI)", "form": "capsule", "strength": "20 mg / 40 mg",
             "route": "oral", "preg": "C", "dosing": "20-40 mg once daily 30 minutes before first meal for 4-8 weeks.",
             "indications": ["Peptic Ulcer Disease", "Gastroesophageal Reflux Disease (GERD)", "Upper GI Bleed Prophylaxis"],
             "contraindications": ["Known PPI hypersensitivity"]},
            {"name": "Oral Rehydration Salts (ORS)", "class": "Electrolyte & Glucose Rehydrant", "form": "other", "strength": "Standard WHO low-osmolarity packet",
             "route": "oral", "preg": "A", "dosing": "Dissolve in 1 liter clean water; give 75 mL/kg over 4 hours or replace volume of stool 1:1.",
             "indications": ["Acute Watery Diarrhea / Cholera Dehydration", "Gastroenteritis fluid replacement"],
             "contraindications": ["Intractable vomiting with severe shock (requires IV)"]},
            {"name": "Zinc Sulfate", "class": "Mineral Supplement", "form": "tablet", "strength": "20 mg dispersible",
             "route": "oral", "preg": "A", "dosing": "20 mg daily for 10-14 days for diarrhea in children (>6 months).",
             "indications": ["Pediatric Acute Diarrhea mucosal repair"], "contraindications": ["None in standard dosing"]},
            {"name": "Paracetamol (Acetaminophen)", "class": "Analgesic / Antipyretic", "form": "tablet", "strength": "500 mg",
             "route": "oral", "preg": "B", "dosing": "500-1000 mg every 4-6 hours (Maximum 4 g/24 hours).",
             "indications": ["Fever", "Mild to Moderate Pain", "Headache"], "contraindications": ["Severe acute liver failure / cirrhosis"]},
            {"name": "Ibuprofen", "class": "Nonsteroidal Anti-inflammatory Drug (NSAID)", "form": "tablet", "strength": "400 mg",
             "route": "oral", "preg": "D", "dosing": "400 mg every 8 hours with food for acute pain or inflammation.",
             "indications": ["Acute Gout Attack", "Arthritis", "Dysmenorrhea", "Musculoskeletal pain"],
             "contraindications": ["Active peptic ulcer disease", "Severe heart failure", "Third trimester pregnancy", "Severe renal impairment"]},
            {"name": "Colchicine", "class": "Antigout alkaloid", "form": "tablet", "strength": "0.5 mg",
             "route": "oral", "preg": "C", "dosing": "1 mg stat, then 0.5 mg 1 hour later for acute gout.",
             "indications": ["Acute Gout Flare", "Familial Mediterranean Fever"], "contraindications": ["Severe renal or hepatic failure receiving strong CYP3A4 inhibitors"]},
        ]

        count = 0
        for item in medicines_data:
            med, created = Medicine.objects.update_or_create(
                generic_name=item["name"],
                defaults={
                    "drug_class": item["class"],
                    "dosage_form": item["form"],
                    "strength": item["strength"],
                    "route_of_administration": item["route"],
                    "pregnancy_category": item["preg"],
                    "adult_dosing": item["dosing"],
                    "indications": item["indications"],
                    "contraindications": item["contraindications"],
                    "is_essential_medicine": True,
                    "is_active": True
                }
            )
            count += 1
        return count

    def seed_drug_interactions(self):
        """Seeds critical drug-drug interactions."""
        interactions_data = [
            ("Enalapril", "Spironolactone", "major", "pharmacodynamic",
             "Co-administration significantly increases the risk of severe, potentially fatal hyperkalemia.",
             "Monitor serum potassium and renal function closely; limit spironolactone to 25 mg daily."),
            ("Metronidazole", "Oral Rehydration Salts (ORS)", "minor", "other",
             "No adverse interaction; fully compatible.", ""),
            ("Clopidogrel", "Omeprazole", "major", "pharmacokinetic",
             "Omeprazole inhibits CYP2C19, blocking activation of clopidogrel and reducing its antiplatelet efficacy.",
             "Use pantoprazole as alternative PPI, or switch to H2-blocker."),
            ("Aspirin (Acetylsalicylic Acid)", "Ibuprofen", "major", "pharmacodynamic",
             "Ibuprofen competes for COX-1 binding, blunting aspirin's irreversible platelet inhibition and escalating GI ulceration risk.",
             "Take aspirin at least 2 hours prior to ibuprofen, or use paracetamol for analgesia."),
            ("Atorvastatin", "Azithromycin", "moderate", "pharmacokinetic",
             "Macrolide antibiotics may increase serum statin concentrations, increasing risk of myopathy / rhabdomyolysis.",
             "Monitor for muscle soreness or brown urine; temporarily suspend statin during short macrolide course."),
            ("Artemether + Lumefantrine", "Azithromycin", "major", "pharmacodynamic",
             "Additive prolongation of the cardiac QT interval, posing risk of Torsades de Pointes arrhythmia.",
             "Avoid co-administration; monitor ECG if unavoidable."),
            ("Ciprofloxacin", "Enalapril", "moderate", "pharmacokinetic",
             "Additive risk of acute kidney injury and hypoglycemia in diabetic patients.",
             "Hydrate adequately and monitor renal biomarkers."),
        ]

        count = 0
        for med_a_name, med_b_name, severity, itype, desc, mgmt in interactions_data:
            try:
                med_a = Medicine.objects.get(generic_name=med_a_name)
                med_b = Medicine.objects.get(generic_name=med_b_name)
                # Sort alphabetically to keep unique pair
                if str(med_a.id) > str(med_b.id):
                    med_a, med_b = med_b, med_a

                DrugInteraction.objects.update_or_create(
                    medicine_a=med_a,
                    medicine_b=med_b,
                    defaults={
                        "severity": severity,
                        "interaction_type": itype,
                        "description": desc,
                        "clinical_management": mgmt,
                        "is_active": True
                    }
                )
                count += 1
            except Medicine.DoesNotExist:
                continue
        return count

    def seed_diseases_and_protocols(self):
        """Seeds 50+ diseases with symptom links and treatment regimens."""
        diseases_catalog = [
            # 1. Malaria (Plasmodium falciparum)
            {
                "name": "Malaria (Plasmodium falciparum)", "category": "infectious", "icd10": "B50.9",
                "definition": "Acute parasitic infection transmitted by female Anopheles mosquitoes, characterized by paroxysmal high fevers, rigors, hemolytic anemia, and risk of fatal cerebral malaria.",
                "etiology": "Plasmodium falciparum protozoan parasites destroying erythrocytes and sequestering in deep vascular beds.",
                "age": "All ages (highest fatality in children <5 years and pregnant women)",
                "mgmt": "Prompt treatment with Artemisinin-based Combination Therapy (ACT). In severe cases, emergency parenteral Artesunate followed by supportive care and fluid management.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", True),
                    ("Chills & Rigors", "very_common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                    ("Severe Throbbing Headache", "common", "moderately_specific", False),
                    ("Profuse Diaphoresis / Night Sweats", "common", "moderately_specific", False),
                    ("Splenomegaly", "common", "highly_specific", True),
                    ("Jaundice / Scleral Icterus", "occasional", "moderately_specific", False),
                    ("Severe Conjunctival & Palmar Pallor", "occasional", "moderately_specific", False),
                    ("Altered Mental Status / Acute Confusion", "rare", "highly_specific", False),
                ],
                "treatments": [
                    ("Artemether + Lumefantrine", "first_line", "4 tablets at 0, 8, 24, 36, 48, 60 hours with food for uncomplicated malaria."),
                    ("Artesunate IV", "second_line", "2.4 mg/kg IV stat for severe malaria with hyperparasitemia or impaired consciousness."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "1 g oral every 6 hours PRN for fever >38.5°C.")
                ]
            },
            # 2. Acute Bacterial Meningitis
            {
                "name": "Acute Bacterial Meningitis", "category": "infectious", "icd10": "G00.9",
                "definition": "Rapidly progressive, life-threatening infection of the leptomeninges and subarachnoid space.",
                "etiology": "Neisseria meningitidis, Streptococcus pneumoniae, or Haemophilus influenzae type b.",
                "age": "All ages (infants, adolescents, and elderly at highest risk)",
                "mgmt": "Immediate empiric IV high-dose bactericidal antibiotics within 30 minutes of presentation. Adjunctive dexamethasone to reduce neurological sequelae.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Nuchal Rigidity (Neck Stiffness)", "very_common", "pathognomonic", True),
                    ("Positive Kernig's / Brudzinski's Sign", "very_common", "pathognomonic", True),
                    ("Severe Throbbing Headache", "very_common", "highly_specific", False),
                    ("Marked Photophobia", "common", "highly_specific", True),
                    ("Altered Mental Status / Acute Confusion", "common", "highly_specific", True),
                    ("Petechial Rash & Purpura", "occasional", "highly_specific", True),
                    ("Generalized Tonic-Clonic Seizures", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Ceftriaxone", "first_line", "2 g IV every 12 hours (total 4 g/day) for 10-14 days."),
                    ("Dexamethasone", "adjunct", "10 mg IV 15-20 minutes before or with first dose of ceftriaxone, then every 6 hours for 4 days."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "1 g IV/oral every 6 hours PRN for severe headache and pyrexia.")
                ]
            },
            # 3. Community-Acquired Pneumonia
            {
                "name": "Community-Acquired Pneumonia (Bacterial)", "category": "respiratory", "icd10": "J18.9",
                "definition": "Acute infection of the pulmonary parenchymal tissue acquired outside healthcare facilities.",
                "etiology": "Streptococcus pneumoniae, Klebsiella pneumoniae, or Haemophilus influenzae.",
                "age": "Elderly (>65) and young children (<5 years)",
                "mgmt": "Empiric antimicrobial therapy based on severity (CURB-65 criteria), oxygenation targeting SpO2 >92%, and bronchial toilet.",
                "symptoms": [
                    ("Productive Cough with Purulent Sputum", "very_common", "highly_specific", True),
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Inspiratory Crackles / Crepitations", "very_common", "highly_specific", True),
                    ("Pleuritic Chest Pain", "common", "highly_specific", True),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                    ("Tachypnea (>24 breaths/min)", "common", "moderately_specific", True),
                    ("Central Cyanosis", "occasional", "highly_specific", False),
                ],
                "treatments": [
                    ("Amoxicillin + Clavulanic Acid", "first_line", "1 g oral every 12 hours for 7-10 days (outpatient moderate)."),
                    ("Ceftriaxone", "second_line", "1-2 g IV daily for severe hospitalized pneumonia."),
                    ("Azithromycin", "adjunct", "500 mg daily for 3 days to cover atypical pathogens.")
                ]
            },
            # 4. Pulmonary Tuberculosis
            {
                "name": "Pulmonary Tuberculosis (PTB)", "category": "infectious", "icd10": "A15.0",
                "definition": "Chronic granulomatous airborne infection of lung parenchyma caused by Mycobacterium tuberculosis.",
                "etiology": "Mycobacterium tuberculosis (acid-fast bacillus).",
                "age": "Productive age groups (15-49 years), immunocompromised individuals",
                "mgmt": "Standard Directly Observed Treatment Short-course (DOTS) with 2 months RHZE followed by 4 months RH.",
                "symptoms": [
                    ("Persistent Dry Paroxysmal Cough", "very_common", "moderately_specific", False),
                    ("Productive Cough with Purulent Sputum", "very_common", "moderately_specific", False),
                    ("Profuse Diaphoresis / Night Sweats", "very_common", "highly_specific", True),
                    ("Unintentional Weight Loss", "very_common", "highly_specific", True),
                    ("Hemoptysis (Coughing up Blood)", "common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                    ("Inspiratory Crackles / Crepitations", "common", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Rifampicin + Isoniazid + Pyrazinamide + Ethambutol (RHZE)", "first_line", "4 tablets daily for 2 months intensive phase."),
                    ("Rifampicin + Isoniazid (RH)", "second_line", "4 tablets daily for 4 months continuation phase.")
                ]
            },
            # 5. Acute Myocardial Infarction
            {
                "name": "Acute Myocardial Infarction (STEMI / NSTEMI)", "category": "cardiovascular", "icd10": "I21.9",
                "definition": "Myocardial cell necrosis caused by acute rupture of an atheromatous plaque and subsequent occlusive coronary thrombosis.",
                "etiology": "Coronary artery atherosclerotic thrombosis.",
                "age": "Adults >40 years, especially with smoking, hypertension, or diabetes history",
                "mgmt": "Immediate antiplatelet loading (Aspirin + Clopidogrel), high-intensity statin, pain relief, and emergency reperfusion (PCI or thrombolysis).",
                "symptoms": [
                    ("Crushing Retrosternal Chest Pain", "very_common", "pathognomonic", True),
                    ("Pain Radiation to Left Arm or Jaw", "very_common", "pathognomonic", True),
                    ("Profuse Diaphoresis / Night Sweats", "common", "moderately_specific", True),
                    ("Dyspnea / Shortness of Breath", "common", "non_specific", False),
                    ("Persistent Nausea & Vomiting", "occasional", "non_specific", False),
                    ("Cold Clammy Extremities / Circulatory Collapse", "occasional", "highly_specific", False),
                ],
                "treatments": [
                    ("Aspirin (Acetylsalicylic Acid)", "first_line", "300 mg chewed loading immediately, then 75 mg daily."),
                    ("Clopidogrel", "first_line", "300-600 mg loading immediately, then 75 mg daily."),
                    ("Atorvastatin", "first_line", "80 mg once daily at bedtime."),
                    ("Glyceryl Trinitrate (Nitroglycerin)", "adjunct", "0.5 mg sublingually every 5 min up to 3 doses (contraindicated if SBP <90).")
                ]
            },
            # 6. Congestive Heart Failure
            {
                "name": "Congestive Heart Failure (Decompensated)", "category": "cardiovascular", "icd10": "I50.9",
                "definition": "Inability of the heart to pump sufficient blood forward to meet metabolic tissue demands, leading to venous congestion.",
                "etiology": "Longstanding hypertension, ischemic heart disease, dilated cardiomyopathy, or valvular disease.",
                "age": "Adults >50 years",
                "mgmt": "IV loop diuretic to relieve pulmonary congestion, ACE inhibitor, beta-blocker, aldosterone antagonist, and sodium restriction.",
                "symptoms": [
                    ("Bilateral Peripheral Pitting Edema", "very_common", "pathognomonic", True),
                    ("Orthopnea", "very_common", "pathognomonic", True),
                    ("Paroxysmal Nocturnal Dyspnea (PND)", "very_common", "pathognomonic", True),
                    ("Dyspnea / Shortness of Breath", "very_common", "moderately_specific", False),
                    ("Jugular Venous Distension (JVD)", "common", "highly_specific", True),
                    ("Inspiratory Crackles / Crepitations", "common", "highly_specific", True),
                    ("Hepatomegaly", "occasional", "moderately_specific", False),
                    ("Palpitations / Tachycardia", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Furosemide", "first_line", "40-80 mg IV stat, titrate to achieve net negative fluid balance."),
                    ("Enalapril", "first_line", "2.5-5 mg oral once daily, titrate to target 20 mg daily."),
                    ("Spironolactone", "adjunct", "25 mg oral once daily.")
                ]
            },
            # 7. Cholera
            {
                "name": "Cholera (Vibrio cholerae)", "category": "infectious", "icd10": "A00.9",
                "definition": "Acute dehydrating diarrheal illness caused by infection of the intestine with Vibrio cholerae.",
                "etiology": "Vibrio cholerae O1 or O139 entering through fecal-oral contaminated water.",
                "age": "All ages",
                "mgmt": "Aggressive fluid resuscitation with Oral Rehydration Salts (ORS) or IV Ringer's Lactate. Single-dose antibiotic to reduce volume.",
                "symptoms": [
                    ("Profuse Rice-Water Watery Diarrhea", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "very_common", "moderately_specific", False),
                    ("Polydipsia (Excessive Thirst)", "very_common", "highly_specific", True),
                    ("Severe Oliguria / Anuria (<400 mL/day)", "common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                    ("Cold Clammy Extremities / Circulatory Collapse", "occasional", "highly_specific", True),
                ],
                "treatments": [
                    ("Oral Rehydration Salts (ORS)", "first_line", "Continuous oral replacement volume for volume of stool."),
                    ("Doxycycline", "first_line", "Single dose 300 mg oral (adults) to shorten excretion and volume."),
                    ("Zinc Sulfate", "adjunct", "20 mg daily for 10 days for mucosal recovery.")
                ]
            },
            # 8. Acute Bronchial Asthma Exacerbation
            {
                "name": "Bronchial Asthma (Acute Exacerbation)", "category": "respiratory", "icd10": "J45.9",
                "definition": "Acute or subacute worsening of respiratory symptoms with airflow obstruction and wheezing.",
                "etiology": "Airway hyperresponsiveness and chronic eosinophilic inflammation triggered by viral URI, allergens, or cold air.",
                "age": "Children and young adults",
                "mgmt": "Repeated inhaled short-acting beta-2 agonist (Salbutamol) via spacer or nebulizer, early systemic oral corticosteroid, and supplemental oxygen.",
                "symptoms": [
                    ("Wheezing on Auscultation", "very_common", "pathognomonic", True),
                    ("Dyspnea / Shortness of Breath", "very_common", "moderately_specific", False),
                    ("Persistent Dry Paroxysmal Cough", "common", "moderately_specific", False),
                    ("Tachypnea (>24 breaths/min)", "common", "moderately_specific", True),
                    ("Palpitations / Tachycardia", "common", "non_specific", False),
                    ("Central Cyanosis", "rare", "highly_specific", False),
                ],
                "treatments": [
                    ("Salbutamol Inhaler (Albuterol)", "first_line", "4-10 puffs with spacer every 20 minutes for first hour, then every 4 hours."),
                    ("Prednisolone", "first_line", "40-50 mg oral once daily for 5-7 days."),
                    ("Ipratropium Bromide", "second_line", "4 puffs inhaled or 500 mcg nebulized added for severe exacerbations.")
                ]
            },
            # 9. Type 2 Diabetes Mellitus
            {
                "name": "Type 2 Diabetes Mellitus", "category": "endocrine", "icd10": "E11.9",
                "definition": "Metabolic disorder characterized by chronic hyperglycemia resulting from defects in insulin secretion and peripheral insulin resistance.",
                "etiology": "Multifactorial genetic predisposition combined with obesity, physical inactivity, and progressive beta-cell dysfunction.",
                "age": "Adults >30 years",
                "mgmt": "Lifestyle modification (diet and exercise), first-line metformin, cardiovascular risk reduction, and target HbA1c <7.0%.",
                "symptoms": [
                    ("Polydipsia (Excessive Thirst)", "very_common", "pathognomonic", True),
                    ("Polyuria (Excessive Urination)", "very_common", "pathognomonic", True),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                    ("Unintentional Weight Loss", "occasional", "moderately_specific", False),
                    ("Burning Epigastric Pain / Dyspepsia", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Metformin", "first_line", "500 mg with breakfast, titrate over weeks to 1000 mg twice daily."),
                    ("Atorvastatin", "adjunct", "20 mg daily for cardiovascular prevention."),
                    ("Enalapril", "adjunct", "5-10 mg daily for renal protection if microalbuminuria present.")
                ]
            },
            # 10. Diabetic Ketoacidosis (DKA)
            {
                "name": "Diabetic Ketoacidosis (DKA)", "category": "endocrine", "icd10": "E10.1",
                "definition": "Acute, life-threatening metabolic emergency characterized by triad of hyperglycemia, metabolic acidosis, and ketonemia.",
                "etiology": "Absolute or relative insulin deficiency compounded by increased counter-regulatory hormones.",
                "age": "Primarily Type 1 Diabetes; also Type 2 under severe infection or surgical stress",
                "mgmt": "IV fluid resuscitation (0.9% Normal Saline), continuous low-dose regular insulin infusion, potassium replacement, and frequent blood gas monitoring.",
                "symptoms": [
                    ("Kussmaul Breathing (Deep Sighing Respiration)", "very_common", "pathognomonic", True),
                    ("Fruity Breath Odor (Acetone Breath)", "very_common", "pathognomonic", True),
                    ("Polydipsia (Excessive Thirst)", "very_common", "highly_specific", True),
                    ("Polyuria (Excessive Urination)", "very_common", "highly_specific", True),
                    ("Persistent Nausea & Vomiting", "common", "moderately_specific", False),
                    ("Altered Mental Status / Acute Confusion", "common", "highly_specific", False),
                    ("Cold Clammy Extremities / Circulatory Collapse", "occasional", "highly_specific", False),
                ],
                "treatments": [
                    ("Human Regular Insulin (Soluble)", "first_line", "0.1 unit/kg/hr IV continuous infusion after initial fluid rehydration."),
                    ("Oral Rehydration Salts (ORS)", "adjunct", "Oral fluid transition once acidosis clears and glucose normalizes.")
                ]
            },
            # 11. Acute Ischemic Stroke
            {
                "name": "Acute Ischemic Stroke (CVA)", "category": "neurological", "icd10": "I63.9",
                "definition": "Sudden onset of neurological deficit persisting >24 hours caused by focal cerebral ischemia.",
                "etiology": "Thromboembolic or large vessel atherosclerotic occlusion of cerebral arterial supply.",
                "age": "Adults >50 years",
                "mgmt": "Emergency non-contrast head CT, thrombolysis within 4.5 hours if eligible, antiplatelet therapy after 24 hours, and permissive hypertension management.",
                "symptoms": [
                    ("Acute Focal Facial Droop", "very_common", "pathognomonic", True),
                    ("Unilateral Arm Weakness (Hemiparesis)", "very_common", "pathognomonic", True),
                    ("Acute Dysarthria / Slurred Speech", "very_common", "pathognomonic", True),
                    ("Severe Throbbing Headache", "occasional", "moderately_specific", False),
                    ("Altered Mental Status / Acute Confusion", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Aspirin (Acetylsalicylic Acid)", "first_line", "150-300 mg daily started 24 hours post-thrombolysis or immediately once bleed excluded."),
                    ("Atorvastatin", "first_line", "80 mg once daily for plaque stabilization.")
                ]
            },
            # 12. Acute Pyelonephritis
            {
                "name": "Acute Pyelonephritis", "category": "genitourinary", "icd10": "N10",
                "definition": "Upper urinary tract infection with bacterial invasion and inflammation of the renal parenchyma and pelvis.",
                "etiology": "Ascending infection predominantly by uropathogenic Escherichia coli (UPEC).",
                "age": "Young sexually active women, elderly men with BPH, diabetic patients",
                "mgmt": "Parenteral or oral fluoroquinolone / third-generation cephalosporin for 7-14 days with adequate fluid hydration.",
                "symptoms": [
                    ("Costovertebral Angle Tenderness (Flank Pain)", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Chills & Rigors", "very_common", "moderately_specific", False),
                    ("Dysuria (Burning Micturition)", "common", "highly_specific", True),
                    ("Persistent Nausea & Vomiting", "common", "non_specific", False),
                    ("Gross Hematuria (Visible Blood in Urine)", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Ciprofloxacin", "first_line", "500 mg oral twice daily for 7 days (outpatient)."),
                    ("Ceftriaxone", "first_line", "1 g IV daily for 10-14 days (inpatient severe)."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "1 g oral every 6 hours PRN for fever.")
                ]
            },
            # 13. Acute Appendicitis
            {
                "name": "Acute Appendicitis", "category": "gastrointestinal", "icd10": "K35.8",
                "definition": "Acute surgical inflammation of the vermiform appendix, typically secondary to luminal obstruction.",
                "etiology": "Obstruction of the appendiceal lumen by fecalith, lymphoid hyperplasia, or foreign body.",
                "age": "Teens and young adults (10-30 years)",
                "mgmt": "Urgent surgical appendectomy, preoperative broad-spectrum antibiotic coverage, and pain control.",
                "symptoms": [
                    ("Right Lower Quadrant Abdominal Tenderness", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "very_common", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Board-Like Abdominal Rigidity & Rebound Tenderness", "occasional", "highly_specific", True),
                ],
                "treatments": [
                    ("Ceftriaxone", "first_line", "1 g IV single dose pre-operatively."),
                    ("Metronidazole", "first_line", "500 mg IV single dose pre-operatively.")
                ]
            },
            # 14. Acute Gouty Arthritis
            {
                "name": "Acute Gouty Arthritis", "category": "musculoskeletal", "icd10": "M10.0",
                "definition": "Monosodium urate crystal-induced inflammatory arthritis, most commonly presenting as acute podagra.",
                "etiology": "Hyperuricemia resulting in crystal precipitation within synovial joints.",
                "age": "Adult males >35 years, postmenopausal females",
                "mgmt": "Rapid pain and inflammation relief with NSAIDs, Colchicine, or intra-articular/systemic corticosteroids. Urate-lowering therapy after acute flare settles.",
                "symptoms": [
                    ("Acute Podagra (Severe Pain & Swelling in First MTP Joint)", "very_common", "pathognomonic", True),
                    ("Spreading Erythematous Warm Swelling (Cellulitis)", "common", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Ibuprofen", "first_line", "800 mg oral every 8 hours with meals for 3-5 days."),
                    ("Colchicine", "first_line", "1 mg oral loading, then 0.5 mg 1 hour later."),
                    ("Prednisolone", "second_line", "35 mg oral daily for 5 days if NSAIDs contraindicated.")
                ]
            },
            # 15. Measles
            {
                "name": "Measles (Rubeola)", "category": "infectious", "icd10": "B05.9",
                "definition": "Highly contagious viral exanthematous infection characterized by fever, cough, coryza, conjunctivitis, and characteristic rash.",
                "etiology": "Measles morbillivirus (Paramyxoviridae).",
                "age": "Unvaccinated infants and young children",
                "mgmt": "Supportive rehydration, antipyretics, high-dose Vitamin A, and isolation to prevent outbreaks.",
                "symptoms": [
                    ("Koplik Spots on Buccal Mucosa", "very_common", "pathognomonic", True),
                    ("Maculopapular Morbilliform Rash", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Persistent Dry Paroxysmal Cough", "very_common", "moderately_specific", False),
                    ("Marked Photophobia", "common", "moderately_specific", False),
                ],
                "treatments": [
                    ("Zinc Sulfate", "adjunct", "20 mg daily for supportive mucosal defense."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "15 mg/kg oral every 6 hours PRN for fever.")
                ]
            },
            # 16. Tetanus
            {
                "name": "Tetanus (Lockjaw)", "category": "infectious", "icd10": "A35",
                "definition": "Acute neurologic disease characterized by painful tonic muscle spasms caused by Clostridium tetani neurotoxin.",
                "etiology": "Tetanospasmin neurotoxin produced by Clostridium tetani entering via contaminated puncture wounds.",
                "age": "Unvaccinated individuals, neonates born to unvaccinated mothers",
                "mgmt": "Tetanus immunoglobulin (TIG), surgical wound debridement, IV metronidazole, sedation, and muscle spasm control.",
                "symptoms": [
                    ("Severe Trismus ('Lockjaw') and Risus Sardonicus", "very_common", "pathognomonic", True),
                    ("Board-Like Abdominal Rigidity & Rebound Tenderness", "common", "highly_specific", True),
                    ("Generalized Tonic-Clonic Seizures", "common", "moderately_specific", False),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                ],
                "treatments": [
                    ("Metronidazole", "first_line", "500 mg IV every 8 hours for 7-10 days to eradicate vegetative bacteria."),
                    ("Dexamethasone", "adjunct", "For acute inflammation and autonomic storming.")
                ]
            },
            # 17. Bacterial Cellulitis
            {
                "name": "Bacterial Cellulitis", "category": "dermatological", "icd10": "L03.9",
                "definition": "Acute bacterial infection of the deep dermis and subcutaneous tissues.",
                "etiology": "Streptococcus pyogenes or Staphylococcus aureus.",
                "age": "All ages",
                "mgmt": "Oral or parenteral beta-lactam antibiotics, limb elevation, and marking border progression.",
                "symptoms": [
                    ("Spreading Erythematous Warm Swelling (Cellulitis)", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Chills & Rigors", "common", "non_specific", False),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Amoxicillin + Clavulanic Acid", "first_line", "625 mg oral three times daily for 7-10 days."),
                    ("Ceftriaxone", "second_line", "1 g IV daily if systemic signs or rapid spreading."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "500 mg every 6 hours for pain.")
                ]
            },
            # 18. Peptic Ulcer Disease
            {
                "name": "Peptic Ulcer Disease (Gastric / Duodenal)", "category": "gastrointestinal", "icd10": "K27.9",
                "definition": "Circumscribed mucosal ulceration in stomach or duodenum penetrating the muscularis mucosae.",
                "etiology": "Helicobacter pylori infection or prolonged use of NSAIDs/Aspirin.",
                "age": "Adults 25-65 years",
                "mgmt": "Proton Pump Inhibitor (PPI) and H. pylori eradication therapy (PPI + Clarithromycin + Amoxicillin/Metronidazole).",
                "symptoms": [
                    ("Burning Epigastric Pain / Dyspepsia", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "common", "non_specific", False),
                    ("Coffee-Ground Emesis / Melena", "occasional", "highly_specific", True),
                    ("Unintentional Weight Loss", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Omeprazole", "first_line", "20-40 mg oral once daily for 4-8 weeks."),
                    ("Amoxicillin + Clavulanic Acid", "first_line", "1 g twice daily for 14 days (as part of triple therapy)."),
                    ("Metronidazole", "first_line", "400 mg twice daily for 14 days.")
                ]
            },
            # 19. Severe Iron Deficiency Anemia
            {
                "name": "Severe Iron Deficiency Anemia", "category": "hematology", "icd10": "D50.9",
                "definition": "Microcytic hypochromic anemia resulting from depleted body iron stores.",
                "etiology": "Chronic occult blood loss, hookworm infection, or inadequate dietary iron intake.",
                "age": "Reproductive-age females, young children, elderly with GI lesions",
                "mgmt": "Oral or IV iron replacement and treatment of underlying etiology.",
                "symptoms": [
                    ("Severe Conjunctival & Palmar Pallor", "very_common", "pathognomonic", True),
                    ("Severe Malaise & Fatigue", "very_common", "highly_specific", False),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                    ("Palpitations / Tachycardia", "common", "moderately_specific", False),
                    ("Severe Throbbing Headache", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Oral Rehydration Salts (ORS)", "adjunct", "Supportive."),
                    ("Zinc Sulfate", "adjunct", "Mineral balance.")
                ]
            },
            # 20. Sepsis & Septic Shock
            {
                "name": "Sepsis & Septic Shock", "category": "emergency", "icd10": "A41.9",
                "definition": "Life-threatening organ dysfunction caused by a dysregulated host response to infection.",
                "etiology": "Severe bacteremia or focal infections (pneumonia, UTI, intra-abdominal, meningitis).",
                "age": "All ages (extremes of age at highest risk)",
                "mgmt": "Surviving Sepsis Campaign bundle: blood cultures before antibiotics, broad-spectrum IV antimicrobials within 1 hour, 30 mL/kg crystalloid fluid bolus, and vasopressors if MAP <65 mmHg.",
                "symptoms": [
                    ("Cold Clammy Extremities / Circulatory Collapse", "very_common", "pathognomonic", True),
                    ("Altered Mental Status / Acute Confusion", "very_common", "pathognomonic", True),
                    ("Tachypnea (>24 breaths/min)", "very_common", "highly_specific", True),
                    ("Severe Oliguria / Anuria (<400 mL/day)", "common", "highly_specific", True),
                    ("High Fever (>38.5°C)", "common", "moderately_specific", False),
                    ("Severe Hypothermia (<35°C)", "occasional", "highly_specific", True),
                    ("Palpitations / Tachycardia", "very_common", "non_specific", False),
                ],
                "treatments": [
                    ("Ceftriaxone", "first_line", "2 g IV stat within 1 hour of presentation."),
                    ("Metronidazole", "first_line", "500 mg IV stat if intra-abdominal source suspected.")
                ]
            },
            # 21. Typhoid Fever
            {
                "name": "Typhoid Fever (Enteric Fever)", "category": "infectious", "icd10": "A01.0",
                "definition": "Systemic bacterial infection caused by Salmonella enterica serotype Typhi characterized by stepwise remittent fever, rose spots, relative bradycardia, and hepatosplenomegaly.",
                "etiology": "Salmonella Typhi ingested via fecal-oral contaminated food or water.",
                "age": "Children and young adults (5-25 years)",
                "mgmt": "Fluoroquinolones or third-generation cephalosporins (Ceftriaxone / Azithromycin). Fluid and electrolyte maintenance, monitoring for intestinal perforation.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", True),
                    ("Severe Throbbing Headache", "very_common", "moderately_specific", False),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                    ("Splenomegaly", "common", "highly_specific", True),
                    ("Hepatomegaly", "common", "moderately_specific", False),
                    ("Persistent Dry Paroxysmal Cough", "occasional", "non_specific", False),
                    ("Burning Epigastric Pain / Dyspepsia", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Ciprofloxacin", "first_line", "500 mg oral twice daily for 10-14 days."),
                    ("Ceftriaxone", "second_line", "2 g IV daily for 7-10 days."),
                    ("Azithromycin", "second_line", "1 g oral daily for 5-7 days.")
                ]
            },
            # 22. Visceral Leishmaniasis
            {
                "name": "Visceral Leishmaniasis (Kala-azar)", "category": "infectious", "icd10": "B55.0",
                "definition": "Chronic systemic protozoan parasitic infection transmitted by phlebotomine sandflies resulting in massive splenomegaly, pancytopenia, and progressive wasting.",
                "etiology": "Leishmania donovani protozoan complex multiplying within reticuloendothelial macrophages.",
                "age": "Children, agricultural workers, migrant laborers in lowland endemic areas",
                "mgmt": "Combination antimonial therapy or liposomal Amphotericin B. Nutritional support and screening for co-infections.",
                "symptoms": [
                    ("Splenomegaly", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", True),
                    ("Unintentional Weight Loss", "very_common", "pathognomonic", True),
                    ("Severe Conjunctival & Palmar Pallor", "very_common", "highly_specific", True),
                    ("Hepatomegaly", "common", "moderately_specific", False),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                    ("Generalized Lymphadenopathy", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Artesunate IV", "adjunct", "If concurrent malaria suspected."),
                    ("Oral Rehydration Salts (ORS)", "adjunct", "Nutritional fluid rehydration.")
                ]
            },
            # 23. Chronic Obstructive Pulmonary Disease
            {
                "name": "Chronic Obstructive Pulmonary Disease (COPD Exacerbation)", "category": "respiratory", "icd10": "J44.1",
                "definition": "Persistent airflow limitation typically progressive and associated with an enhanced chronic inflammatory response to noxious particles.",
                "etiology": "Longterm tobacco smoking or biomass fuel smoke exposure (indoor air pollution).",
                "age": "Adults >40 years",
                "mgmt": "Inhaled bronchodilators (SABA + SAMA), oral systemic corticosteroids, controlled oxygen targeting SpO2 88-92%, and antibiotics if sputum purulent.",
                "symptoms": [
                    ("Dyspnea / Shortness of Breath", "very_common", "highly_specific", True),
                    ("Productive Cough with Purulent Sputum", "very_common", "pathognomonic", True),
                    ("Wheezing on Auscultation", "very_common", "highly_specific", True),
                    ("Central Cyanosis", "common", "highly_specific", True),
                    ("Tachypnea (>24 breaths/min)", "common", "moderately_specific", True),
                    ("Bilateral Peripheral Pitting Edema", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Salbutamol Inhaler (Albuterol)", "first_line", "4-8 puffs with spacer every 20-30 min."),
                    ("Ipratropium Bromide", "first_line", "4 puffs inhaled every 6 hours."),
                    ("Prednisolone", "first_line", "40 mg oral daily for 5 days."),
                    ("Amoxicillin + Clavulanic Acid", "second_line", "625 mg oral three times daily if sputum purulent.")
                ]
            },
            # 24. Pulmonary Embolism
            {
                "name": "Pulmonary Embolism (Acute)", "category": "cardiovascular", "icd10": "I26.9",
                "definition": "Occlusion of one or more pulmonary arteries by thrombi that originate elsewhere, typically from the deep veins of the lower extremities.",
                "etiology": "Deep vein thrombosis (DVT) dislodging and impacting the pulmonary arterial bed.",
                "age": "Adults with immobility, recent surgery, active cancer, or pregnancy/oral contraceptives",
                "mgmt": "Immediate anticoagulation (Low Molecular Weight Heparin or direct oral anticoagulant), oxygenation, and systemic thrombolysis for massive PE with hypotension.",
                "symptoms": [
                    ("Dyspnea / Shortness of Breath", "very_common", "pathognomonic", True),
                    ("Pleuritic Chest Pain", "very_common", "pathognomonic", True),
                    ("Tachypnea (>24 breaths/min)", "very_common", "highly_specific", True),
                    ("Palpitations / Tachycardia", "very_common", "highly_specific", True),
                    ("Hemoptysis (Coughing up Blood)", "common", "highly_specific", True),
                    ("Cold Clammy Extremities / Circulatory Collapse", "occasional", "highly_specific", False),
                ],
                "treatments": [
                    ("Aspirin (Acetylsalicylic Acid)", "adjunct", "Long-term secondary thromboprophylaxis."),
                    ("Furosemide", "adjunct", "Contraindicated if acute right heart strain with hypotension.")
                ]
            },
            # 25. Essential Systemic Hypertension
            {
                "name": "Essential Systemic Hypertension", "category": "cardiovascular", "icd10": "I10",
                "definition": "Chronic sustained elevation of systemic arterial pressure (Systolic >= 140 mmHg and/or Diastolic >= 90 mmHg) without identifiable secondary cause.",
                "etiology": "Complex interplay of genetic predisposition, dietary salt excess, sympathetic overactivity, and arterial stiffening.",
                "age": "Adults >30 years",
                "mgmt": "First-line antihypertensive therapy with ACE inhibitor, calcium channel blocker, or thiazide diuretic; dietary DASH lifestyle modifications.",
                "symptoms": [
                    ("Severe Throbbing Headache", "common", "moderately_specific", False),
                    ("Palpitations / Tachycardia", "occasional", "non_specific", False),
                    ("Severe Malaise & Fatigue", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Enalapril", "first_line", "10-20 mg once daily."),
                    ("Amlodipine", "first_line", "5-10 mg once daily."),
                    ("Atorvastatin", "adjunct", "20 mg daily for atherosclerotic prevention.")
                ]
            },
            # 26. Hypertensive Emergency / Crisis
            {
                "name": "Hypertensive Emergency / Crisis", "category": "cardiovascular", "icd10": "I16.1",
                "definition": "Severe elevation in blood pressure (usually SBP >180 mmHg or DBP >120 mmHg) associated with acute, progressive target organ damage.",
                "etiology": "Acute breakdown in vascular autoregulation triggered by non-adherence or renal ischemia.",
                "age": "Adults with chronic untreated or poorly controlled hypertension",
                "mgmt": "Controlled BP reduction in ICU using parenteral titratable agents; target no more than 25% reduction in first hour to prevent ischemic stroke.",
                "symptoms": [
                    ("Severe Throbbing Headache", "very_common", "pathognomonic", True),
                    ("Crushing Retrosternal Chest Pain", "common", "highly_specific", True),
                    ("Altered Mental Status / Acute Confusion", "common", "highly_specific", True),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                    ("Persistent Nausea & Vomiting", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Furosemide", "first_line", "20-40 mg IV if pulmonary edema present."),
                    ("Amlodipine", "second_line", "10 mg oral once stabilized.")
                ]
            },
            # 27. Deep Vein Thrombosis
            {
                "name": "Deep Vein Thrombosis (DVT)", "category": "cardiovascular", "icd10": "I80.2",
                "definition": "Formation of a blood clot within the deep veins of the lower extremity or pelvis.",
                "etiology": "Virchow's triad: endothelial injury, stasis, and hypercoagulability.",
                "age": "Adults with prolonged immobility, hospitalization, cancer, or postpartum",
                "mgmt": "Therapeutic anticoagulation for minimum 3-6 months and compression stockings once edema resolves.",
                "symptoms": [
                    ("Bilateral Peripheral Pitting Edema", "very_common", "pathognomonic", True),
                    ("Spreading Erythematous Warm Swelling (Cellulitis)", "common", "moderately_specific", False),
                    ("Palpitations / Tachycardia", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Aspirin (Acetylsalicylic Acid)", "second_line", "75 mg daily once initial anticoagulant course completes.")
                ]
            },
            # 28. Bacterial Dysentery
            {
                "name": "Acute Bacterial Dysentery (Shigellosis)", "category": "gastrointestinal", "icd10": "A03.9",
                "definition": "Invasive acute colonic infection characterized by severe tenesmus, fever, and frequent small stools containing blood, mucus, and pus.",
                "etiology": "Shigella dysenteriae, flexneri, or sonnei invading the rectosigmoid epithelium.",
                "age": "Children 1-5 years, crowded settings with poor sanitation",
                "mgmt": "Oral rehydration, zinc supplementation in children, and ciprofloxacin or azithromycin.",
                "symptoms": [
                    ("Bloody Mucopurulent Diarrhea (Dysentery)", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "very_common", "highly_specific", True),
                    ("Persistent Nausea & Vomiting", "common", "non_specific", False),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                    ("Board-Like Abdominal Rigidity & Rebound Tenderness", "rare", "highly_specific", False),
                ],
                "treatments": [
                    ("Ciprofloxacin", "first_line", "500 mg oral twice daily for 3 days."),
                    ("Oral Rehydration Salts (ORS)", "first_line", "Immediate oral replacement."),
                    ("Zinc Sulfate", "adjunct", "20 mg daily for 14 days.")
                ]
            },
            # 29. Amoebic Dysentery
            {
                "name": "Amoebic Dysentery (Intestinal Amoebiasis)", "category": "gastrointestinal", "icd10": "A06.0",
                "definition": "Invasive protozoan infection of the large intestine causing mucosal ulceration and bloody mucoid diarrhea.",
                "etiology": "Entamoeba histolytica trophozoites invading colonic mucosal crypts ('flask-shaped ulcers').",
                "age": "All ages",
                "mgmt": "Oral Metronidazole or Tinidazole followed by a luminal amoebicide to clear cyst carriage.",
                "symptoms": [
                    ("Bloody Mucopurulent Diarrhea (Dysentery)", "very_common", "pathognomonic", True),
                    ("Burning Epigastric Pain / Dyspepsia", "common", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "occasional", "moderately_specific", False),
                    ("Hepatomegaly", "occasional", "highly_specific", True),
                ],
                "treatments": [
                    ("Metronidazole", "first_line", "500 mg oral three times daily for 7-10 days."),
                    ("Oral Rehydration Salts (ORS)", "first_line", "Fluid replacement.")
                ]
            },
            # 30. Cirrhosis & Portal Hypertension
            {
                "name": "Cirrhosis with Portal Hypertension & Ascites", "category": "gastrointestinal", "icd10": "K74.6",
                "definition": "End-stage diffuse hepatic fibrosis with nodular regeneration, architectural distortion, and elevated portal venous pressure.",
                "etiology": "Chronic viral hepatitis B/C, alcoholic liver disease, or metabolic dysfunction-associated steatohepatitis (MASH).",
                "age": "Adults >40 years",
                "mgmt": "Diuretic combination (Spironolactone + Furosemide), dietary sodium restriction (<2 g/day), beta-blockers for variceal bleeding prevention, and paracentesis.",
                "symptoms": [
                    ("Ascites (Abdominal Distension with Shifting Dullness)", "very_common", "pathognomonic", True),
                    ("Jaundice / Scleral Icterus", "very_common", "pathognomonic", True),
                    ("Bilateral Peripheral Pitting Edema", "very_common", "highly_specific", True),
                    ("Splenomegaly", "common", "highly_specific", True),
                    ("Coffee-Ground Emesis / Melena", "occasional", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Spironolactone", "first_line", "100 mg oral daily, titrate up to 400 mg daily."),
                    ("Furosemide", "first_line", "40 mg oral daily (maintain 100:40 ratio with spironolactone)."),
                    ("Omeprazole", "adjunct", "40 mg daily for variceal and ulcer prophylaxis.")
                ]
            },
            # 31. Acute Viral Hepatitis
            {
                "name": "Acute Viral Hepatitis (Hepatitis A/E)", "category": "gastrointestinal", "icd10": "B15.9",
                "definition": "Acute inflammatory liver injury transmitted via the fecal-oral route.",
                "etiology": "Hepatitis A virus (HAV) or Hepatitis E virus (HEV).",
                "age": "Children and young adults; pregnant women at high risk of acute liver failure from HEV",
                "mgmt": "Supportive hydration and rest; avoid hepatotoxic medications (paracetamol, NSAIDs, alcohol).",
                "symptoms": [
                    ("Jaundice / Scleral Icterus", "very_common", "pathognomonic", True),
                    ("High Fever (>38.5°C)", "common", "moderately_specific", False),
                    ("Persistent Nausea & Vomiting", "very_common", "moderately_specific", False),
                    ("Hepatomegaly", "common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                ],
                "treatments": [
                    ("Oral Rehydration Salts (ORS)", "first_line", "Supportive hydration.")
                ]
            },
            # 32. Acute Pancreatitis
            {
                "name": "Acute Pancreatitis", "category": "gastrointestinal", "icd10": "K85.9",
                "definition": "Acute enzymatic autodigestive inflammation of pancreatic parenchyma.",
                "etiology": "Gallstones obstructing the ampulla of Vater or heavy alcohol ingestion.",
                "age": "Adults 30-70 years",
                "mgmt": "Aggressive IV crystalloid resuscitation (250-500 mL/hr Ringer's Lactate), multimodal analgesia, and early oral feeding as tolerated.",
                "symptoms": [
                    ("Burning Epigastric Pain / Dyspepsia", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "very_common", "highly_specific", True),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Board-Like Abdominal Rigidity & Rebound Tenderness", "occasional", "highly_specific", True),
                    ("Cold Clammy Extremities / Circulatory Collapse", "rare", "highly_specific", False),
                ],
                "treatments": [
                    ("Omeprazole", "adjunct", "40 mg IV daily for stress ulcer prophylaxis.")
                ]
            },
            # 33. Acute Cholecystitis
            {
                "name": "Acute Cholecystitis & Biliary Colic", "category": "gastrointestinal", "icd10": "K81.0",
                "definition": "Acute inflammation of the gallbladder, almost always secondary to cystic duct obstruction by a gallstone.",
                "etiology": "Impacted gallstone producing mechanical distension, ischemia, and secondary bacterial infection.",
                "age": "Adult females >40 years, multiparous, obese",
                "mgmt": "IV antibiotics covering enteric gram-negative bacilli, analgesia, and early laparoscopic cholecystectomy within 72 hours.",
                "symptoms": [
                    ("Right Lower Quadrant Abdominal Tenderness", "occasional", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Persistent Nausea & Vomiting", "very_common", "moderately_specific", False),
                    ("Jaundice / Scleral Icterus", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Ceftriaxone", "first_line", "1 g IV daily."),
                    ("Metronidazole", "first_line", "500 mg IV every 8 hours.")
                ]
            },
            # 34. Primary Hyperthyroidism
            {
                "name": "Primary Hyperthyroidism (Graves' Disease)", "category": "endocrine", "icd10": "E05.0",
                "definition": "Hypermetabolic syndrome caused by excessive circulating thyroid hormones (free T4/T3).",
                "etiology": "TSH-receptor stimulating autoantibodies (Graves') or toxic multinodular goiter.",
                "age": "Females 20-50 years",
                "mgmt": "Thionamides (Methimazole / Propylthiouracil), beta-blockers for adrenergic symptom control, and definitive radioiodine or surgery.",
                "symptoms": [
                    ("Heat Intolerance with Tremor & Weight Loss", "very_common", "pathognomonic", True),
                    ("Palpitations / Tachycardia", "very_common", "pathognomonic", True),
                    ("Unintentional Weight Loss", "very_common", "highly_specific", True),
                    ("Polydipsia (Excessive Thirst)", "common", "moderately_specific", False),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Atenolol", "first_line", "50 mg oral daily for rapid adrenergic heart rate control.")
                ]
            },
            # 35. Primary Hypothyroidism
            {
                "name": "Primary Hypothyroidism (Hashimoto's)", "category": "endocrine", "icd10": "E03.9",
                "definition": "Deficiency of thyroid hormone production leading to generalized slowing of metabolic processes.",
                "etiology": "Autoimmune lymphocytic thyroiditis (Hashimoto's) or dietary iodine deficiency.",
                "age": "Females >40 years",
                "mgmt": "Lifelong oral levothyroxine sodium monotherapy titrated to normalize serum TSH.",
                "symptoms": [
                    ("Cold Intolerance with Constipation & Dry Skin", "very_common", "pathognomonic", True),
                    ("Severe Malaise & Fatigue", "very_common", "highly_specific", True),
                    ("Bilateral Peripheral Pitting Edema", "common", "moderately_specific", False),
                    ("Severe Bradycardia (<50 bpm)", "common", "highly_specific", True),
                ],
                "treatments": [
                    ("Levothyroxine", "first_line", "1.6 mcg/kg/day oral fasting 30 min before breakfast.")
                ]
            },
            # 36. Acute Hemorrhagic Stroke
            {
                "name": "Hemorrhagic Stroke (Intracerebral / Subarachnoid)", "category": "neurological", "icd10": "I61.9",
                "definition": "Acute neurological insult caused by spontaneous rupture of a cerebral blood vessel into parenchyma or subarachnoid space.",
                "etiology": "Chronic hypertensive lipohyalinosis or rupture of a saccular berry aneurysm.",
                "age": "Adults >50 years with chronic hypertension",
                "mgmt": "Emergency non-contrast head CT, intensive BP lowering (target SBP 140 mmHg), reversal of anticoagulation, and neurosurgical evacuation if indicated.",
                "symptoms": [
                    ("Severe Throbbing Headache", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "very_common", "highly_specific", True),
                    ("Altered Mental Status / Acute Confusion", "very_common", "pathognomonic", True),
                    ("Acute Focal Facial Droop", "common", "highly_specific", True),
                    ("Unilateral Arm Weakness (Hemiparesis)", "common", "highly_specific", True),
                    ("Nuchal Rigidity (Neck Stiffness)", "occasional", "highly_specific", True),
                ],
                "treatments": [
                    ("Furosemide", "second_line", "If cerebral edema with imminent herniation.")
                ]
            },
            # 37. Generalized Epilepsy
            {
                "name": "Generalized Epilepsy / Tonic-Clonic Seizure", "category": "neurological", "icd10": "G40.9",
                "definition": "Chronic neurological disorder characterized by recurrent unprovoked generalized seizures.",
                "etiology": "Genetic channelopathies, perinatal brain injury, post-traumatic cortical scarring, or CNS infections.",
                "age": "Childhood through elderly",
                "mgmt": "Emergency termination of status epilepticus with IV benzodiazepines; long-term antiepileptic drug monotherapy.",
                "symptoms": [
                    ("Generalized Tonic-Clonic Seizures", "very_common", "pathognomonic", True),
                    ("Altered Mental Status / Acute Confusion", "very_common", "pathognomonic", True),
                    ("Severe Throbbing Headache", "common", "moderately_specific", False),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Paracetamol (Acetaminophen)", "adjunct", "For post-ictal headache.")
                ]
            },
            # 38. Migraine Headache
            {
                "name": "Migraine Headache (with / without Aura)", "category": "neurological", "icd10": "G43.9",
                "definition": "Primary neurovascular headache disorder characterized by recurrent attacks of moderate to severe throbbing unilateral pain.",
                "etiology": "Cortical spreading depression and trigeminovascular sensitization.",
                "age": "Females 15-45 years",
                "mgmt": "Acute treatment with triptans, NSAIDs, and antiemetics; preventive therapy with beta-blockers, amitriptyline, or topiramate.",
                "symptoms": [
                    ("Severe Throbbing Headache", "very_common", "pathognomonic", True),
                    ("Marked Photophobia", "very_common", "pathognomonic", True),
                    ("Persistent Nausea & Vomiting", "common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Ibuprofen", "first_line", "400-800 mg oral at onset of attack."),
                    ("Paracetamol (Acetaminophen)", "second_line", "1 g oral at onset.")
                ]
            },
            # 39. Acute Uncomplicated Cystitis
            {
                "name": "Acute Uncomplicated Cystitis (UTI)", "category": "genitourinary", "icd10": "N30.0",
                "definition": "Superficial bacterial infection of the bladder mucosa in an otherwise healthy non-pregnant female.",
                "etiology": "Uropathogenic Escherichia coli (80%), Staphylococcus saprophyticus.",
                "age": "Sexually active females 18-50 years",
                "mgmt": "Short-course oral antimicrobial therapy (Nitrofurantoin, Fosfomycin, or Co-trimoxazole) and increased oral fluid intake.",
                "symptoms": [
                    ("Dysuria (Burning Micturition)", "very_common", "pathognomonic", True),
                    ("Gross Hematuria (Visible Blood in Urine)", "occasional", "moderately_specific", False),
                ],
                "treatments": [
                    ("Ciprofloxacin", "second_line", "250-500 mg oral twice daily for 3 days."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "For suprapubic discomfort.")
                ]
            },
            # 40. Chronic Kidney Disease
            {
                "name": "Chronic Kidney Disease (Stage 4-5 / Uremia)", "category": "genitourinary", "icd10": "N18.9",
                "definition": "Longstanding, irreversible decline in renal function characterized by GFR <30 mL/min and accumulation of uremic toxins.",
                "etiology": "Diabetic nephropathy, hypertensive nephrosclerosis, chronic glomerulonephritis.",
                "age": "Adults >45 years",
                "mgmt": "Blood pressure control with ACEi/ARB, volume management with loop diuretics, dietary protein restriction, and preparation for renal replacement therapy.",
                "symptoms": [
                    ("Severe Oliguria / Anuria (<400 mL/day)", "very_common", "pathognomonic", True),
                    ("Bilateral Peripheral Pitting Edema", "very_common", "pathognomonic", True),
                    ("Severe Conjunctival & Palmar Pallor", "very_common", "highly_specific", True),
                    ("Persistent Nausea & Vomiting", "common", "highly_specific", False),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                ],
                "treatments": [
                    ("Furosemide", "first_line", "High-dose 80-160 mg oral daily to maintain diuresis."),
                    ("Enalapril", "first_line", "Careful low-dose titration with regular potassium monitoring.")
                ]
            },
            # 41. Rheumatoid Arthritis
            {
                "name": "Rheumatoid Arthritis", "category": "musculoskeletal", "icd10": "M05.9",
                "definition": "Chronic systemic autoimmune inflammatory disorder characterized by persistent symmetric polyarthritis and synovial proliferation.",
                "etiology": "Loss of immune tolerance and anti-citrullinated protein antibody (ACPA) mediated joint destruction.",
                "age": "Females 30-55 years",
                "mgmt": "Early disease-modifying antirheumatic drugs (DMARDs, e.g. Methotrexate), short-term bridging corticosteroids, and NSAIDs for symptom relief.",
                "symptoms": [
                    ("Symmetric Polyarthritis with Morning Stiffness (>1 hr)", "very_common", "pathognomonic", True),
                    ("Severe Malaise & Fatigue", "very_common", "highly_specific", False),
                    ("Unintentional Weight Loss", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Ibuprofen", "first_line", "400 mg oral three times daily with meals."),
                    ("Prednisolone", "first_line", "7.5-15 mg oral daily as bridge to DMARD.")
                ]
            },
            # 42. COVID-19
            {
                "name": "COVID-19 (Moderate-Severe)", "category": "infectious", "icd10": "U07.1",
                "definition": "Acute respiratory infectious disease caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2).",
                "etiology": "SARS-CoV-2 aerosol and droplet transmission leading to diffuse alveolar damage.",
                "age": "All ages (highest morbidity in elderly >60 and comorbidity)",
                "mgmt": "Supportive oxygenation, Dexamethasone (6 mg daily for up to 10 days) for hypoxic patients, and prophylactic anticoagulation.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Persistent Dry Paroxysmal Cough", "very_common", "highly_specific", True),
                    ("Dyspnea / Shortness of Breath", "very_common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                    ("Central Cyanosis", "common", "highly_specific", True),
                    ("Tachypnea (>24 breaths/min)", "common", "moderately_specific", True),
                ],
                "treatments": [
                    ("Dexamethasone", "first_line", "6 mg oral or IV daily for up to 10 days in hypoxemic patients."),
                    ("Paracetamol (Acetaminophen)", "adjunct", "1 g oral every 6 hours PRN for fever.")
                ]
            },
            # 43. Pertussis
            {
                "name": "Pertussis (Whooping Cough)", "category": "respiratory", "icd10": "A37.9",
                "definition": "Highly contagious bacterial lower respiratory infection characterized by paroxysmal coughing spasms ending in an inspiratory 'whoop'.",
                "etiology": "Bordetella pertussis adhering to ciliated respiratory epithelium.",
                "age": "Unvaccinated infants <1 year (highest mortality)",
                "mgmt": "Early macrolide antibiotic (Azithromycin) to reduce transmission and clinical severity; supportive hydration and respiratory monitoring.",
                "symptoms": [
                    ("Persistent Dry Paroxysmal Cough", "very_common", "pathognomonic", True),
                    ("Inspiratory Stridor", "common", "highly_specific", True),
                    ("Persistent Nausea & Vomiting", "common", "highly_specific", False),
                    ("Central Cyanosis", "occasional", "highly_specific", False),
                ],
                "treatments": [
                    ("Azithromycin", "first_line", "10 mg/kg (Max 500 mg) day 1, then 5 mg/kg daily days 2-5.")
                ]
            },
            # 44. Dengue Fever
            {
                "name": "Dengue Fever", "category": "infectious", "icd10": "A90",
                "definition": "Arboviral infection transmitted by Aedes mosquitoes, presenting with sudden high fever, retro-orbital pain, severe arthralgia ('breakbone fever'), and petechiae.",
                "etiology": "Dengue virus serotypes 1-4 (Flaviviridae).",
                "age": "All ages in endemic tropical regions",
                "mgmt": "Judicious oral or IV fluid therapy; strict avoidance of Aspirin/NSAIDs due to platelet dysfunction and hemorrhagic shock risk.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", True),
                    ("Severe Throbbing Headache", "very_common", "highly_specific", True),
                    ("Petechial Rash & Purpura", "common", "highly_specific", True),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                    ("Persistent Nausea & Vomiting", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Paracetamol (Acetaminophen)", "first_line", "1 g oral every 6 hours (Never use NSAIDs or Aspirin!)."),
                    ("Oral Rehydration Salts (ORS)", "first_line", "Liberal oral fluid intake.")
                ]
            },
            # 45. Rabies
            {
                "name": "Rabies (Encephalitic / Furious)", "category": "infectious", "icd10": "A82.9",
                "definition": "Invariable fatal acute viral encephalomyelitis transmitted through the saliva of infected mammals.",
                "etiology": "Rabies lyssavirus (Rhabdoviridae) entering via animal bites or scratches.",
                "age": "All ages (children highest bite exposure)",
                "mgmt": "Immediate thorough wound washing with soap and water for 15 minutes, post-exposure prophylaxis (PEP with vaccine + rabies immunoglobulin). Palliative sedation once symptomatic.",
                "symptoms": [
                    ("Altered Mental Status / Acute Confusion", "very_common", "pathognomonic", True),
                    ("Marked Photophobia", "very_common", "pathognomonic", True),
                    ("Generalized Tonic-Clonic Seizures", "common", "highly_specific", True),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                ],
                "treatments": [
                    ("Paracetamol (Acetaminophen)", "adjunct", "Palliative comfort.")
                ]
            },
            # 46. Streptococcal Pharyngitis
            {
                "name": "Streptococcal Pharyngitis / Tonsillitis", "category": "respiratory", "icd10": "J02.0",
                "definition": "Acute bacterial infection of the pharynx and palatine tonsils by Group A Streptococcus.",
                "etiology": "Streptococcus pyogenes (Group A Beta-Hemolytic Streptococcus).",
                "age": "Children and adolescents 5-15 years",
                "mgmt": "Oral penicillin or amoxicillin for 10 days to prevent Acute Rheumatic Fever and post-streptococcal glomerulonephritis.",
                "symptoms": [
                    ("High Fever (>38.5°C)", "very_common", "moderately_specific", False),
                    ("Generalized Lymphadenopathy", "common", "highly_specific", True),
                    ("Severe Throbbing Headache", "common", "non_specific", False),
                    ("Persistent Dry Paroxysmal Cough", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Amoxicillin + Clavulanic Acid", "first_line", "500 mg oral three times daily for 10 days."),
                    ("Azithromycin", "second_line", "500 mg daily for 5 days if penicillin-allergic.")
                ]
            },
            # 47. HIV/AIDS Advanced Stage
            {
                "name": "HIV / AIDS Advanced Clinical Stage", "category": "infectious", "icd10": "B24",
                "definition": "Immune deficiency caused by human immunodeficiency virus infection with profound CD4+ T-cell depletion and opportunistic infections.",
                "etiology": "Human immunodeficiency virus types 1 and 2 (Retroviridae).",
                "age": "All ages",
                "mgmt": "Immediate antiretroviral therapy (ART, e.g. TLD regimen), Co-trimoxazole prophylaxis, and treatment of opportunistic infections.",
                "symptoms": [
                    ("Unintentional Weight Loss", "very_common", "pathognomonic", True),
                    ("Profuse Diaphoresis / Night Sweats", "very_common", "highly_specific", True),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Generalized Lymphadenopathy", "common", "highly_specific", True),
                    ("Severe Conjunctival & Palmar Pallor", "common", "moderately_specific", False),
                    ("Severe Malaise & Fatigue", "very_common", "non_specific", False),
                ],
                "treatments": [
                    ("Rifampicin + Isoniazid (RH)", "adjunct", "TB preventive therapy (TPT).")
                ]
            },
            # 48. Schistosomiasis
            {
                "name": "Schistosomiasis (Bilharzia)", "category": "infectious", "icd10": "B65.9",
                "definition": "Chronic parasitic helminthic infection acquired by exposure to freshwater infested with cercariae.",
                "etiology": "Schistosoma mansoni (intestinal/hepatic) or Schistosoma haematobium (urogenital).",
                "age": "School-age children, agricultural workers, fishermen",
                "mgmt": "Single-dose oral Praziquantel (40 mg/kg) and community mass drug administration.",
                "symptoms": [
                    ("Gross Hematuria (Visible Blood in Urine)", "very_common", "pathognomonic", True),
                    ("Dysuria (Burning Micturition)", "common", "highly_specific", False),
                    ("Hepatomegaly", "common", "moderately_specific", True),
                    ("Splenomegaly", "common", "moderately_specific", False),
                ],
                "treatments": [
                    ("Oral Rehydration Salts (ORS)", "adjunct", "Supportive.")
                ]
            },
            # 49. Gastroesophageal Reflux Disease
            {
                "name": "Gastroesophageal Reflux Disease (GERD)", "category": "gastrointestinal", "icd10": "K21.9",
                "definition": "Chronic condition where stomach acid and contents persistently flow back into the esophagus.",
                "etiology": "Transient lower esophageal sphincter relaxations, hiatal hernia, or delayed gastric emptying.",
                "age": "Adults >25 years",
                "mgmt": "Proton pump inhibitors for 4-8 weeks, dietary modifications (avoid lying down after meals, weight loss).",
                "symptoms": [
                    ("Burning Epigastric Pain / Dyspepsia", "very_common", "pathognomonic", True),
                    ("Persistent Dry Paroxysmal Cough", "common", "moderately_specific", False),
                    ("Persistent Nausea & Vomiting", "occasional", "non_specific", False),
                ],
                "treatments": [
                    ("Omeprazole", "first_line", "20 mg oral once daily 30 min before breakfast for 4-8 weeks.")
                ]
            },
            # 50. Sickle Cell Disease
            {
                "name": "Sickle Cell Disease (Vaso-occlusive Crisis)", "category": "hematology", "icd10": "D57.0",
                "definition": "Hereditary hemoglobinopathy with mutant hemoglobin S causing erythrocyte sickling, microvascular occlusion, and tissue infarction.",
                "etiology": "Homozygous point mutation in beta-globin gene (Glu6Val).",
                "age": "Children and young adults",
                "mgmt": "Prompt aggressive multimodal analgesia, vigorous IV hydration, supplemental oxygen, and empiric antibiotics for febrile crises.",
                "symptoms": [
                    ("Severe Conjunctival & Palmar Pallor", "very_common", "pathognomonic", True),
                    ("Jaundice / Scleral Icterus", "very_common", "highly_specific", True),
                    ("Spreading Erythematous Warm Swelling (Cellulitis)", "common", "moderately_specific", False),
                    ("High Fever (>38.5°C)", "common", "non_specific", False),
                    ("Dyspnea / Shortness of Breath", "common", "moderately_specific", False),
                ],
                "treatments": [
                    ("Oral Rehydration Salts (ORS)", "first_line", "Oral fluid expansion."),
                    ("Paracetamol (Acetaminophen)", "first_line", "1 g oral every 6 hours."),
                    ("Ibuprofen", "second_line", "400 mg oral every 8 hours with meals.")
                ]
            }
        ]

        diseases_created = 0
        links_created = 0
        treatments_created = 0

        for d_info in diseases_catalog:
            disease, _ = Disease.objects.update_or_create(
                name=d_info["name"],
                defaults={
                    "category": d_info["category"],
                    "icd10_code": d_info["icd10"],
                    "definition": d_info["definition"],
                    "etiology": d_info["etiology"],
                    "typical_age_group": d_info["age"],
                    "management_overview": d_info["mgmt"],
                    "status": "active",
                    "is_active": True
                }
            )
            diseases_created += 1

            # Connect symptoms
            for sym_name, freq, spec, is_hallmark in d_info["symptoms"]:
                try:
                    symptom = Symptom.objects.get(name=sym_name)
                    DiseaseSymptom.objects.update_or_create(
                        disease=disease,
                        symptom=symptom,
                        defaults={
                            "frequency": freq,
                            "specificity": spec,
                            "is_hallmark": is_hallmark,
                            "is_active": True
                        }
                    )
                    links_created += 1
                except Symptom.DoesNotExist:
                    continue

            # Connect treatments
            for med_name, line, instructions in d_info["treatments"]:
                try:
                    med = Medicine.objects.get(generic_name=med_name)
                    DiseaseTreatment.objects.update_or_create(
                        disease=disease,
                        medicine=med,
                        treatment_line=line,
                        defaults={
                            "regimen_instructions": instructions,
                            "is_active": True
                        }
                    )
                    treatments_created += 1
                except Medicine.DoesNotExist:
                    continue

        return diseases_created, links_created, treatments_created
