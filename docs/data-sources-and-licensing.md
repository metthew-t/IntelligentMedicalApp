# Data Sources and Licensing

## 1. Overview

This document outlines potential data sources for medical knowledge, their licensing considerations, and integration strategies for the Intelligent Medical and Hospital Management System.

## 2. Data Source Categories

### 2.1 Disease Classifications

#### WHO ICD-11
- **Source**: World Health Organization
- **Content**: International Classification of Diseases, 11th Revision
- **URL**: https://icd.who.int/
- **API**: Yes - ICD API available
- **License**: WHO terms of use apply
- **Cost**: Free for non-commercial use (verify for commercial deployment)
- **Data Format**: JSON, XML via API
- **Coverage**: Comprehensive disease classification
- **Updates**: Regular
- **Integration Complexity**: Medium
- **Status**: Recommended primary source

**Integration Notes:**
```python
# Example ICD-11 API integration
import requests

class ICD11Client:
    def __init__(self, client_id, client_secret):
        self.base_url = "https://id.who.int/icd/release/11/2024-01"
        self.token = self._get_token(client_id, client_secret)
    
    def search_disease(self, query, language='en'):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Accept-Language': language,
            'API-Version': 'v2'
        }
        
        response = requests.get(
            f"{self.base_url}/mms/search",
            params={'q': query},
            headers=headers
        )
        
        return response.json()
```

#### ICD-10
- **Source**: WHO
- **Content**: Previous version, still widely used
- **License**: WHO terms
- **Cost**: Free
- **Status**: Legacy support

### 2.2 Medicine Databases

#### RxNorm (US)
- **Source**: U.S. National Library of Medicine
- **Content**: Normalized names for clinical drugs
- **URL**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **License**: Free (UMLS license required)
- **Cost**: Free
- **Data Format**: RRF files, REST API
- **Coverage**: US medications
- **Updates**: Monthly
- **Status**: Recommended for US deployment

#### DrugBank
- **Source**: DrugBank (Canada)
- **Content**: Comprehensive drug data
- **URL**: https://www.drugbank.com/
- **License**: Academic free, Commercial requires license
- **Cost**: Free for academic, $$$ for commercial
- **Data Format**: XML, JSON, CSV
- **Coverage**: 14,000+ drugs, interactions, targets
- **Updates**: Monthly
- **Status**: Recommended for comprehensive data

#### WHO Essential Medicines List
- **Source**: World Health Organization
- **Content**: Model list of essential medicines
- **URL**: https://www.who.int/medicines/publications/essentialmedicines/
- **License**: WHO terms
- **Cost**: Free
- **Data Format**: PDF (manual entry required)
- **Coverage**: ~500 essential medicines
- **Updates**: Biennial
- **Status**: Good for basic formulary

#### Ethiopian Food and Drug Authority (EFDA) Registry
- **Source**: Ethiopian FDA
- **Content**: Registered medicines in Ethiopia
- **License**: Public data (verify terms)
- **Cost**: Free (likely)
- **Data Format**: TBD (may require scraping or manual entry)
- **Coverage**: Ethiopia-specific
- **Status**: **Critical for Ethiopian deployment**

### 2.3 Drug Interactions

#### Drugs.com Interaction Checker Database
- **Source**: Drugs.com
- **License**: Proprietary (licensing required)
- **Cost**: $$$
- **Coverage**: Comprehensive
- **Status**: Investigate licensing

#### DrugBank Interactions
- **Included in**: DrugBank subscription
- **Coverage**: 1.3 million+ interactions
- **Status**: Recommended

#### FDA Adverse Event Reporting System (FAERS)
- **Source**: US FDA
- **License**: Public domain
- **Cost**: Free
- **Data Format**: ASCII, XML
- **Use**: Post-market surveillance, interaction signals
- **Status**: Supplementary source

### 2.4 Clinical Guidelines

#### WHO Guidelines
- **Source**: World Health Organization
- **Content**: Evidence-based guidelines for various conditions
- **URL**: https://www.who.int/publications/who-guidelines
- **License**: Open access (verify specific guidelines)
- **Cost**: Free
- **Status**: Recommended primary source

#### UpToDate
- **Source**: Wolters Kluwer
- **Content**: Evidence-based clinical decision support
- **License**: Subscription required
- **Cost**: $$$$
- **API**: Limited
- **Status**: Premium option (expensive)

