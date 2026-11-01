# Database Design

## 1. Overview

This document describes the database schema for the Intelligent Medical and Hospital Management System. The design prioritizes data integrity, clinical safety, auditability, and scalability while maintaining flexibility for future enhancements.

## 2. Design Principles

1. **Data Integrity**: Foreign keys, constraints, and transactions ensure consistency
2. **Auditability**: All tables track creation, modification, and deletion events
3. **Versioning**: Clinical content supports version history
4. **Soft Deletes**: Important records use `is_active` flag instead of hard deletes
5. **UUID Primary Keys**: Use UUIDs for distributed system compatibility
6. **Normalized Design**: Follow 3NF with strategic denormalization
7. **Facility Isolation**: Multi-tenancy support through facility foreign keys
8. **Clinical Safety**: Constraints prevent dangerous data states

## 3. Database Technology

- **RDBMS**: PostgreSQL 15+
- **Extensions**:
  - `uuid-ossp` - UUID generation
  - `pg_trgm` - Fuzzy text search
  - `btree_gin` - Multi-column indexes
  - `pg_stat_statements` - Query performance monitoring

## 4. Common Patterns

### 4.1 Base Table Structure

All tables inherit common audit fields:

```sql
CREATE TABLE base_example (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL
);
```

### 4.2 Versioned Content Pattern

```sql
CREATE TABLE versioned_content_example (
    -- Base fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    -- Version control
    version INTEGER DEFAULT 1 NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    
    -- Approval tracking
    reviewed_by_id UUID REFERENCES accounts_user(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Version chain
    superseded_by_id UUID REFERENCES versioned_content_example(id),
    
    -- Content fields
    -- ...
    
    CHECK (status IN ('draft', 'in_review', 'approved', 'active', 'superseded', 'retired'))
);
```

### 4.3 Facility-Scoped Pattern

```sql
CREATE TABLE facility_scoped_example (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    -- Other fields...
    
    -- Ensure queries filter by facility
    INDEX idx_facility_id (facility_id)
);
```

## 5. Core Schema

### 5.1 Accounts Module

#### accounts_user

```sql
CREATE TABLE accounts_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_staff BOOLEAN DEFAULT false NOT NULL,
    is_superuser BOOLEAN DEFAULT false NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Security
    must_change_password BOOLEAN DEFAULT false NOT NULL,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- MFA
    mfa_enabled BOOLEAN DEFAULT false NOT NULL,
    mfa_secret VARCHAR(32),
    
    -- Profile
    phone VARCHAR(20),
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_is_active (is_active)
);
```

#### accounts_role

```sql
CREATE TABLE accounts_role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (code IN (
        'system_admin', 'hospital_admin', 'receptionist', 
        'triage_nurse', 'doctor', 'nurse', 'pharmacist',
        'lab_staff', 'radiology_staff', 'medical_editor',
        'clinical_reviewer', 'ml_reviewer', 'auditor'
    ))
);
```

#### accounts_userrole

```sql
CREATE TABLE accounts_userrole (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES accounts_user(id) ON DELETE CASCADE NOT NULL,
    role_id UUID REFERENCES accounts_role(id) ON DELETE CASCADE NOT NULL,
    facility_id UUID REFERENCES organizations_facility(id) ON DELETE CASCADE,
    granted_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    UNIQUE (user_id, role_id, facility_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id),
    INDEX idx_facility_id (facility_id)
);
```

#### accounts_permission

```sql
CREATE TABLE accounts_permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    
    INDEX idx_resource_action (resource_type, action)
);
```

#### accounts_rolepermission

```sql
CREATE TABLE accounts_rolepermission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID REFERENCES accounts_role(id) ON DELETE CASCADE NOT NULL,
    permission_id UUID REFERENCES accounts_permission(id) ON DELETE CASCADE NOT NULL,
    
    UNIQUE (role_id, permission_id),
    INDEX idx_role_id (role_id)
);
```

### 5.2 Organizations Module

#### organizations_organization

```sql
CREATE TABLE organizations_organization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    organization_type VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (organization_type IN ('hospital', 'clinic', 'health_center', 'laboratory', 'pharmacy')),
    INDEX idx_code (code),
    INDEX idx_is_active (is_active)
);
```

#### organizations_facility

```sql
CREATE TABLE organizations_facility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations_organization(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) NOT NULL,
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(254),
    website VARCHAR(255),
    
    -- Operational
    license_number VARCHAR(100),
    accreditation_status VARCHAR(50),
    bed_capacity INTEGER,
    operating_status VARCHAR(20) DEFAULT 'active' NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    UNIQUE (organization_id, code),
    CHECK (facility_type IN ('hospital', 'clinic', 'health_center', 'laboratory', 'pharmacy')),
    CHECK (operating_status IN ('active', 'inactive', 'suspended')),
    INDEX idx_organization_id (organization_id),
    INDEX idx_code (code)
);
```

