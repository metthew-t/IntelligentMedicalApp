"""
Django Admin interface customization for Medical Knowledge models.
"""
from django.contrib import admin
from apps.medical_knowledge.models import (
    Disease, Symptom, DiseaseSymptom, Medicine, DrugInteraction, DiseaseTreatment
)


class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 1
    autocomplete_fields = ['symptom']
    fields = ['symptom', 'frequency', 'specificity', 'is_hallmark', 'stage', 'notes']


class DiseaseTreatmentInline(admin.TabularInline):
    model = DiseaseTreatment
    extra = 1
    autocomplete_fields = ['medicine']
    fields = ['medicine', 'treatment_line', 'regimen_instructions', 'target_population']


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icd10_code', 'typical_age_group', 'status', 'is_active', 'updated_at']
    list_filter = ['category', 'status', 'is_active']
    search_fields = ['name', 'icd10_code', 'icd11_code', 'synonyms', 'definition']
    inlines = [DiseaseSymptomInline, DiseaseTreatmentInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('name', 'name_local', 'synonyms', 'category', 'icd10_code', 'icd11_code')
        }),
        ('Clinical Overview', {
            'fields': ('definition', 'etiology', 'risk_factors', 'complications', 'typical_age_group')
        }),
        ('Diagnostic & Management', {
            'fields': ('diagnostic_criteria', 'management_overview', 'prevention_guidance', 'referral_criteria')
        }),
        ('Status & Metadata', {
            'fields': ('status', 'version', 'source_organization', 'source_url', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'symptom_type', 'body_system', 'is_red_flag', 'severity_weight', 'is_active']
    list_filter = ['symptom_type', 'body_system', 'is_red_flag', 'is_active']
    search_fields = ['name', 'synonyms', 'description', 'snomed_code']
    ordering = ['body_system', 'name']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['generic_name', 'drug_class', 'dosage_form', 'strength', 'route_of_administration', 'pregnancy_category', 'is_essential_medicine']
    list_filter = ['drug_class', 'dosage_form', 'route_of_administration', 'pregnancy_category', 'is_essential_medicine']
    search_fields = ['generic_name', 'brand_names', 'atc_code', 'indications']


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ['medicine_a', 'medicine_b', 'severity', 'interaction_type']
    list_filter = ['severity', 'interaction_type']
    search_fields = ['medicine_a__generic_name', 'medicine_b__generic_name', 'description']
    autocomplete_fields = ['medicine_a', 'medicine_b']


@admin.register(DiseaseTreatment)
class DiseaseTreatmentAdmin(admin.ModelAdmin):
    list_display = ['disease', 'medicine', 'treatment_line', 'target_population']
    list_filter = ['treatment_line']
    search_fields = ['disease__name', 'medicine__generic_name']
    autocomplete_fields = ['disease', 'medicine']
