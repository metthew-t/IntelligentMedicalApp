# API Design Specification

## 1. Overview

The Intelligent Medical and Hospital Management System exposes a RESTful API built with Django REST Framework. The API follows industry best practices for healthcare APIs while maintaining simplicity and developer-friendliness.

## 2. API Principles

1. **RESTful Design** - Resource-oriented URLs and HTTP methods
2. **Versioned** - API version in URL path (`/api/v1/`)
3. **Consistent** - Uniform response formats and error handling
4. **Secure** - Authentication required for all endpoints except login
5. **Documented** - OpenAPI/Swagger documentation available
6. **Paginated** - Large result sets automatically paginated
7. **Filterable** - Query parameters for searching and filtering
8. **HATEOAS** - Hypermedia links where appropriate

## 3. Base URL

```
Development: http://localhost:8000/api/v1/
Production: https://api.intelligent-medical.example.com/api/v1/
```

## 4. Authentication

### 4.1 JWT Authentication

The API uses JWT (JSON Web Tokens) for authentication.

**Login Request:**
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Login Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["doctor"],
    "facility": {
      "id": "uuid",
      "name": "General Hospital"
    }
  },
  "expires_in": 900
}
```

**Using Access Token:**
```http
GET /api/v1/patients/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Token Refresh:**
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token Lifetime:**
- Access Token: 15 minutes
- Refresh Token: 7 days

### 4.2 Logout