#### PubMed/MEDLINE
- **Source**: U.S. National Library of Medicine
- **Content**: Biomedical literature
- **URL**: https://pubmed.ncbi.nlm.nih.gov/
- **API**: Yes - E-utilities API
- **License**: Free
- **Cost**: Free
- **Status**: For research and evidence linking

### 2.5 Laboratory Reference Ranges

**Note**: Reference ranges vary by:
- Laboratory
- Test methodology
- Population
- Age and sex

**Sources:**
- Clinical laboratory standards (CLSI)
- Manufacturer package inserts
- Local laboratory validation data
- **Must be customized per facility**

### 2.6 Symptoms and Clinical Findings

#### SNOMED CT
- **Source**: SNOMED International
- **Content**: Comprehensive clinical terminology
- **URL**: https://www.snomed.org/
- **License**: Free in member countries, license required otherwise
- **Cost**: Free for members, $$$ for non-members
- **Data Format**: RF2 files
- **Coverage**: 350,000+ concepts
- **Status**: Recommended for structured terminology

#### Medical Subject Headings (MeSH)
- **Source**: U.S. National Library of Medicine
- **Content**: Biomedical vocabulary
- **URL**: https://www.nlm.nih.gov/mesh/
- **License**: Public domain
- **Cost**: Free
- **Status**: Supplementary source

## 3. Data Collection and Integration Strategy

### 3.1 Initial Data Population

**Phase 1: Core Content (Manual Entry)**
1. 50-100 most common diseases
2. 200-300 common symptoms
3. 100-200 essential medicines
4. Basic drug interactions
5. Emergency protocols

**Phase 2: Automated Import**
1. ICD-11 integration
2. Ethiopian medicine registry
3. WHO essential medicines
4. Common laboratory tests

**Phase 3: Enhanced Content**
1. DrugBank integration (if licensed)
2. Comprehensive interactions
3. Clinical guidelines database
4. Advanced decision rules

### 3.2 Import Pipeline

```python
class DataImportPipeline:
    """
    Generic import pipeline for external data
    """
    def __init__(self, source_name, source_type):
        self.source_name = source_name
        self.source_type = source_type
        self.import_job = None
    
    def run_import(self, file_path, dry_run=False):
        """
        Execute import with validation
        """
        # Create import job
        self.import_job = ImportJob.objects.create(
            source_name=self.source_name,
            source_type=self.source_type,
            file_path=file_path,
            dry_run=dry_run,
            status='pending',
            started_by=get_current_user()
        )
        
        try:
            # Step 1: Load data
            raw_data = self.load_data(file_path)
            self.import_job.total_records = len(raw_data)
            self.import_job.save()
            
            # Step 2: Validate schema
            validation_errors = self.validate_schema(raw_data)
            if validation_errors:
                self.import_job.status = 'validation_failed'
                self.import_job.error_summary = validation_errors
                self.import_job.save()
                return
            
            # Step 3: Transform data
            transformed_data = self.transform_data(raw_data)
            
            # Step 4: Check for duplicates
            duplicates = self.detect_duplicates(transformed_data)
            self.import_job.duplicate_count = len(duplicates)
            
            # Step 5: Preview (if dry run)
            if dry_run:
                self.import_job.status = 'preview_ready'
                self.import_job.preview_data = transformed_data[:10]
                self.import_job.save()
                return
            
            # Step 6: Import with provenance
            imported_count = 0
            failed_count = 0
            
            for record in transformed_data:
                try:
                    self.import_record(record, self.import_job)
                    imported_count += 1
                except Exception as e:
                    failed_count += 1
                    self.log_import_error(record, str(e))
            
            # Step 7: Complete
            self.import_job.status = 'completed'
            self.import_job.imported_count = imported_count
            self.import_job.failed_count = failed_count
            self.import_job.completed_at = timezone.now()
            self.import_job.save()
            
        except Exception as e:
            self.import_job.status = 'failed'
            self.import_job.error_message = str(e)
            self.import_job.save()
            raise
```

### 3.3 Data Provenance Tracking

