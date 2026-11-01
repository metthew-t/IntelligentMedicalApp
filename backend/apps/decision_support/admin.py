"""
Django Admin interface customization for Decision Support models.
"""
from django.contrib import admin
from apps.decision_support.models import DecisionSupportRequest, DecisionSupportCandidate


class DecisionSupportCandidateInline(admin.TabularInline):
    model = DecisionSupportCandidate
    extra = 0
    fields = ['rank', 'disease', 'probability_score', 'confidence_level', 'clinician_decision']
    readonly_fields = ['rank', 'disease', 'probability_score', 'confidence_level', 'clinician_decision']
    can_delete = False


@admin.register(DecisionSupportRequest)
class DecisionSupportRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'triage_level', 'processing_status', 'processing_time_ms', 'requested_by', 'created_at']
    list_filter = ['triage_level', 'processing_status', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processing_time_ms']
    inlines = [DecisionSupportCandidateInline]
    fieldsets = (
        ('Request Metadata', {
            'fields': ('id', 'triage_level', 'processing_status', 'processing_time_ms', 'engine_version', 'model_version', 'requested_by')
        }),
        ('Patient Clinical Snapshot', {
            'fields': ('patient_demographics', 'symptoms', 'signs', 'vital_signs', 'medical_history')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DecisionSupportCandidate)
class DecisionSupportCandidateAdmin(admin.ModelAdmin):
    list_display = ['disease', 'rank', 'probability_score', 'confidence_level', 'clinician_decision', 'decided_at']
    list_filter = ['confidence_level', 'clinician_decision', 'created_at']
    search_fields = ['disease__name', 'clinician_feedback']
    readonly_fields = ['created_at']