```http
POST /api/v1/auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 5. Standard Response Formats

### 5.1 Success Response (Single Resource)

```json
{
  "data": {
    "id": "uuid",
    "patient_number": "P-2026-00001",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_of_birth": "1985-03-15",
    "sex": "female",
    "phone": "+251911234567",
    "created_at": "2026-10-15T10:30:00Z",
    "updated_at": "2026-10-15T10:30:00Z"
  },
  "meta": {
    "timestamp": "2026-10-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 5.2 Success Response (List)

```json
{
  "data": [
    {
      "id": "uuid",
      "patient_number": "P-2026-00001",
      "first_name": "Jane",
      "last_name": "Doe"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "total_count": 95,
    "next": "/api/v1/patients/?page=2",
    "previous": null
  },
  "meta": {
    "timestamp": "2026-10-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 5.3 Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "date_of_birth": [
        "This field is required."
      ],
      "phone": [
        "Invalid phone number format."
      ]
    },
    "timestamp": "2026-10-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 5.4 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTHENTICATION_FAILED | 401 | Invalid credentials or token |
| PERMISSION_DENIED | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid input data |
| CONFLICT | 409 | Resource conflict (e.g., duplicate) |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |
| CLINICAL_SAFETY_ERROR | 422 | Clinical safety check failed |

## 6. Endpoint Catalog

### 6.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login/` | User login |
| POST | `/auth/logout/` | User logout |
| POST | `/auth/refresh/` | Refresh access token |
| POST | `/auth/password/reset/` | Request password reset |
| POST | `/auth/password/reset/confirm/` | Confirm password reset |
| POST | `/auth/password/change/` | Change password |

### 6.2 User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List users |
| POST | `/users/` | Create user |
| GET | `/users/{id}/` | Get user details |
| PATCH | `/users/{id}/` | Update user |
| DELETE | `/users/{id}/` | Deactivate user |
| GET | `/users/me/` | Get current user profile |
| PATCH | `/users/me/` | Update own profile |
| GET | `/users/{id}/roles/` | List user roles |
| POST | `/users/{id}/roles/` | Assign role |
| DELETE | `/users/{id}/roles/{role_id}/` | Revoke role |

### 6.3 Patients

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients/` | List patients |
| POST | `/patients/` | Register new patient |
| GET | `/patients/{id}/` | Get patient details |
| PATCH | `/patients/{id}/` | Update patient |
| GET | `/patients/search/` | Search patients |
| GET | `/patients/{id}/encounters/` | List patient encounters |
| GET | `/patients/{id}/allergies/` | List patient allergies |
| POST | `/patients/{id}/allergies/` | Add allergy |
| GET | `/patients/{id}/medical-history/` | Get medical history |
| POST | `/patients/{id}/medical-history/` | Add medical history item |
| GET | `/patients/{id}/summary/` | Get patient summary |

### 6.4 Encounters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/encounters/` | List encounters |
| POST | `/encounters/` | Create encounter |
| GET | `/encounters/{id}/` | Get encounter details |
| PATCH | `/encounters/{id}/` | Update encounter |
| POST | `/encounters/{id}/close/` | Close encounter |
| GET | `/encounters/{id}/observations/` | List observations |
| POST | `/encounters/{id}/observations/` | Add observation |
| GET | `/encounters/{id}/notes/` | List clinical notes |
| POST | `/encounters/{id}/notes/` | Add clinical note |
| PATCH | `/encounters/{id}/notes/{note_id}/` | Update clinical note |
| POST | `/encounters/{id}/notes/{note_id}/finalize/` | Finalize note |

### 6.5 Medical Knowledge

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/medical-knowledge/diseases/` | List diseases |
| GET | `/medical-knowledge/diseases/{id}/` | Get disease details |
| GET | `/medical-knowledge/diseases/search/` | Search diseases |
| GET | `/medical-knowledge/symptoms/` | List symptoms |
| GET | `/medical-knowledge/symptoms/{id}/` | Get symptom details |
| GET | `/medical-knowledge/symptoms/search/` | Search symptoms |
| GET | `/medical-knowledge/medicines/` | List medicines |
| GET | `/medical-knowledge/medicines/{id}/` | Get medicine details |
| GET | `/medical-knowledge/medicines/search/` | Search medicines |
| GET | `/medical-knowledge/medicines/{id}/interactions/` | Get drug interactions |

### 6.6 Clinical Decision Support

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/decision-support/differential-diagnosis/` | Request differential diagnosis |
| GET | `/decision-support/requests/{id}/` | Get CDSS request results |
| POST | `/decision-support/candidates/{id}/feedback/` | Submit clinician feedback |
| POST | `/decision-support/safety-check/` | Perform safety check |

### 6.7 Prescriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prescriptions/` | List prescriptions |
| POST | `/prescriptions/` | Create prescription |
| GET | `/prescriptions/{id}/` | Get prescription details |
| PATCH | `/prescriptions/{id}/` | Update prescription |
| POST | `/prescriptions/{id}/approve/` | Approve prescription |
| POST | `/prescriptions/{id}/cancel/` | Cancel prescription |
| POST | `/prescriptions/{id}/safety-check/` | Run safety checks |
| GET | `/prescriptions/{id}/items/` | List prescription items |
| POST | `/prescriptions/{id}/items/` | Add prescription item |

### 6.8 Laboratory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/laboratory/tests/` | List available tests |
| GET | `/laboratory/orders/` | List lab orders |
| POST | `/laboratory/orders/` | Create lab order |
| GET | `/laboratory/orders/{id}/` | Get order details |
| PATCH | `/laboratory/orders/{id}/` | Update order status |
| POST | `/laboratory/orders/{id}/collect-specimen/` | Record specimen collection |
| GET | `/laboratory/orders/{id}/results/` | Get results |
| POST | `/laboratory/orders/{id}/results/` | Enter results |
| POST | `/laboratory/results/{id}/verify/` | Verify results |

### 6.9 Pharmacy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pharmacy/inventory/` | List inventory items |
| GET | `/pharmacy/inventory/{id}/` | Get inventory details |
| GET | `/pharmacy/inventory/{id}/batches/` | List stock batches |
| POST | `/pharmacy/inventory/{id}/receive/` | Receive stock |
| POST | `/pharmacy/inventory/{id}/adjust/` | Adjust stock |
| GET | `/pharmacy/dispensing/` | List dispensing records |
| POST | `/pharmacy/dispensing/` | Record dispensing |
| GET | `/pharmacy/expiring-soon/` | List expiring stock |
| GET | `/pharmacy/low-stock/` | List low stock items |

### 6.10 Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/appointments/` | List appointments |
| POST | `/appointments/` | Create appointment |
| GET | `/appointments/{id}/` | Get appointment details |
| PATCH | `/appointments/{id}/` | Update appointment |
| POST | `/appointments/{id}/cancel/` | Cancel appointment |
| POST | `/appointments/{id}/check-in/` | Check in patient |
| GET | `/appointments/availability/` | Check availability |

### 6.11 Admissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admissions/` | List admissions |
| POST | `/admissions/` | Create admission |
| GET | `/admissions/{id}/` | Get admission details |
| POST | `/admissions/{id}/transfer/` | Transfer patient |
| POST | `/admissions/{id}/discharge/` | Discharge patient |
| GET | `/admissions/beds/` | List beds |
| GET | `/admissions/beds/available/` | List available beds |

### 6.12 ML Governance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ml-governance/datasets/` | List datasets |
| POST | `/ml-governance/datasets/` | Create dataset |
| GET | `/ml-governance/datasets/{id}/` | Get dataset details |
| GET | `/ml-governance/models/` | List models |
| POST | `/ml-governance/models/` | Register model |
| GET | `/ml-governance/models/{id}/` | Get model details |
| GET | `/ml-governance/models/{id}/evaluations/` | Get evaluations |
| POST | `/ml-governance/models/{id}/approve/` | Approve model |
| POST | `/ml-governance/models/{id}/deploy/` | Deploy model |
| POST | `/ml-governance/models/{id}/rollback/` | Rollback model |
| GET | `/ml-governance/models/{id}/monitoring/` | Get monitoring data |

### 6.13 Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/` | List available reports |
| POST | `/reports/generate/` | Generate report |
| GET | `/reports/{id}/` | Get report results |
| GET | `/reports/{id}/download/` | Download report |

### 6.14 Audit

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit/logs/` | List audit logs |
| GET | `/audit/logs/{id}/` | Get audit log details |
| GET | `/audit/access-logs/` | List access logs |

## 7. Request/Response Examples

### 7.1 Create Patient

**Request:**
```http
POST /api/v1/patients/
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Abebe",
  "last_name": "Kebede",
  "date_of_birth": "1990-05-20",
  "sex": "male",
  "phone": "+251911234567",
  "email": "abebe.kebede@example.com",
  "address_line1": "123 Main Street",
  "city": "Addis Ababa",
  "region": "Addis Ababa",
  "country": "ET",
  "national_id": "ID1234567",
  "blood_group": "O+",
  "consent_for_treatment": true
}
```

**Response:**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_number": "P-2026-00123",
    "first_name": "Abebe",
    "last_name": "Kebede",
    "date_of_birth": "1990-05-20",
    "age": 36,
    "sex": "male",
    "phone": "+251911234567",
    "email": "abebe.kebede@example.com",
    "address_line1": "123 Main Street",
    "city": "Addis Ababa",
    "region": "Addis Ababa",
    "country": "ET",
    "national_id": "ID1234567",
    "blood_group": "O+",
    "consent_for_treatment": true,
    "registered_facility": {
      "id": "uuid",
      "name": "General Hospital"
    },
    "registration_date": "2026-10-19T10:30:00Z",
    "created_at": "2026-10-19T10:30:00Z",
    "updated_at": "2026-10-19T10:30:00Z"
  },
  "meta": {
    "timestamp": "2026-10-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 7.2 Search Patients

**Request:**
```http
GET /api/v1/patients/search/?q=Abebe&date_of_birth=1990-05-20
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "patient_number": "P-2026-00123",
      "first_name": "Abebe",
      "last_name": "Kebede",
      "date_of_birth": "1990-05-20",
      "age": 36,
      "sex": "male",
      "phone": "+251911234567",
      "match_score": 0.95
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1
  },
  "meta": {
    "query": "Abebe",
    "filters": {
      "date_of_birth": "1990-05-20"
    },
    "timestamp": "2026-10-19T10:30:00Z"
  }
}
```

### 7.3 Request Differential Diagnosis

**Request:**
```http
POST /api/v1/decision-support/differential-diagnosis/
Authorization: Bearer {token}
Content-Type: application/json