**Every imported record must include:**
```python
class ProvenanceMetadata(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Source information
    source_organization = models.CharField(max_length=255)
    source_database = models.CharField(max_length=255)
    source_url = models.URLField(blank=True)
    source_version = models.CharField(max_length=50)
    source_identifier = models.CharField(max_length=255)
    
    # Import metadata
    import_job = models.ForeignKey(ImportJob)
    import_datetime = models.DateTimeField(auto_now_add=True)
    
    # Data quality
    data_quality_score = models.DecimalField(max_digits=3, decimal_places=2)
    completeness_score = models.DecimalField(max_digits=3, decimal_places=2)
    
    # License
    license_type = models.CharField(max_length=100)
    license_url = models.URLField(blank=True)
    attribution_required = models.BooleanField(default=False)
```

## 4. Licensing Compliance

### 4.1 License Tracking

```python
class DataSourceLicense(models.Model):
    source_name = models.CharField(max_length=255)
    license_type = models.CharField(choices=[
        ('public_domain', 'Public Domain'),
        ('cc0', 'CC0 - Public Domain Dedication'),
        ('cc_by', 'CC BY - Attribution'),
        ('cc_by_sa', 'CC BY-SA - Attribution ShareAlike'),
        ('proprietary_free', 'Proprietary - Free Use'),
        ('proprietary_commercial', 'Proprietary - Commercial License'),
        ('government', 'Government/Public Data'),
    ])
    
    license_url = models.URLField()
    license_text = models.TextField()
    
    # Usage terms
    commercial_use_allowed = models.BooleanField()
    attribution_required = models.BooleanField()
    share_alike_required = models.BooleanField()
    modifications_allowed = models.BooleanField()
    
    # License holder
    license_holder = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    
    # Agreement
    license_agreement_file = models.FileField(blank=True)
    agreement_date = models.DateField(null=True)
    expires_date = models.DateField(null=True)
    
    # Audit
    added_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateField()
    next_review_date = models.DateField()
```

### 4.2 Attribution Requirements

**Display where required:**
```html
<!-- Attribution footer example -->
<footer class="attribution">
  <p>Medical data sources:</p>
  <ul>
    <li>Disease classifications from WHO ICD-11 (https://icd.who.int/)</li>
    <li>Drug information from DrugBank (https://www.drugbank.com/) - Licensed for non-commercial use</li>
    <li>Clinical guidelines from WHO (https://www.who.int/)</li>
  </ul>
  <p>Last updated: 2026-10-19</p>
</footer>
```

## 5. Recommended Data Sources by Priority

### Priority 1: Essential for MVP
1. ✅ ICD-10/ICD-11 - Disease classification
2. ✅ Ethiopian FDA medicine registry
3. ✅ WHO Essential Medicines List
4. ✅ Basic drug interactions (manual/open source)
5. ✅ WHO clinical guidelines (selected conditions)

### Priority 2: Enhanced Functionality
1. ⚠ DrugBank - Comprehensive drug data
2. ⚠ RxNorm - Medicine normalization
3. ⚠ SNOMED CT - Clinical terminology
4. ⚠ Additional clinical guidelines

### Priority 3: Advanced Features
1. 🔄 UpToDate - Premium clinical content
2. 🔄 Proprietary interaction databases
3. 🔄 Specialized disease databases
4. 🔄 Research literature integration

## 6. Data Quality Management

### 6.1 Quality Dimensions

- **Accuracy**: Information is correct
- **Completeness**: All required fields populated
- **Consistency**: No contradictions
- **Timeliness**: Information is current
- **Provenance**: Source is documented

### 6.2 Quality Assurance Process

```python
def assess_content_quality(content):
    """
    Assess quality of imported medical content
    """
    quality_score = 0
    max_score = 100
    
    # Completeness (30 points)
    required_fields = ['name', 'definition', 'source']
    optional_fields = ['synonyms', 'icd_code', 'category']
    
    completeness = sum(
        30/len(required_fields) for field in required_fields 
        if getattr(content, field)
    )
    quality_score += completeness
    
    # Source credibility (20 points)
    if content.source_organization in TRUSTED_SOURCES:
        quality_score += 20
    elif content.source_organization in KNOWN_SOURCES:
        quality_score += 10
    
    # Recency (20 points)
    if content.publication_date:
        age_years = (date.today() - content.publication_date).days / 365
        if age_years < 2:
            quality_score += 20
        elif age_years < 5:
            quality_score += 10
    
    # Evidence level (20 points)
    if content.evidence_level in ['systematic_review', 'rct']:
        quality_score += 20
    elif content.evidence_level in ['cohort_study', 'case_control']:
        quality_score += 10
    
    # Peer review (10 points)
    if content.peer_reviewed:
        quality_score += 10
    
    return {
        'quality_score': quality_score,
        'grade': get_quality_grade(quality_score),
        'issues': identify_quality_issues(content)
    }
```

