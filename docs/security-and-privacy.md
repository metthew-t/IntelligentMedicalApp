# Security and Privacy Specification

## 1. Overview

This document outlines the security and privacy measures implemented in the Intelligent Medical and Hospital Management System. Given the sensitive nature of healthcare data, security is a top priority and is implemented at multiple layers.

## 2. Security Principles

1. **Defense in Depth** - Multiple layers of security controls
2. **Least Privilege** - Users have minimum necessary permissions
3. **Secure by Default** - Security features enabled out of the box
4. **Zero Trust** - Verify every request, never assume trust
5. **Privacy by Design** - Privacy considered from the start
6. **Data Minimization** - Collect only necessary information
7. **Audit Everything** - Log all sensitive operations
8. **Fail Securely** - Failures deny access rather than grant it

## 3. Authentication Security

### 3.1 Password Policy

**Requirements:**
- Minimum 12 characters
- Must include: uppercase, lowercase, number, special character
- Cannot contain username or common words
- Cannot reuse last 5 passwords
- Expires every 90 days for privileged accounts
- Maximum 5 failed attempts before account lockout
- Lockout duration: 30 minutes

**Implementation:**
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.accounts.validators.PasswordComplexityValidator',
    },
    {
        'NAME': 'apps.accounts.validators.PasswordHistoryValidator',
    },
]
```

### 3.2 Multi-Factor Authentication (MFA)

**Implementation:**
- Time-based One-Time Password (TOTP)
- Required for System Administrators
- Required for users with patient data access
- Backup codes provided during setup

**MFA Enforcement:**
```python
REQUIRED_MFA_ROLES = [
    'system_admin',
    'hospital_admin',
    'doctor',
    'pharmacist'
]
```

### 3.3 JWT Token Security

**Access Token:**
- Lifetime: 15 minutes
- Signed with RS256 (asymmetric)
- Cannot be revoked (short lifetime mitigates risk)

**Refresh Token:**
- Lifetime: 7 days
- Stored in database (can be revoked)
- Rotated on each refresh
- Bound to user agent and IP (optional)
- Blacklisted on logout

**Token Storage:**
- Access tokens: Memory only (never localStorage)
- Refresh tokens: HTTP-only, secure cookies

### 3.4 Session Management

**Security Controls:**
- Session timeout: 30 minutes of inactivity
- Absolute timeout: 8 hours
- Concurrent session limit: 3 per user
- Session invalidated on password change
- Session bound to IP address (optional)

## 4. Authorization Security

### 4.1 Role-Based Access Control (RBAC)

**Permission Model:**
```
User → UserRole → Role → RolePermission → Permission
         ↓
      Facility (scope)
```

**Permission Format:**
```
<resource>:<action>:<scope>

Examples:
- patient:read:own_facility
- prescription:approve:own
- medical_knowledge:edit:all
- audit:read:own_facility
```

### 4.2 Object-Level Permissions

Every data access checks:
1. **Role permissions** - Does user's role allow this action?
2. **Facility scope** - Is the resource in user's facility?
3. **Object ownership** - For personal data, is user the owner?
4. **Special rules** - Custom business logic (e.g., assigned doctor)

**Implementation Example:**
```python
def has_patient_access(user, patient):
    # Check role permissions
    if not user.has_permission('patient:read'):
        return False
    
    # Check facility scope
    if patient.registered_facility_id not in user.facilities:
        return False
    
    # Check specific access rules
    if user.role == 'doctor':
        # Doctor can access if they're attending any encounter
        return Encounter.objects.filter(
            patient=patient,
            attending_physician=user
        ).exists()
    
    return True
