"""
Audit middleware for tracking user actions.
"""


class AuditMiddleware:
    """Middleware to log user actions for audit trail."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Log audit trail here (to be implemented)
        # For now, just pass through
        
        return response