{
  "encounter_id": "uuid",
  "symptoms": [
    {
      "symptom_id": "uuid",
      "name": "Fever",
      "severity": "moderate",
      "duration_days": 3,
      "onset": "gradual"
    },
    {
      "symptom_id": "uuid",
      "name": "Cough",
      "severity": "mild",
      "duration_days": 2,
      "characteristics": ["dry"]
    }
  ],
  "vital_signs": {
    "temperature": 38.5,
    "temperature_unit": "celsius",
    "pulse_rate": 92,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "respiratory_rate": 18,
    "oxygen_saturation": 97
  },
  "relevant_history": {
    "chronic_conditions": [],
    "recent_travel": false,
    "known_exposures": []
  }
}
```

**Response:**
```json
{
  "data": {
    "request_id": "uuid",
    "status": "completed",
    "processed_at": "2026-10-19T10:30:05Z",
    "engine_version": "1.0.0",
    "model_version": null,
    "candidates": [
      {
        "id": "uuid",
        "rank": 1,
        "disease": {
          "id": "uuid",
          "name": "Upper Respiratory Tract Infection",
          "icd10_code": "J06.9",
          "category": "Respiratory Infections"
        },
        "confidence_level": "high",
        "supporting_findings": [
          {
            "finding": "Fever",
            "relevance": "very_common",
            "notes": "Fever is a common presenting symptom"
          },
          {
            "finding": "Cough",
            "relevance": "very_common"
          },
          {
            "finding": "Normal oxygen saturation",
            "relevance": "expected"
          }
        ],
        "contradicting_findings": [],
        "missing_information": [
          "Nasal congestion",
          "Sore throat",
          "Duration of illness"
        ],
        "red_flags": [],
        "suggested_investigations": [
          {
            "investigation": "Complete Blood Count",
            "indication": "To assess infection severity",
            "priority": "routine",
            "source": "Clinical guideline v2.1"
          }
        ],
        "diagnostic_criteria": {
          "criteria_met": ["Acute onset", "Fever", "Respiratory symptoms"],
          "criteria_not_met": [],
          "criteria_unknown": ["Physical examination findings"]
        },
        "guideline_reference": {
          "source": "WHO IMCI Guidelines",
          "version": "2023",
          "url": "https://example.com/guideline"
        }
      }
    ],
    "emergency_alerts": [],
    "limitations": [
      "Based on limited clinical information",
      "Physical examination findings not available",
      "No machine learning model deployed - using rule-based engine only"
    ]
  },
  "meta": {
    "timestamp": "2026-10-19T10:30:05Z",
    "request_id": "uuid",
    "processing_time_ms": 523
  }
}
```

### 7.4 Create Prescription

**Request:**
```http
POST /api/v1/prescriptions/
Authorization: Bearer {token}
Content-Type: application/json