#### organizations_department

```sql
CREATE TABLE organizations_department (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL,
    department_type VARCHAR(50) NOT NULL,
    description TEXT,
    head_id UUID REFERENCES accounts_user(id),
    phone VARCHAR(20),
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    UNIQUE (facility_id, code),
    CHECK (department_type IN (
        'emergency', 'outpatient', 'inpatient', 'surgery', 'icu',
        'laboratory', 'radiology', 'pharmacy', 'administration'
    )),
    INDEX idx_facility_id (facility_id),
    INDEX idx_is_active (is_active)
);
```

### 5.3 Patients Module

#### patients_patient

```sql
CREATE TABLE patients_patient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identifiers
    patient_number VARCHAR(50) UNIQUE NOT NULL,
    national_id VARCHAR(50),
    passport_number VARCHAR(50),
    
    -- Demographics
    first_name VARCHAR(150) NOT NULL,
    middle_name VARCHAR(150),
    last_name VARCHAR(150) NOT NULL,
    date_of_birth DATE NOT NULL,
    sex VARCHAR(10) NOT NULL,
    gender_identity VARCHAR(50),
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(254),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'ET' NOT NULL,
    
    -- Clinical
    blood_group VARCHAR(5),
    photo_url VARCHAR(500),
    
    -- Consent
    consent_for_treatment BOOLEAN DEFAULT false NOT NULL,
    consent_for_research BOOLEAN DEFAULT false NOT NULL,
    consent_date TIMESTAMP WITH TIME ZONE,
    
    -- Registration
    registered_facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (sex IN ('male', 'female', 'other', 'unknown')),
    CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    INDEX idx_patient_number (patient_number),
    INDEX idx_national_id (national_id),
    INDEX idx_last_name (last_name),
    INDEX idx_date_of_birth (date_of_birth),
    INDEX idx_registered_facility (registered_facility_id)
);
```

#### patients_emergencycontact

```sql
CREATE TABLE patients_emergencycontact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients_patient(id) ON DELETE CASCADE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    email VARCHAR(254),
    address VARCHAR(500),
    is_primary BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    INDEX idx_patient_id (patient_id)
);
```

#### patients_allergy

```sql
CREATE TABLE patients_allergy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients_patient(id) ON DELETE CASCADE NOT NULL,
    allergen_type VARCHAR(50) NOT NULL,
    allergen VARCHAR(200) NOT NULL,
    reaction_type VARCHAR(100),
    severity VARCHAR(20) NOT NULL,
    onset_date DATE,
    notes TEXT,
    verified BOOLEAN DEFAULT false NOT NULL,
    verified_by_id UUID REFERENCES accounts_user(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (allergen_type IN ('drug', 'food', 'environmental', 'other')),
    CHECK (severity IN ('mild', 'moderate', 'severe', 'life_threatening')),
    INDEX idx_patient_id (patient_id),
    INDEX idx_allergen_type (allergen_type),
    INDEX idx_is_active (is_active)
);
```

#### patients_medicalhistory

```sql
CREATE TABLE patients_medicalhistory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients_patient(id) ON DELETE CASCADE NOT NULL,
    condition_type VARCHAR(50) NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    icd_code VARCHAR(20),
    diagnosis_date DATE,
    ongoing BOOLEAN DEFAULT true NOT NULL,
    resolution_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (condition_type IN ('chronic_disease', 'past_surgery', 'family_history', 'social_history')),
    INDEX idx_patient_id (patient_id),
    INDEX idx_condition_type (condition_type),
    INDEX idx_ongoing (ongoing)
);
```

### 5.4 Encounters Module

#### encounters_encounter

```sql
CREATE TABLE encounters_encounter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id UUID REFERENCES patients_patient(id) NOT NULL,
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    department_id UUID REFERENCES organizations_department(id),
    
    -- Encounter details
    encounter_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'in_progress' NOT NULL,
    priority VARCHAR(20) DEFAULT 'routine',
    
    -- Timing
    admission_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    discharge_datetime TIMESTAMP WITH TIME ZONE,
    
    -- Clinical
    chief_complaint TEXT,
    presenting_complaint TEXT,
    triage_category VARCHAR(20),
    
    -- Staff
    attending_physician_id UUID REFERENCES accounts_user(id),
    admitting_nurse_id UUID REFERENCES accounts_user(id),
    
    -- Outcome
    discharge_disposition VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (encounter_type IN ('outpatient', 'emergency', 'inpatient', 'day_surgery')),
    CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    CHECK (priority IN ('routine', 'urgent', 'emergency', 'resuscitation')),
    CHECK (triage_category IN ('immediate', 'very_urgent', 'urgent', 'standard', 'non_urgent')),
    INDEX idx_encounter_number (encounter_number),
    INDEX idx_patient_id (patient_id),
    INDEX idx_facility_id (facility_id),
    INDEX idx_status (status),
    INDEX idx_admission_datetime (admission_datetime)
);
```