```

### 4.3 Permission Matrix

| Role | Patients | Prescriptions | Medical Knowledge | ML Models | Audit Logs |
|------|----------|---------------|-------------------|-----------|------------|
| System Admin | All facilities | View only | Manage | Deploy | All |
| Hospital Admin | Own facility | View only | View | View | Own facility |
| Doctor | Assigned patients | Create & approve | View | View | Own actions |
| Nurse | Assigned patients | View | View | None | Own actions |
| Pharmacist | Prescription patients | Review & dispense | View medicines | None | Own actions |
| Lab Staff | Order patients | None | View tests | None | Own actions |
| Medical Editor | None | None | Edit | None | None |
| Clinical Reviewer | None | None | Approve content | None | None |
| ML Reviewer | None | None | None | Approve & deploy | ML operations |
| Auditor | View (de-identified) | View | View | View | All |

## 5. Network Security

### 5.1 HTTPS/TLS

**Requirements:**
- TLS 1.3 or TLS 1.2 minimum
- Strong cipher suites only
- HSTS enabled with long max-age
- Certificate pinning in mobile apps

**Configuration:**
```python
# Django settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 5.2 CORS Policy

**Configuration:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://app.intelligent-medical.example.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]

CORS_ALLOWED_HEADERS = [
    'authorization',
    'content-type',
    'x-csrftoken',
    'x-requested-with',
]
```

### 5.3 Firewall Rules

**Inbound:**
- 443 (HTTPS) - Public
- 22 (SSH) - Admin IPs only
- 5432 (PostgreSQL) - Application servers only
- 6379 (Redis) - Application servers only

**Outbound:**
- Allow: 443 (HTTPS for external APIs)
- Allow: 25/587 (SMTP for emails)
- Block: All other outbound

## 6. Application Security

### 6.1 Input Validation

**All inputs validated:**
- Type checking
- Length limits
- Format validation (email, phone, dates)
- Whitelist allowed characters
- Sanitize HTML inputs
- Validate file uploads

**Django REST Framework Serializers:**
```python
class PatientSerializer(serializers.ModelSerializer):
    phone = serializers.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={'invalid': 'Invalid phone number format'}
    )
    email = serializers.EmailField(required=False)
    date_of_birth = serializers.DateField()
    
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future"
            )
        if value < date.today() - timedelta(days=365*150):
            raise serializers.ValidationError(
                "Invalid date of birth"
            )
        return value
```

### 6.2 Output Encoding

**Automatic encoding:**
- HTML entities escaped in templates
- JSON properly encoded
- SQL injection prevented by ORM
- Command injection prevented by avoiding shell=True

### 6.3 CSRF Protection

**Django CSRF middleware enabled:**
```python
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
```

**API CSRF:**
- Session-based endpoints require CSRF token
- JWT endpoints exempt (token itself provides CSRF protection)

### 6.4 SQL Injection Prevention

**Use Django ORM:**
```python
# SAFE - Parameterized
Patient.objects.filter(last_name=user_input)

# UNSAFE - Never do this
Patient.objects.raw(f"SELECT * FROM patients WHERE last_name = '{user_input}'")
```

**Raw queries (when necessary):**
```python
# Use parameterized queries
cursor.execute(
    "SELECT * FROM patients WHERE last_name = %s",
    [user_input]
)
```

### 6.5 XSS Prevention

**Content Security Policy:**
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Remove unsafe-inline in production
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
```

**Output encoding:**
- Django templates auto-escape by default
- Use `|safe` filter sparingly and only with trusted content
- Sanitize user-generated HTML with bleach library

### 6.6 File Upload Security

**Restrictions:**
- Maximum file size: 10 MB
- Allowed types: PDF, DOCX, PNG, JPG only
- Filename sanitization
- Virus scanning
- Store outside web root
- Serve through application (not direct access)
- Generate random filenames

**Implementation:**
```python
ALLOWED_UPLOAD_TYPES = {
    'application/pdf': '.pdf',
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
}

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file):
    # Check size
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError("File too large")
    
    # Check type
    file_type = magic.from_buffer(file.read(1024), mime=True)
    if file_type not in ALLOWED_UPLOAD_TYPES:
        raise ValidationError("File type not allowed")
    
    # Scan for viruses
    if not virus_scan(file):
        raise ValidationError("File failed security scan")
    
    return True
```

