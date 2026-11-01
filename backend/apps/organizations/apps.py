"""
App configuration for organizations app.
"""
from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organizations'
    verbose_name = 'Organizations'
    
    def ready(self):
        """Import signals when app is ready."""
        pass  # Import signals here when needed