#### encounters_clinicalnote

```sql
CREATE TABLE encounters_clinicalnote (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID REFERENCES encounters_encounter(id) ON DELETE CASCADE NOT NULL,
    note_type VARCHAR(50) NOT NULL,
    note_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    author_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    -- Approval
    is_finalized BOOLEAN DEFAULT false NOT NULL,
    finalized_at TIMESTAMP WITH TIME ZONE,
    
    -- Amendment
    amended_from_id UUID REFERENCES encounters_clinicalnote(id),
    amendment_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (note_type IN (
        'history', 'examination', 'assessment', 'plan',
        'progress', 'discharge', 'consultation', 'procedure'
    )),
    INDEX idx_encounter_id (encounter_id),
    INDEX idx_note_type (note_type),
    INDEX idx_note_datetime (note_datetime),
    INDEX idx_author_id (author_id)
);
```

#### encounters_observation

```sql
CREATE TABLE encounters_observation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID REFERENCES encounters_encounter(id) ON DELETE CASCADE NOT NULL,
    observation_type VARCHAR(50) NOT NULL,
    observation_code VARCHAR(50),
    observed_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Value (use appropriate field based on type)
    value_numeric NUMERIC(10, 2),
    value_text VARCHAR(500),
    value_boolean BOOLEAN,
    value_datetime TIMESTAMP WITH TIME ZONE,
    
    -- Units and interpretation
    unit VARCHAR(50),
    reference_range_min NUMERIC(10, 2),
    reference_range_max NUMERIC(10, 2),
    interpretation VARCHAR(20),
    
    -- Context
    body_site VARCHAR(100),
    method VARCHAR(100),
    notes TEXT,
    
    -- Observer
    observed_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    -- Status
    is_critical BOOLEAN DEFAULT false NOT NULL,
    is_abnormal BOOLEAN DEFAULT false NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (observation_type IN (
        'vital_sign', 'physical_exam', 'symptom', 'sign', 'measurement'
    )),
    CHECK (interpretation IN ('normal', 'low', 'high', 'critical_low', 'critical_high')),
    INDEX idx_encounter_id (encounter_id),
    INDEX idx_observation_type (observation_type),
    INDEX idx_observed_datetime (observed_datetime),
    INDEX idx_is_critical (is_critical)
);
```

### 5.5 Medical Knowledge Module

#### medical_knowledge_disease

```sql
CREATE TABLE medical_knowledge_disease (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identification
    name VARCHAR(255) NOT NULL,
    name_local JSONB,  -- {"am": "name in Amharic", "om": "name in Oromo"}
    synonyms TEXT[],
    
    -- Classification
    category VARCHAR(100),
    icd10_code VARCHAR(20),
    icd11_code VARCHAR(20),
    
    -- Clinical Information
    definition TEXT,
    etiology TEXT,
    risk_factors TEXT[],
    complications TEXT[],
    typical_age_group VARCHAR(50),
    
    -- Diagnostic Criteria
    diagnostic_criteria JSONB,
    
    -- Management
    management_overview TEXT,
    prevention_guidance TEXT,
    referral_criteria TEXT,
    
    -- Provenance
    source_organization VARCHAR(255),
    source_url VARCHAR(500),
    source_version VARCHAR(50),
    publication_date DATE,
    jurisdiction VARCHAR(50),
    
    -- Lifecycle
    version INTEGER DEFAULT 1 NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    reviewed_by_id UUID REFERENCES accounts_user(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    superseded_by_id UUID REFERENCES medical_knowledge_disease(id),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (status IN ('draft', 'in_review', 'approved', 'active', 'superseded', 'retired')),
    INDEX idx_name (name),
    INDEX idx_icd10_code (icd10_code),
    INDEX idx_status (status),
    INDEX idx_category (category)
);
```

#### medical_knowledge_symptom