## 7. Data Security

### 7.1 Encryption at Rest

**Database:**
- PostgreSQL Transparent Data Encryption (TDE)
- Encrypted backups
- Encrypted pg_dump files

**File Storage:**
- Server-side encryption (SSE)
- Encrypted file system (LUKS)
- Encrypted backup storage

**Secrets:**
- Environment variables
- AWS Secrets Manager / HashiCorp Vault
- Never in code or version control

### 7.2 Encryption in Transit

**All communications encrypted:**
- API: HTTPS only
- Database: SSL connections
- Redis: TLS enabled
- Email: TLS/STARTTLS
- Backups: Encrypted transfer

### 7.3 Data Masking

**Sensitive data masked in logs:**
```python
SENSITIVE_FIELDS = [
    'password',
    'token',
    'secret',
    'national_id',
    'ssn',
    'credit_card'
]

def mask_sensitive_data(data):
    if isinstance(data, dict):
        return {
            k: '***REDACTED***' if any(s in k.lower() for s in SENSITIVE_FIELDS) else mask_sensitive_data(v)
            for k, v in data.items()
        }
    return data
```

### 7.4 Data Backup

**Backup Schedule:**
- Full backup: Daily at 2 AM
- Incremental backup: Every 6 hours
- Transaction logs: Continuous archiving

**Backup Security:**
- Encrypted with AES-256
- Stored in separate geographic location
- Access restricted to backup administrators
- Retention: 30 days online, 7 years archived

**Backup Verification:**
- Monthly restore test
- Integrity checks on every backup
- Documented recovery procedures

## 8. Privacy Controls

### 8.1 Data Minimization

**Principles:**
- Collect only necessary information
- Delete or anonymize when no longer needed
- Purpose limitation - use data only for stated purpose

**Implementation:**
- Required fields marked explicitly
- Optional fields clearly indicated
- Data retention policies enforced

### 8.2 Consent Management

**Consent Types:**
- Treatment consent (required)
- Data processing consent (required in EU)
- Research consent (optional)
- Marketing communications (optional)

**Consent Tracking:**
```python
class Consent(models.Model):
    patient = models.ForeignKey(Patient)
    consent_type = models.CharField(choices=CONSENT_TYPES)
    given = models.BooleanField()
    given_datetime = models.DateTimeField()
    withdrawn_datetime = models.DateTimeField(null=True)
    version = models.CharField()  # Policy version
    method = models.CharField()  # verbal, written, electronic
```

### 8.3 Right to Access

**Patient rights (GDPR/HIPAA):**
- Access their own data
- Receive copy of data
- Correct inaccurate data
- Request deletion (where legally permitted)
- Data portability