## 7. Update and Maintenance Strategy

### 7.1 Update Frequency

| Data Type | Update Frequency | Method |
|-----------|------------------|--------|
| Disease classifications | Annually | API sync |
| Medicine database | Quarterly | API/manual |
| Drug interactions | Quarterly | Import |
| Clinical guidelines | As published | Manual review |
| Laboratory ranges | As needed | Facility-specific |

### 7.2 Change Management

```python
class ContentUpdate(models.Model):
    """
    Track updates to medical knowledge content
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey()
    
    update_type = models.CharField(choices=[
        ('new', 'New Content'),
        ('update', 'Content Update'),
        ('correction', 'Correction'),
        ('deprecation', 'Deprecation'),
    ])
    
    previous_version = models.JSONField()
    new_version = models.JSONField()
    changes_summary = models.TextField()
    
    reason = models.TextField()
    evidence_source = models.URLField(blank=True)
    
    # Approval
    status = models.CharField(choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    reviewed_by = models.ForeignKey(User, null=True)
    reviewed_at = models.DateTimeField(null=True)
    
    applied_at = models.DateTimeField(null=True)
```

## 8. Data Governance

### 8.1 Content Approval Workflow

1. **Import/Create** - Content entered into system
2. **Validation** - Automated quality checks
3. **Clinical Review** - Healthcare professional review
4. **Approval** - Authorized reviewer approves
5. **Publication** - Content becomes active
6. **Monitoring** - Usage and accuracy monitored

### 8.2 Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| **Data Curator** | Import and maintain data sources |
| **Clinical Reviewer** | Review medical accuracy |
| **Data Quality Analyst** | Monitor quality metrics |
| **Compliance Officer** | Ensure licensing compliance |

## 9. Ethical and Legal Considerations

### 9.1 Intellectual Property

- ✅ Respect copyright
- ✅ Honor license terms
- ✅ Provide required attribution
- ✅ Do not scrape restricted data
- ✅ Obtain necessary agreements

### 9.2 Clinical Accuracy Responsibility

- ✅ Verify information accuracy
- ✅ Review updates before deployment
- ✅ Document sources and evidence levels
- ✅ Clearly mark unverified content
- ✅ Provide mechanism for corrections

## 10. Contact Information for Licensing

### Key Organizations to Contact

1. **WHO** - https://www.who.int/about/policies/terms-of-use
2. **DrugBank** - https://www.drugbank.com/contact
3. **SNOMED International** - https://www.snomed.org/get-snomed
4. **Ethiopian FDA** - [Contact details TBD]

## 11. Budget Considerations

### Estimated Licensing Costs (Annual)

| Data Source | Cost Estimate | Priority | Notes |
|-------------|---------------|----------|-------|
| WHO ICD-11 | Free | P1 | Verify terms for commercial use |
| Ethiopian FDA Registry | Free | P1 | May require data sharing agreement |
| DrugBank Academic | Free | P2 | Academic use only |
| DrugBank Commercial | $5,000-25,000 | P2 | Depends on organization size |
| SNOMED CT | Free-$10,000 | P2 | Depends on country membership |
| RxNorm | Free | P2 | UMLS license required |
| UpToDate | $500+/user | P3 | Premium content |

**Total Estimated Annual Cost (excluding premium)**: $5,000 - $35,000

## 12. Action Items

### Immediate (Pre-Development)
- [ ] Register for WHO ICD-11 API access
- [ ] Contact Ethiopian FDA regarding data access
- [ ] Download WHO Essential Medicines List
- [ ] Review DrugBank licensing options
- [ ] Apply for UMLS license (for RxNorm)

### Short-term (Month 1-3)
- [ ] Implement ICD-11 API integration
- [ ] Create manual entry workflow for essential content
- [ ] Establish data quality procedures
- [ ] Define content approval workflow

### Medium-term (Month 3-6)
- [ ] Evaluate commercial data sources
- [ ] Negotiate licensing agreements
- [ ] Implement automated update procedures
- [ ] Expand content coverage

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Status**: APPROVED FOR DEVELOPMENT  
**Next Review**: 2027-01-19

**Data Governance Lead**: [To be assigned]