```sql
CREATE TABLE medical_knowledge_symptom (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    name_local JSONB,
    synonyms TEXT[],
    description TEXT,
    category VARCHAR(100),
    body_system VARCHAR(100),
    symptom_type VARCHAR(20) NOT NULL,
    snomed_code VARCHAR(50),
    icon_name VARCHAR(50),
    
    -- Lifecycle
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (symptom_type IN ('symptom', 'sign', 'both')),
    CHECK (status IN ('draft', 'active', 'retired')),
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_body_system (body_system)
);
```

#### medical_knowledge_diseasesymptom

```sql
CREATE TABLE medical_knowledge_diseasesymptom (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disease_id UUID REFERENCES medical_knowledge_disease(id) ON DELETE CASCADE NOT NULL,
    symptom_id UUID REFERENCES medical_knowledge_symptom(id) ON DELETE CASCADE NOT NULL,
    
    -- Association strength
    frequency VARCHAR(20) NOT NULL,
    specificity VARCHAR(20),
    stage VARCHAR(50),
    notes TEXT,
    
    -- Evidence
    evidence_level VARCHAR(20),
    source VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    UNIQUE (disease_id, symptom_id),
    CHECK (frequency IN ('very_common', 'common', 'occasional', 'rare')),
    CHECK (specificity IN ('highly_specific', 'moderately_specific', 'non_specific')),
    INDEX idx_disease_id (disease_id),
    INDEX idx_symptom_id (symptom_id)
);
```

#### medical_knowledge_medicine

```sql
CREATE TABLE medical_knowledge_medicine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Names
    generic_name VARCHAR(255) NOT NULL,
    brand_names TEXT[],
    local_names JSONB,
    
    -- Classification
    drug_class VARCHAR(100),
    atc_code VARCHAR(20),
    
    -- Formulation
    dosage_form VARCHAR(100) NOT NULL,
    strength VARCHAR(100),
    unit VARCHAR(50),
    route_of_administration VARCHAR(50) NOT NULL,
    
    -- Clinical
    indications TEXT[],
    contraindications TEXT[],
    warnings TEXT[],
    adverse_reactions TEXT[],
    pregnancy_category VARCHAR(5),
    breastfeeding_safety VARCHAR(50),
    
    -- Dosing
    adult_dosing TEXT,
    pediatric_dosing TEXT,
    renal_adjustment TEXT,
    hepatic_adjustment TEXT,
    maximum_dose VARCHAR(200),
    
    -- Drug Interactions
    -- Stored in separate table
    
    -- Administration
    administration_instructions TEXT,
    monitoring_requirements TEXT[],
    storage_requirements TEXT,
    
    -- Formulary
    formulary_status VARCHAR(50),
    restricted BOOLEAN DEFAULT false NOT NULL,
    registration_number VARCHAR(100),
    manufacturer VARCHAR(255),
    
    -- Provenance
    source_organization VARCHAR(255),
    source_version VARCHAR(50),
    source_url VARCHAR(500),
    
    -- Lifecycle
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (status IN ('draft', 'active', 'retired')),
    CHECK (dosage_form IN (
        'tablet', 'capsule', 'syrup', 'suspension', 'injection',
        'ointment', 'cream', 'drops', 'inhaler', 'patch'
    )),
    INDEX idx_generic_name (generic_name),
    INDEX idx_drug_class (drug_class),
    INDEX idx_status (status)
);
```

#### medical_knowledge_druginteraction

```sql
CREATE TABLE medical_knowledge_druginteraction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medicine_a_id UUID REFERENCES medical_knowledge_medicine(id) NOT NULL,
    medicine_b_id UUID REFERENCES medical_knowledge_medicine(id) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    clinical_management TEXT,
    evidence_level VARCHAR(20),
    source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (severity IN ('contraindicated', 'major', 'moderate', 'minor')),
    CHECK (interaction_type IN (
        'pharmacodynamic', 'pharmacokinetic', 'additive_toxicity', 'other'
    )),
    CHECK (medicine_a_id < medicine_b_id), -- Prevent duplicates
    UNIQUE (medicine_a_id, medicine_b_id),
    INDEX idx_medicine_a (medicine_a_id),
    INDEX idx_medicine_b (medicine_b_id),
    INDEX idx_severity (severity)
);
```

## 6. Clinical Decision Support

### decision_support_request

```sql
CREATE TABLE decision_support_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID REFERENCES encounters_encounter(id) NOT NULL,
    request_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Input data snapshot
    symptoms JSONB NOT NULL,
    signs JSONB,
    vital_signs JSONB,
    patient_demographics JSONB NOT NULL,
    medical_history JSONB,
    
    -- Engine version
    engine_version VARCHAR(50) NOT NULL,
    model_version VARCHAR(50),
    
    -- Result
    processing_status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    -- Requesting user
    requested_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    INDEX idx_encounter_id (encounter_id),
    INDEX idx_request_datetime (request_datetime),
    INDEX idx_processing_status (processing_status)
);
```

