import json
from pathlib import Path
from django.shortcuts import render
from django.views import View
from apps.medical_knowledge.models import Disease, Symptom, Medicine
from apps.decision_support.ml_engine.model_trainer import METRICS_JSON_PATH


class CDSSDashboardView(View):
    """
    Renders the modern, interactive Clinical Decision Support System dashboard.
    """
    def get(self, request):
        total_diseases = Disease.objects.filter(is_active=True).count()
        total_symptoms = Symptom.objects.filter(is_active=True).count()
        total_medicines = Medicine.objects.filter(is_active=True).count()
        
        # Load ML model training metrics if available
        ml_metrics = {}
        if METRICS_JSON_PATH.exists():
            try:
                with open(METRICS_JSON_PATH, 'r', encoding='utf-8') as f:
                    ml_metrics = json.load(f)
            except Exception:
                pass
        
        context = {
            'total_diseases': total_diseases,
            'total_symptoms': total_symptoms,
            'total_medicines': total_medicines,
            'body_systems': Symptom.BodySystem.choices,
            'ml_metrics': ml_metrics,
        }
        return render(request, 'decision_support/cdss_dashboard.html', context)