{
  "encounter_id": "uuid",
  "items": [
    {
      "medicine_id": "uuid",
      "dose": "500",
      "dose_unit": "mg",
      "route": "oral",
      "frequency": "Every 8 hours",
      "duration_value": 7,
      "duration_unit": "days",
      "quantity": 21,
      "quantity_unit": "tablets",
      "indication": "Upper respiratory tract infection",
      "instructions": "Take with food",
      "start_date": "2026-10-19"
    }
  ],
  "run_safety_checks": true
}
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "prescription_number": "RX-2026-00456",
    "status": "draft",
    "encounter_id": "uuid",
    "patient": {
      "id": "uuid",
      "patient_number": "P-2026-00123",
      "full_name": "Abebe Kebede"
    },
    "prescriber": {
      "id": "uuid",
      "full_name": "Dr. John Smith"
    },
    "prescribed_datetime": "2026-10-19T10:30:00Z",
    "items": [
      {
        "id": "uuid",
        "medicine": {
          "id": "uuid",
          "generic_name": "Amoxicillin",
          "dosage_form": "tablet",
          "strength": "500 mg"
        },
        "dose": "500",
        "dose_unit": "mg",
        "route": "oral",
        "frequency": "Every 8 hours",
        "duration": "7 days",
        "quantity": 21,
        "quantity_unit": "tablets",
        "indication": "Upper respiratory tract infection",
        "instructions": "Take with food",
        "start_date": "2026-10-19",
        "end_date": "2026-10-26",
        "safety_checks_passed": true,
        "safety_warnings": []
      }
    ],
    "safety_check_summary": {
      "checks_performed": [
        "allergy_check",
        "interaction_check",
        "contraindication_check",
        "dose_range_check"
      ],
      "warnings": [],
      "errors": [],
      "passed": true
    },
    "valid_until": "2026-11-19",
    "created_at": "2026-10-19T10:30:00Z"
  },
  "meta": {
    "timestamp": "2026-10-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

## 8. Pagination

All list endpoints support pagination using query parameters:

```http
GET /api/v1/patients/?page=2&page_size=50
```

**Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 20, max: 100) - Items per page