### decision_support_candidate

```sql
CREATE TABLE decision_support_candidate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES decision_support_request(id) ON DELETE CASCADE NOT NULL,
    disease_id UUID REFERENCES medical_knowledge_disease(id) NOT NULL,
    
    -- Ranking
    rank INTEGER NOT NULL,
    confidence_level VARCHAR(20),
    
    -- Evidence
    supporting_findings JSONB NOT NULL,
    contradicting_findings JSONB,
    missing_information JSONB,
    red_flags JSONB,
    
    -- Recommendations
    suggested_investigations JSONB,
    diagnostic_criteria_met JSONB,
    
    -- Clinician Feedback
    clinician_decision VARCHAR(20),
    clinician_feedback TEXT,
    decided_by_id UUID REFERENCES accounts_user(id),
    decided_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (confidence_level IN ('high', 'moderate', 'low', 'uncertain')),
    CHECK (clinician_decision IN ('confirmed', 'rejected', 'deferred', 'requires_investigation')),
    INDEX idx_request_id (request_id),
    INDEX idx_disease_id (disease_id),
    INDEX idx_rank (rank)
);
```

## 7. Prescriptions and Pharmacy

### prescriptions_prescription

```sql
CREATE TABLE prescriptions_prescription (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_number VARCHAR(50) UNIQUE NOT NULL,
    encounter_id UUID REFERENCES encounters_encounter(id) NOT NULL,
    patient_id UUID REFERENCES patients_patient(id) NOT NULL,
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    
    -- Lifecycle
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    prescribed_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Prescriber
    prescriber_id UUID REFERENCES accounts_user(id) NOT NULL,
    prescriber_signature VARCHAR(500),
    
    -- Approval
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Pharmacy review
    reviewed_by_pharmacist_id UUID REFERENCES accounts_user(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    pharmacy_notes TEXT,
    
    -- Validity
    valid_until DATE,
    
    -- Cancellation
    cancelled_by_id UUID REFERENCES accounts_user(id),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (status IN ('draft', 'pending_approval', 'approved', 'dispensed', 'partially_dispensed', 'completed', 'cancelled')),
    INDEX idx_prescription_number (prescription_number),
    INDEX idx_patient_id (patient_id),
    INDEX idx_encounter_id (encounter_id),
    INDEX idx_status (status),
    INDEX idx_prescribed_datetime (prescribed_datetime)
);
```

### prescriptions_prescriptionitem

```sql
CREATE TABLE prescriptions_prescriptionitem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id UUID REFERENCES prescriptions_prescription(id) ON DELETE CASCADE NOT NULL,
    medicine_id UUID REFERENCES medical_knowledge_medicine(id) NOT NULL,
    
    -- Dosing
    dose VARCHAR(100) NOT NULL,
    dose_unit VARCHAR(50) NOT NULL,
    route VARCHAR(50) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration_value INTEGER,
    duration_unit VARCHAR(20),
    
    -- Quantity
    quantity NUMERIC(10, 2) NOT NULL,
    quantity_unit VARCHAR(50) NOT NULL,
    
    -- Instructions
    indication VARCHAR(255),
    instructions TEXT,
    special_instructions TEXT,
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE,
    
    -- Substitution
    substitution_allowed BOOLEAN DEFAULT true NOT NULL,
    
    -- Safety checks performed
    safety_checks_passed BOOLEAN DEFAULT false NOT NULL,
    safety_warnings JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (route IN (
        'oral', 'iv', 'im', 'sc', 'topical', 'inhalation',
        'nasal', 'ophthalmic', 'otic', 'rectal', 'vaginal'
    )),
    CHECK (duration_unit IN ('days', 'weeks', 'months')),
    INDEX idx_prescription_id (prescription_id),
    INDEX idx_medicine_id (medicine_id)
);
```

### pharmacy_inventoryitem

```sql
CREATE TABLE pharmacy_inventoryitem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    medicine_id UUID REFERENCES medical_knowledge_medicine(id) NOT NULL,
    
    -- Stock
    current_stock NUMERIC(10, 2) DEFAULT 0 NOT NULL,
    stock_unit VARCHAR(50) NOT NULL,
    reorder_level NUMERIC(10, 2) NOT NULL,
    reorder_quantity NUMERIC(10, 2),
    
    -- Storage
    storage_location VARCHAR(100),
    storage_conditions TEXT,
    
    -- Status
    is_available BOOLEAN DEFAULT true NOT NULL,
    is_restricted BOOLEAN DEFAULT false NOT NULL,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    UNIQUE (facility_id, medicine_id),
    INDEX idx_facility_id (facility_id),
    INDEX idx_medicine_id (medicine_id),
    INDEX idx_current_stock (current_stock)
);
```

