# Machine Learning Governance Framework

## 1. Overview

This document defines the governance framework for machine learning within the Intelligent Medical and Hospital Management System. ML in healthcare requires rigorous oversight to ensure safety, effectiveness, fairness, and transparency.

## 2. ML Governance Principles

1. **Clinical Safety First** - Patient safety is the highest priority
2. **Human Oversight** - ML assists, never replaces, clinical judgment
3. **Transparency** - Model decisions must be explainable
4. **Fairness** - Performance must be equitable across populations
5. **Accountability** - Clear ownership and responsibility
6. **Continuous Monitoring** - Ongoing performance surveillance
7. **Controlled Learning** - No autonomous retraining
8. **Reversibility** - Immediate rollback capability

## 3. ML Lifecycle Governance

### Phase 1: Problem Definition

**Governance Requirements:**
- ✅ Clinical need clearly documented
- ✅ Intended use defined
- ✅ Target population specified
- ✅ Success criteria established
- ✅ Clinical stakeholders identified
- ✅ Ethics review completed

**Approval Required From:**
- Clinical Advisory Board
- ML Governance Committee

### Phase 2: Data Collection

**Governance Requirements:**
- ✅ Data source authorization documented
- ✅ Patient consent verified (where required)
- ✅ Data use purpose clearly defined
- ✅ Privacy impact assessment completed
- ✅ Data quality assessment performed
- ✅ Bias assessment planned

**Data Quality Checklist:**
```python
class DataQualityAssessment:
    def assess_dataset(self, dataset):
        return {
            'completeness': self.check_completeness(dataset),
            'accuracy': self.check_accuracy(dataset),
            'consistency': self.check_consistency(dataset),
            'timeliness': self.check_timeliness(dataset),
            'representativeness': self.check_representativeness(dataset),
            'label_quality': self.assess_labels(dataset),
            'bias_indicators': self.assess_bias(dataset)
        }
    
    def check_representativeness(self, dataset):
        """Ensure dataset represents target population"""
        return {
            'age_distribution': self.compare_to_population(dataset.age_groups),
            'sex_distribution': self.compare_to_population(dataset.sex),
            'geographic_coverage': self.assess_geography(dataset),
            'disease_prevalence': self.compare_prevalence(dataset),
            'underrepresented_groups': self.identify_gaps(dataset)
        }
```

### Phase 3: Model Development

**Governance Requirements:**
- ✅ Model architecture justified
- ✅ Training methodology documented
- ✅ Hyperparameters recorded
- ✅ Cross-validation performed
- ✅ Model artifacts versioned
- ✅ Code reviewed
- ✅ Reproducibility verified

**Model Card Template:**
```markdown
# Model Card: [Model Name] v[Version]

## Model Details
- **Developer**: [Team/Individual]
- **Model Date**: [Date]
- **Model Type**: [Algorithm]
- **Model Version**: [Version]

## Intended Use
- **Primary Use**: [Description]
- **Primary Users**: [User types]
- **Out-of-Scope Uses**: [What NOT to use for]

## Training Data
- **Dataset**: [Name and version]
- **Size**: [Number of records]
- **Time Period**: [Date range]
- **Geographic Coverage**: [Locations]

## Performance Metrics
- **Overall Accuracy**: [Value]
- **Sensitivity**: [Value]
- **Specificity**: [Value]
- **AUROC**: [Value]
- **Calibration**: [Description]

## Subgroup Performance
- [Performance by age, sex, etc.]

## Limitations
- [Known limitations]
- [Edge cases]
- [When not to use]

## Ethical Considerations
- [Bias assessment results]
- [Fairness metrics]
- [Potential harms]
```

### Phase 4: Evaluation

**Required Evaluations:**

**Clinical Performance:**
```python
def evaluate_clinical_performance(model, test_data):
    """
    Comprehensive clinical evaluation
    """
    results = {}
    
    # Overall performance
    results['overall'] = {
        'accuracy': calculate_accuracy(model, test_data),
        'sensitivity': calculate_sensitivity(model, test_data),
        'specificity': calculate_specificity(model, test_data),
        'ppv': calculate_ppv(model, test_data),
        'npv': calculate_npv(model, test_data),
        'auroc': calculate_auroc(model, test_data),
        'auprc': calculate_auprc(model, test_data)
    }
    
    # Calibration
    results['calibration'] = {
        'calibration_plot': generate_calibration_plot(model, test_data),
        'brier_score': calculate_brier_score(model, test_data),
        'hosmer_lemeshow': hosmer_lemeshow_test(model, test_data)
    }
    
    # Subgroup analysis
    results['subgroups'] = {}
    for subgroup in ['age_group', 'sex', 'ethnicity']:
        results['subgroups'][subgroup] = evaluate_subgroup(
            model, test_data, subgroup
        )
    
    # Clinical utility
    results['clinical_utility'] = {
        'decision_curve': generate_decision_curve(model, test_data),
        'nnt': calculate_nnt(model, test_data),  # Number needed to treat
        'diagnostic_yield': calculate_diagnostic_yield(model, test_data)
    }
    
    # Failure analysis
    results['failures'] = {
        'false_negatives': analyze_false_negatives(model, test_data),
        'false_positives': analyze_false_positives(model, test_data),
        'error_patterns': identify_error_patterns(model, test_data)
    }
    
    return results
```