**Implementation:**
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_data_export(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Verify patient or authorized user
    if not (request.user.is_patient_owner(patient) or 
            request.user.has_permission('patient:export')):
        return Response(status=403)
    
    # Generate comprehensive export
    data = {
        'demographics': PatientSerializer(patient).data,
        'encounters': EncounterSerializer(patient.encounters.all(), many=True).data,
        'prescriptions': PrescriptionSerializer(patient.prescriptions.all(), many=True).data,
        'lab_results': LabResultSerializer(patient.lab_results.all(), many=True).data,
    }
    
    return Response(data)
```

### 8.4 De-identification for Research

**De-identification Process:**
1. Remove direct identifiers (name, ID, address)
2. Generalize quasi-identifiers (age ranges, geographic regions)
3. Remove free-text notes (or redact PHI)
4. Apply k-anonymity where possible

**Implementation:**
```python
def de_identify_for_research(queryset):
    return queryset.annotate(
        age_group=Case(
            When(date_of_birth__gte=date.today() - timedelta(days=365*18), then=Value('0-18')),
            When(date_of_birth__gte=date.today() - timedelta(days=365*40), then=Value('19-40')),
            When(date_of_birth__gte=date.today() - timedelta(days=365*60), then=Value('41-60')),
            default=Value('61+'),
            output_field=CharField()
        ),
        region_broad=F('region')  # Keep region, remove city
    ).values(
        'age_group',
        'sex',
        'region_broad',
        'diagnosis',
        'treatment_outcome'
    )
```

### 8.5 Data Retention

**Retention Periods:**
| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Active patient records | Indefinite | Medical necessity |
| Inactive patients (no visit > 10 years) | Indefinite, archived | Legal requirement |
| Audit logs | 7 years | Compliance |
| Session logs | 90 days | Security analysis |
| Temporary files | 24 hours | No ongoing need |
| Deleted patient data (GDPR request) | 30 days in recycle bin | Accidental deletion recovery |

**Automated Cleanup:**
```python
# Celery task
@shared_task
def cleanup_old_data():
    # Delete expired sessions
    Session.objects.filter(
        expire_date__lt=timezone.now() - timedelta(days=90)
    ).delete()
    
    # Archive old encounters
    old_encounters = Encounter.objects.filter(
        discharge_datetime__lt=timezone.now() - timedelta(days=365*10),
        archived=False
    )
    for encounter in old_encounters:
        archive_encounter(encounter)
```

## 9. Audit and Monitoring

### 9.1 Audit Logging

**Events Logged:**
- Authentication (login, logout, failed attempts)
- Authorization failures
- Patient record access
- Patient record modifications
- Prescription creation/approval
- Medication dispensing
- Lab result entry/verification
- Configuration changes
- User management actions
- Data exports
- ML model deployments

**Audit Log Format:**
```python
{
    "id": "uuid",
    "timestamp": "2026-10-19T10:30:00.123456Z",
    "user_id": "uuid",
    "username": "doctor@example.com",
    "ip_address": "192.168.1.100",
    "session_id": "session-uuid",
    "action": "patient:read",
    "resource_type": "Patient",
    "resource_id": "patient-uuid",
    "outcome": "success",
    "facility_id": "facility-uuid",
    "request_method": "GET",
    "request_path": "/api/v1/patients/uuid/",
    "user_agent": "Mozilla/5.0...",
    "changes_made": null
}
```

### 9.2 Security Monitoring

**Alerts Configured:**
- Multiple failed login attempts
- Unusual data access patterns
- After-hours access to sensitive data
- Bulk data exports
- Permission escalation attempts
- Configuration changes
- Failed authorization attempts
- Database connection errors
- Slow query performance

**SIEM Integration:**
- Forward logs to Security Information and Event Management system
- Real-time alerting
- Correlation with other security events

### 9.3 Intrusion Detection

**Monitored Indicators:**
- Unusual API usage patterns
- Geographic anomalies
- Time-based anomalies
- Volume-based anomalies
- Privilege escalation attempts

## 10. Incident Response

### 10.1 Security Incident Categories

| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | Data breach, ransomware, system compromise | Immediate |
| High | Attempted breach, vulnerability exploitation | 1 hour |
| Medium | Suspicious activity, policy violation | 4 hours |
| Low | Failed login, minor policy breach | 24 hours |

### 10.2 Incident Response Plan

**Phase 1: Detection and Analysis**
1. Detect incident through monitoring/alerts
2. Assess severity and scope
3. Assemble response team
4. Document initial findings

**Phase 2: Containment**
1. Short-term containment (isolate affected systems)
2. Evidence preservation
3. Long-term containment (patch vulnerabilities)

**Phase 3: Eradication**
1. Remove malware/unauthorized access
2. Patch vulnerabilities
3. Strengthen defenses

**Phase 4: Recovery**
1. Restore systems from clean backups
2. Monitor for re-infection
3. Gradual return to normal operations

**Phase 5: Post-Incident**
1. Document lessons learned
2. Update policies and procedures
3. Provide training if needed
4. Notify affected parties if required

### 10.3 Breach Notification

**Legal Requirements:**
- HIPAA: 60 days notification to affected individuals
- GDPR: 72 hours notification to supervisory authority

**Notification Process:**
1. Confirm breach occurred
2. Assess scope and impact
3. Notify legal and compliance teams
4. Prepare notification content
5. Notify affected parties
6. Notify regulators if required
7. Document entire process

## 11. Third-Party Security

### 11.1 Vendor Assessment

**Before Integration:**
- Security questionnaire
- Compliance certifications review
- Data processing agreement
- Right to audit clause
- Incident notification requirements

### 11.2 API Integrations

**Security Requirements:**
- TLS 1.2+ required
- API key rotation
- Rate limiting
- IP whitelisting where possible
- Audit logging of all API calls

## 12. Compliance

### 12.1 HIPAA Compliance (US)

**Administrative Safeguards:**
- ✅ Security management process
- ✅ Assigned security responsibility
- ✅ Workforce security
- ✅ Information access management
- ✅ Security awareness and training
- ✅ Security incident procedures
- ✅ Contingency plan
- ✅ Evaluation

**Physical Safeguards:**
- ✅ Facility access controls
- ✅ Workstation use
- ✅ Workstation security
- ✅ Device and media controls

**Technical Safeguards:**
- ✅ Access control
- ✅ Audit controls
- ✅ Integrity
- ✅ Person or entity authentication
- ✅ Transmission security

### 12.2 GDPR Compliance (EU)

**Principles:**
- ✅ Lawfulness, fairness, transparency
- ✅ Purpose limitation
- ✅ Data minimization
- ✅ Accuracy
- ✅ Storage limitation
- ✅ Integrity and confidentiality
- ✅ Accountability

**Rights:**
- ✅ Right to access
- ✅ Right to rectification
- ✅ Right to erasure
- ✅ Right to restrict processing
- ✅ Right to data portability
- ✅ Right to object
- ✅ Rights related to automated decision-making

### 12.3 Local Regulations (Ethiopia)

- Compliance with Ethiopian data protection laws
- Healthcare facility licensing requirements
- Medical record retention requirements
- Cross-border data transfer restrictions

## 13. Security Testing

### 13.1 Vulnerability Scanning

**Automated Scanning:**
- Weekly vulnerability scans
- Dependency vulnerability checking (Dependabot, Safety)
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)

**Tools:**
- OWASP ZAP
- Bandit (Python security linter)
- Safety (Python dependency checker)
- npm audit (JavaScript dependencies)

### 13.2 Penetration Testing

**Frequency:**
- Annual external penetration test
- Quarterly internal security assessment
- After major changes

**Scope:**
- Web application
- API
- Mobile applications
- Network infrastructure
- Social engineering

### 13.3 Security Code Review

**Process:**
- Automated SAST in CI/CD pipeline
- Manual review of security-critical code
- Peer review required for authentication/authorization changes
- Security champion review for high-risk changes

## 14. Security Training

### 14.1 Developer Training

**Topics:**
- Secure coding practices
- OWASP Top 10
- Common vulnerabilities
- Security tools usage
- Incident response procedures

**Frequency:** Annually, plus ad-hoc for new threats

### 14.2 User Security Awareness

**Topics:**
- Password security
- Phishing awareness
- Device security
- Data handling
- Incident reporting

**Frequency:** Quarterly

## 15. Security Checklist

### 15.1 Pre-Deployment

- [ ] All secrets in environment variables
- [ ] HTTPS enforced
- [ ] HSTS enabled
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] Database encrypted
- [ ] Backups encrypted
- [ ] MFA configured for admins
- [ ] Vulnerability scan passed
- [ ] Penetration test passed
- [ ] Security code review completed
- [ ] Incident response plan documented

### 15.2 Post-Deployment

- [ ] Monitor security alerts
- [ ] Review audit logs weekly
- [ ] Update dependencies monthly
- [ ] Review access permissions quarterly
- [ ] Test backups monthly
- [ ] Review incident response plan annually
- [ ] Conduct penetration test annually
- [ ] Review and update security policies annually

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Status**: APPROVED FOR DEVELOPMENT
**Review Date**: 2027-04-19