### pharmacy_stockbatch

```sql
CREATE TABLE pharmacy_stockbatch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_item_id UUID REFERENCES pharmacy_inventoryitem(id) NOT NULL,
    batch_number VARCHAR(100) NOT NULL,
    
    -- Quantities
    received_quantity NUMERIC(10, 2) NOT NULL,
    current_quantity NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    
    -- Dates
    manufacture_date DATE,
    expiry_date DATE NOT NULL,
    received_date DATE DEFAULT CURRENT_DATE NOT NULL,
    
    -- Supplier
    supplier VARCHAR(255),
    purchase_price NUMERIC(10, 2),
    selling_price NUMERIC(10, 2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'available' NOT NULL,
    quarantine_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (status IN ('available', 'quarantined', 'expired', 'recalled', 'depleted')),
    UNIQUE (inventory_item_id, batch_number),
    INDEX idx_inventory_item_id (inventory_item_id),
    INDEX idx_expiry_date (expiry_date),
    INDEX idx_status (status)
);
```

### pharmacy_dispensing

```sql
CREATE TABLE pharmacy_dispensing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_item_id UUID REFERENCES prescriptions_prescriptionitem(id) NOT NULL,
    stock_batch_id UUID REFERENCES pharmacy_stockbatch(id) NOT NULL,
    
    -- Quantities
    quantity_dispensed NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    
    -- Dispensing details
    dispensed_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    dispensed_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    
    -- Patient interaction
    patient_counseled BOOLEAN DEFAULT false NOT NULL,
    counseling_notes TEXT,
    
    -- Substitution
    is_substitution BOOLEAN DEFAULT false NOT NULL,
    substitution_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    INDEX idx_prescription_item_id (prescription_item_id),
    INDEX idx_dispensed_datetime (dispensed_datetime),
    INDEX idx_dispensed_by_id (dispensed_by_id)
);
```

## 8. Laboratory and Imaging

### laboratory_labtest

```sql
CREATE TABLE laboratory_labtest (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(255) NOT NULL,
    test_code VARCHAR(50) UNIQUE NOT NULL,
    test_category VARCHAR(100) NOT NULL,
    description TEXT,
    specimen_type VARCHAR(100) NOT NULL,
    specimen_volume VARCHAR(50),
    turnaround_time_hours INTEGER,
    
    -- Status
    is_available BOOLEAN DEFAULT true NOT NULL,
    requires_fasting BOOLEAN DEFAULT false NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    INDEX idx_test_code (test_code),
    INDEX idx_test_category (test_category),
    INDEX idx_is_available (is_available)
);
```

### laboratory_laborder

```sql
CREATE TABLE laboratory_laborder (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    encounter_id UUID REFERENCES encounters_encounter(id) NOT NULL,
    patient_id UUID REFERENCES patients_patient(id) NOT NULL,
    facility_id UUID REFERENCES organizations_facility(id) NOT NULL,
    lab_test_id UUID REFERENCES laboratory_labtest(id) NOT NULL,
    
    -- Order details
    ordered_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ordered_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    priority VARCHAR(20) DEFAULT 'routine' NOT NULL,
    clinical_info TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    
    -- Specimen
    specimen_collected BOOLEAN DEFAULT false NOT NULL,
    specimen_collected_datetime TIMESTAMP WITH TIME ZONE,
    specimen_collected_by_id UUID REFERENCES accounts_user(id),
    
    -- Result
    result_available BOOLEAN DEFAULT false NOT NULL,
    result_datetime TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    CHECK (priority IN ('stat', 'urgent', 'routine')),
    CHECK (status IN ('pending', 'specimen_collected', 'in_progress', 'completed', 'cancelled')),
    INDEX idx_order_number (order_number),
    INDEX idx_encounter_id (encounter_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status),
    INDEX idx_ordered_datetime (ordered_datetime)
);
```

### laboratory_labresult