**Fairness Assessment:**
```python
def assess_fairness(model, test_data):
    """
    Assess model fairness across demographic groups
    """
    protected_attributes = ['age_group', 'sex', 'ethnicity', 'socioeconomic_status']
    
    fairness_metrics = {}
    
    for attribute in protected_attributes:
        groups = test_data[attribute].unique()
        
        # Statistical parity
        fairness_metrics[f'{attribute}_statistical_parity'] = \
            calculate_statistical_parity(model, test_data, attribute, groups)
        
        # Equal opportunity
        fairness_metrics[f'{attribute}_equal_opportunity'] = \
            calculate_equal_opportunity(model, test_data, attribute, groups)
        
        # Equalized odds
        fairness_metrics[f'{attribute}_equalized_odds'] = \
            calculate_equalized_odds(model, test_data, attribute, groups)
        
        # Predictive parity
        fairness_metrics[f'{attribute}_predictive_parity'] = \
            calculate_predictive_parity(model, test_data, attribute, groups)
    
    # Overall fairness score
    fairness_metrics['overall_fairness_score'] = \
        aggregate_fairness_score(fairness_metrics)
    
    # Bias indicators
    fairness_metrics['bias_detected'] = any(
        metric['disparity_ratio'] > 1.2 or metric['disparity_ratio'] < 0.8
        for metric in fairness_metrics.values()
        if isinstance(metric, dict) and 'disparity_ratio' in metric
    )
    
    return fairness_metrics
```

**Acceptance Criteria:**
- Sensitivity ≥ 0.85 for critical conditions
- Specificity ≥ 0.80
- AUROC ≥ 0.80
- Calibration error < 0.10
- Subgroup performance within 10% of overall performance
- No disparate impact > 1.2 for protected groups

### Phase 5: Approval Workflow

**Multi-Stage Approval:**

```python
class ModelApprovalWorkflow:
    def __init__(self, model_version):
        self.model = model_version
        self.approvals = []
        self.required_approvers = [
            'clinical_reviewer',
            'ml_reviewer',
            'safety_reviewer',
            'compliance_reviewer'
        ]
    
    def submit_for_approval(self):
        """Initiate approval process"""
        return ModelApproval.objects.create(
            model=self.model,
            status='pending',
            submitted_by=self.model.created_by,
            submitted_at=timezone.now()
        )
    
    def review(self, reviewer, decision, comments):
        """Record reviewer decision"""
        if reviewer.role not in self.required_approvers:
            raise PermissionDenied("Not authorized to approve models")
        
        approval = ModelApprovalDecision.objects.create(
            model=self.model,
            reviewer=reviewer,
            reviewer_role=reviewer.role,
            decision=decision,  # 'approved', 'rejected', 'conditional'
            comments=comments,
            reviewed_at=timezone.now()
        )
        
        self.approvals.append(approval)
        
        # Check if all approvals received
        if self._all_approved():
            self.model.approval_status = 'approved'
            self.model.save()
            return {'status': 'fully_approved'}
        elif self._any_rejected():
            self.model.approval_status = 'rejected'
            self.model.save()
            return {'status': 'rejected'}
        else:
            return {'status': 'awaiting_approvals'}
    
    def _all_approved(self):
        approved_roles = set(
            a.reviewer_role for a in self.approvals 
            if a.decision == 'approved'
        )
        return approved_roles == set(self.required_approvers)
```

### Phase 6: Deployment

**Pre-Deployment Checklist:**
- [ ] All approvals received
- [ ] Model artifacts stored securely
- [ ] Model version documented
- [ ] API integration tested
- [ ] Monitoring configured
- [ ] Rollback procedure tested
- [ ] User documentation updated
- [ ] Training materials prepared
- [ ] Deployment plan approved