## 9. Filtering and Sorting

### 9.1 Filtering

```http
GET /api/v1/encounters/?status=in_progress&department=emergency
GET /api/v1/prescriptions/?patient_id={uuid}&status=approved
GET /api/v1/laboratory/orders/?ordered_after=2026-10-01&priority=stat
```

### 9.2 Sorting

```http
GET /api/v1/patients/?ordering=-created_at
GET /api/v1/encounters/?ordering=admission_datetime
GET /api/v1/prescriptions/?ordering=-prescribed_datetime,status
```

Use `-` prefix for descending order.

## 10. Rate Limiting

Rate limits are enforced to prevent abuse:

| User Type | Rate Limit |
|-----------|------------|
| Authenticated | 1000 requests/hour |
| Unauthenticated | 100 requests/hour |
| ML Inference | 100 requests/minute |

**Response Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1634639400
```

**Rate Limit Exceeded:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "retry_after": 3600
    }
  }
}
```

## 11. API Versioning

The API version is included in the URL path:

```
/api/v1/patients/       <- Current version
/api/v2/patients/       <- Future version
```

**Deprecation Policy:**
- New versions announced 6 months in advance
- Old versions supported for 12 months after new version release
- Deprecation warnings included in response headers

**Deprecation Header:**
```
Deprecation: true
Sunset: Sat, 31 Dec 2027 23:59:59 GMT
Link: </api/v2/patients/>; rel="successor-version"
```

## 12. OpenAPI Documentation

Interactive API documentation available at:

```
Development: http://localhost:8000/api/docs/
Production: https://api.intelligent-medical.example.com/api/docs/
```

**Download OpenAPI Schema:**
```http
GET /api/schema/
```

## 13. Webhooks (Future Feature)

Future support for webhooks to notify external systems:

```json
{
  "event": "prescription.approved",
  "timestamp": "2026-10-19T10:30:00Z",
  "data": {
    "prescription_id": "uuid",
    "patient_id": "uuid"
  }
}
```

## 14. FHIR Compatibility (Future Feature)

Future support for HL7 FHIR R4 resources:

```http
GET /fhir/Patient/{id}
GET /fhir/Observation/{id}
GET /fhir/MedicationRequest/{id}
```

## 15. Best Practices for API Consumers

1. **Always handle errors gracefully**
2. **Implement exponential backoff for retries**
3. **Cache responses where appropriate**
4. **Use ETags for conditional requests**
5. **Respect rate limits**
6. **Keep tokens secure**
7. **Validate TLS certificates**
8. **Log request_id for troubleshooting**

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Status**: APPROVED FOR DEVELOPMENT