```sql
CREATE TABLE laboratory_labresult (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_order_id UUID REFERENCES laboratory_laborder(id) ON DELETE CASCADE NOT NULL,
    
    -- Result value
    result_value VARCHAR(500) NOT NULL,
    result_unit VARCHAR(50),
    result_type VARCHAR(20) NOT NULL,
    
    -- Reference range
    reference_range_min NUMERIC(10, 2),
    reference_range_max NUMERIC(10, 2),
    reference_range_text VARCHAR(200),
    
    -- Interpretation
    interpretation VARCHAR(20),
    is_abnormal BOOLEAN DEFAULT false NOT NULL,
    is_critical BOOLEAN DEFAULT false NOT NULL,
    
    -- Status
    result_status VARCHAR(20) DEFAULT 'preliminary' NOT NULL,
    
    -- Personnel
    entered_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    entered_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    verified_by_id UUID REFERENCES accounts_user(id),
    verified_datetime TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    lab_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (result_type IN ('numeric', 'text', 'coded')),
    CHECK (interpretation IN ('normal', 'low', 'high', 'critical_low', 'critical_high', 'abnormal')),
    CHECK (result_status IN ('preliminary', 'final', 'corrected', 'cancelled')),
    INDEX idx_lab_order_id (lab_order_id),
    INDEX idx_is_critical (is_critical),
    INDEX idx_entered_datetime (entered_datetime)
);
```

## 9. Machine Learning Governance

### ml_governance_dataset

```sql
CREATE TABLE ml_governance_dataset (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Data characteristics
    total_records INTEGER NOT NULL,
    feature_schema JSONB NOT NULL,
    target_variable VARCHAR(100) NOT NULL,
    date_range_start DATE,
    date_range_end DATE,
    
    -- Data quality
    completeness_score NUMERIC(5, 2),
    quality_metrics JSONB,
    
    -- Splits
    training_records INTEGER,
    validation_records INTEGER,
    test_records INTEGER,
    
    -- Storage
    storage_location VARCHAR(500) NOT NULL,
    file_format VARCHAR(50),
    file_size_bytes BIGINT,
    
    -- Provenance
    source_query TEXT,
    inclusion_criteria TEXT,
    exclusion_criteria TEXT,
    
    -- Approval
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    approved_by_id UUID REFERENCES accounts_user(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    UNIQUE (name, version),
    CHECK (status IN ('draft', 'approved', 'deprecated')),
    INDEX idx_name_version (name, version),
    INDEX idx_status (status)
);
```

### ml_governance_model

```sql
CREATE TABLE ml_governance_model (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    
    -- Purpose
    intended_use TEXT NOT NULL,
    clinical_domain VARCHAR(100),
    target_population TEXT,
    
    -- Training
    dataset_id UUID REFERENCES ml_governance_dataset(id) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    hyperparameters JSONB,
    training_duration_seconds INTEGER,
    
    -- Performance
    evaluation_metrics JSONB NOT NULL,
    validation_metrics JSONB,
    test_metrics JSONB,
    
    -- Model artifacts
    model_file_path VARCHAR(500) NOT NULL,
    model_size_bytes BIGINT,
    feature_importance JSONB,
    
    -- Limitations
    known_limitations TEXT NOT NULL,
    contraindications TEXT,
    out_of_scope_use TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'development' NOT NULL,
    approval_status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    
    -- Deployment
    deployed BOOLEAN DEFAULT false NOT NULL,
    deployed_at TIMESTAMP WITH TIME ZONE,
    deployment_environment VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id UUID REFERENCES accounts_user(id) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    UNIQUE (model_name, version),
    CHECK (status IN ('development', 'evaluation', 'approved', 'deployed', 'retired')),
    CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    INDEX idx_model_name_version (model_name, version),
    INDEX idx_status (status),
    INDEX idx_deployed (deployed)
);
```

### ml_governance_modelapproval

```sql
CREATE TABLE ml_governance_modelapproval (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES ml_governance_model(id) NOT NULL,
    reviewer_id UUID REFERENCES accounts_user(id) NOT NULL,
    reviewer_role VARCHAR(50) NOT NULL,
    
    -- Decision
    decision VARCHAR(20) NOT NULL,
    decision_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Review
    review_comments TEXT,
    concerns JSONB,
    conditions TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CHECK (decision IN ('approved', 'rejected', 'conditional_approval', 'requires_revision')),
    CHECK (reviewer_role IN ('clinical_reviewer', 'ml_reviewer', 'safety_reviewer', 'compliance_reviewer')),
    INDEX idx_model_id (model_id),
    INDEX idx_reviewer_id (reviewer_id),
    INDEX idx_decision (decision)
);
```

## 10. Audit and Reporting

### audit_auditlog