**Controlled Deployment:**
```python
class ModelDeployment:
    def deploy_model(self, model_version, deployment_plan):
        """
        Controlled model deployment with safeguards
        """
        # Verify approval
        if model_version.approval_status != 'approved':
            raise ValidationError("Cannot deploy unapproved model")
        
        # Verify no active deployment of same model
        active_deployments = ModelDeployment.objects.filter(
            model_name=model_version.model_name,
            status='active'
        )
        
        if active_deployments.exists() and not deployment_plan.replace_existing:
            raise ValidationError("Active deployment exists")
        
        # Create deployment record
        deployment = ModelDeployment.objects.create(
            model_version=model_version,
            deployed_by=deployment_plan.deployed_by,
            deployment_datetime=timezone.now(),
            deployment_environment='production',
            rollback_version=self._get_current_version(),
            status='deploying'
        )
        
        try:
            # Deploy model
            self._deploy_to_inference_service(model_version)
            
            # Run post-deployment tests
            self._run_smoke_tests(model_version)
            
            # Update status
            deployment.status = 'active'
            deployment.save()
            
            # Deactivate old version
            if active_deployments.exists():
                active_deployments.update(
                    status='superseded',
                    superseded_at=timezone.now()
                )
            
            # Initialize monitoring
            self._start_monitoring(deployment)
            
            return {'status': 'success', 'deployment': deployment}
            
        except Exception as e:
            # Rollback on failure
            deployment.status = 'failed'
            deployment.error_message = str(e)
            deployment.save()
            
            logger.error(f"Model deployment failed: {e}")
            self._rollback_deployment(deployment)
            
            return {'status': 'failed', 'error': str(e)}
```

### Phase 7: Monitoring

**Continuous Monitoring:**

```python
class ModelMonitoring:
    def monitor_model_performance(self, deployment):
        """
        Real-time model monitoring
        """
        metrics = {}
        
        # Data drift detection
        metrics['data_drift'] = self.detect_data_drift(deployment)
        
        # Prediction drift
        metrics['prediction_drift'] = self.detect_prediction_drift(deployment)
        
        # Performance monitoring (when outcomes available)
        metrics['performance'] = self.monitor_performance(deployment)
        
        # Usage patterns
        metrics['usage'] = self.monitor_usage(deployment)
        
        # Error rates
        metrics['errors'] = self.monitor_errors(deployment)
        
        # Latency
        metrics['latency'] = self.monitor_latency(deployment)
        
        # Check thresholds
        alerts = self.check_thresholds(metrics)
        
        if alerts:
            self.send_alerts(alerts)
            
            # Auto-rollback on critical issues
            if any(a['severity'] == 'critical' for a in alerts):
                self.initiate_rollback(deployment, reason='Critical monitoring alert')
        
        return metrics
    
    def detect_data_drift(self, deployment):
        """
        Detect if input data distribution has changed
        """
        reference_data = deployment.model_version.training_data_statistics
        recent_data = self.get_recent_predictions(deployment, days=7)
        
        drift_scores = {}
        
        for feature in reference_data.features:
            # KS test for numerical features
            if feature.type == 'numerical':
                ks_statistic, p_value = ks_2samp(
                    reference_data[feature.name],
                    recent_data[feature.name]
                )
                drift_scores[feature.name] = {
                    'test': 'ks_test',
                    'statistic': ks_statistic,
                    'p_value': p_value,
                    'drift_detected': p_value < 0.05
                }
            
            # Chi-square test for categorical features
            elif feature.type == 'categorical':
                chi2, p_value = chi2_contingency(
                    pd.crosstab(
                        reference_data[feature.name],
                        recent_data[feature.name]
                    )
                )
                drift_scores[feature.name] = {
                    'test': 'chi2_test',
                    'statistic': chi2,
                    'p_value': p_value,
                    'drift_detected': p_value < 0.05
                }
        
        # Overall drift score
        drift_detected_count = sum(
            1 for score in drift_scores.values() 
            if score['drift_detected']
        )
        
        return {
            'feature_drift_scores': drift_scores,
            'drift_detected': drift_detected_count > len(drift_scores) * 0.2,
            'features_with_drift': drift_detected_count,
            'action_required': drift_detected_count > len(drift_scores) * 0.3
        }
```

### Phase 8: Rollback

**Immediate Rollback Capability:**