```sql
CREATE TABLE audit_auditlog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Actor
    user_id UUID REFERENCES accounts_user(id),
    username VARCHAR(150),
    ip_address INET,
    session_id VARCHAR(255),
    
    -- Action
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    resource_representation TEXT,
    
    -- Result
    outcome VARCHAR(20) NOT NULL,
    error_message TEXT,
    
    -- Context
    facility_id UUID REFERENCES organizations_facility(id),
    patient_id UUID REFERENCES patients_patient(id),
    
    -- Request details
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    request_body JSONB,
    response_status INTEGER,
    
    -- Changes
    changes_made JSONB,
    
    CHECK (outcome IN ('success', 'failure', 'error')),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_resource_type (resource_type),
    INDEX idx_resource_id (resource_id),
    INDEX idx_action (action),
    INDEX idx_patient_id (patient_id),
    INDEX idx_facility_id (facility_id)
);
```

## 11. Database Indexes

Key indexes have been defined inline. Additional performance indexes should be added based on query patterns observed in production:

```sql
-- Full-text search indexes
CREATE INDEX idx_patient_name_search ON patients_patient 
USING gin(to_tsvector('english', first_name || ' ' || last_name));

CREATE INDEX idx_disease_name_search ON medical_knowledge_disease
USING gin(to_tsvector('english', name));

-- Composite indexes for common queries
CREATE INDEX idx_encounter_patient_facility ON encounters_encounter(patient_id, facility_id, admission_datetime);

CREATE INDEX idx_prescription_patient_status ON prescriptions_prescription(patient_id, status, prescribed_datetime);

-- Partial indexes for active records
CREATE INDEX idx_active_patients ON patients_patient(last_name, first_name) WHERE is_active = true;

CREATE INDEX idx_active_diseases ON medical_knowledge_disease(name) WHERE status = 'active' AND is_active = true;
```

## 12. Database Constraints

### 12.1 Check Constraints

All enum-like fields use CHECK constraints to ensure data validity.

### 12.2 Foreign Key Constraints

- `ON DELETE CASCADE`: Used for true dependent data (e.g., prescription items)
- `ON DELETE PROTECT`: Used for referenced data that should not be deleted if in use
- `ON DELETE SET NULL`: Rarely used, mainly for optional references

### 12.3 Unique Constraints

- Natural keys (patient_number, prescription_number, etc.)
- Composite unique constraints (user_id + role_id + facility_id)

## 13. Data Retention and Archival

### 13.1 Retention Policies

| Data Type | Retention Period | Archive Strategy |
|-----------|------------------|------------------|
| Active patient records | Indefinite | Keep in primary database |
| Inactive patients (no encounter > 10 years) | Indefinite | Move to archive database |
| Audit logs | 7 years | Move to cold storage after 1 year |
| ML training data | Duration of model lifecycle | Archive with model artifacts |
| Temporary data (sessions, cache) | 24-48 hours | Auto-delete |

### 13.2 Archival Process

1. Identify records meeting archival criteria
2. Export to encrypted archive storage
3. Verify archive integrity
4. Soft delete from primary database (mark is_active = false)
5. Hard delete after verification period (optional)

## 14. Database Migrations

### 14.1 Migration Strategy

- Use Django migrations for schema changes
- Always generate migrations before applying
- Review migration SQL before production deployment
- Test migrations on copy of production data
- Ensure migrations are reversible where possible
- Document breaking changes

### 14.2 Migration Safety

```python
# Safe operations:
- Adding nullable columns
- Adding tables
- Adding indexes
- Extending varchar length

# Requires downtime or careful planning:
- Dropping columns
- Changing column types
- Adding NOT NULL columns
- Renaming tables/columns

# Use multi-step migrations for risky changes:
1. Add new column (nullable)
2. Backfill data
3. Make column NOT NULL
4. Drop old column
```

## 15. Performance Considerations

### 15.1 Query Optimization

- Use `select_related()` for foreign keys
- Use `prefetch_related()` for reverse foreign keys and many-to-many
- Add indexes based on WHERE, JOIN, and ORDER BY clauses
- Use database views for complex frequently-used queries
- Implement query result caching for expensive operations

### 15.2 Partitioning Strategy (Future)

Consider partitioning for very large tables:

```sql
-- Example: Partition audit logs by month
CREATE TABLE audit_auditlog_y2026m10 PARTITION OF audit_auditlog
FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
```

## 16. Backup and Recovery

### 16.1 Backup Strategy

```bash
# Daily full backup
pg_dump -Fc -f backup_$(date +%Y%m%d).dump intelligent_medical_db

# Continuous WAL archiving for point-in-time recovery
archive_command = 'cp %p /backup/wal_archive/%f'
```

### 16.2 Recovery Testing

- Test backup restoration monthly
- Document recovery procedures
- Measure Recovery Time Objective (RTO) and Recovery Point Objective (RPO)

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Status**: APPROVED FOR DEVELOPMENT