```python
def rollback_model_deployment(deployment, reason):
    """
    Emergency model rollback
    """
    logger.warning(f"Initiating model rollback: {reason}")
    
    # Get previous version
    previous_deployment = ModelDeployment.objects.filter(
        model_name=deployment.model_name,
        status='superseded',
        deployment_datetime__lt=deployment.deployment_datetime
    ).order_by('-deployment_datetime').first()
    
    if not previous_deployment:
        raise ValueError("No previous version available for rollback")
    
    # Create rollback record
    rollback = ModelRollback.objects.create(
        from_deployment=deployment,
        to_deployment=previous_deployment,
        reason=reason,
        initiated_by=get_current_user(),
        initiated_at=timezone.now(),
        status='in_progress'
    )
    
    try:
        # Restore previous version
        _deploy_to_inference_service(previous_deployment.model_version)
        
        # Verify rollback
        _run_smoke_tests(previous_deployment.model_version)
        
        # Update statuses
        deployment.status = 'rolled_back'
        deployment.rolled_back_at = timezone.now()
        deployment.save()
        
        previous_deployment.status = 'active'
        previous_deployment.save()
        
        rollback.status = 'completed'
        rollback.completed_at = timezone.now()
        rollback.save()
        
        logger.info(f"Model rollback completed successfully")
        
        # Notify stakeholders
        notify_stakeholders({
            'event': 'model_rollback',
            'deployment': deployment,
            'reason': reason,
            'status': 'completed'
        })
        
        return {'status': 'success'}
        
    except Exception as e:
        rollback.status = 'failed'
        rollback.error_message = str(e)
        rollback.save()
        
        logger.error(f"Model rollback failed: {e}")
        
        # Escalate
        escalate_critical_incident({
            'type': 'rollback_failure',
            'deployment': deployment,
            'error': str(e)
        })
        
        return {'status': 'failed', 'error': str(e)}
```

## 4. Governance Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **ML Product Owner** | Define requirements, prioritize features, accept deliverables |
| **Clinical Lead** | Define clinical requirements, review clinical validity |
| **ML Engineer** | Develop models, implement monitoring, maintain infrastructure |
| **Data Scientist** | Data analysis, feature engineering, model evaluation |
| **Clinical Reviewer** | Review clinical appropriateness, safety implications |
| **ML Reviewer** | Review technical implementation, evaluation methodology |
| **Safety Reviewer** | Review safety implications, risk mitigation |
| **Compliance Officer** | Ensure regulatory compliance, review documentation |
| **Ethics Board** | Review ethical implications, fairness assessment |

## 5. Documentation Requirements

**For Each Model:**
- Model card
- Technical specification
- Training data description
- Evaluation report
- Fairness assessment
- Clinical review report
- Approval records
- Deployment plan
- Monitoring plan
- Known limitations
- User documentation

## 6. Ethical Considerations

### 6.1 Bias Mitigation

**Strategies:**
1. Diverse training data
2. Fairness-aware algorithms
3. Regular bias audits
4. Subgroup performance monitoring
5. Stakeholder feedback

### 6.2 Transparency

**Requirements:**
- Explainable predictions
- Feature importance disclosed
- Limitations clearly stated
- Decision process documented
- Uncertainty communicated

### 6.3 Accountability

**Clear ownership:**
- Model development team identified
- Clinical sponsor assigned
- Approval authority documented
- Incident response team designated

## 7. Regulatory Compliance

### 7.1 FDA Software as Medical Device (SaMD)

**Classification:** May require FDA clearance depending on intended use

**Requirements if SaMD:**
- Software requirements specification
- Design history file
- Verification and validation
- Risk analysis (ISO 14971)
- Clinical evaluation
- Post-market surveillance

### 7.2 EU Medical Device Regulation (MDR)

**If deployed in EU:**
- CE marking may be required
- Clinical evaluation per MEDDEV 2.7/1
- Technical documentation
- Quality management system (ISO 13485)

### 7.3 Algorithmic Impact Assessment

**Required for high-risk AI:**
- Purpose and context
- Data characteristics
- Model methodology
- Validation approach
- Risk mitigation
- Fairness assessment
- Monitoring plan

## 8. Continuous Improvement

### 8.1 Model Retraining Policy

**Retraining Triggers:**
- Performance degradation detected
- Data drift exceeds threshold
- New high-quality data available
- Clinical guidelines updated
- Bias identified

**Retraining Process:**
- Follows full governance lifecycle
- Requires re-approval
- A/B testing against current model
- Gradual rollout if superior

### 8.2 Feedback Integration

**Sources:**
- Clinician feedback on predictions
- Patient outcomes (when available)
- Incident reports
- User suggestions
- Performance monitoring

## 9. Governance Tools and Platforms

### 9.1 ML Registry

**Centralized repository for:**
- All datasets (versioned)
- All models (versioned)
- Training runs
- Evaluations
- Approvals
- Deployments
- Monitoring metrics

### 9.2 Experiment Tracking

**Track all experiments:**
- Hyperparameters
- Training metrics
- Evaluation results
- Model artifacts
- Reproducibility information

## 10. Governance Metrics

**Track and Report:**
- Number of models in development
- Number of models in production
- Average time from development to deployment
- Number of rollbacks
- Model performance over time
- Bias metrics by demographic group
- User satisfaction
- Clinical impact (when measurable)

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Status**: APPROVED FOR DEVELOPMENT  
**Next Review**: 2027-04-19

**ML Governance Committee Chair**: [To be assigned]  
**Review Frequency**: Quarterly
