"""
Custom exception handlers for the Intelligent Medical System.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
import logging
import uuid

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Log the exception
    logger.error(
        f"Exception occurred: {exc.__class__.__name__}: {str(exc)}",
        extra={
            'request_id': request_id,
            'view': context.get('view'),
            'request': context.get('request'),
        },
        exc_info=True
    )
    
    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            error_details = exc.message_dict
        elif hasattr(exc, 'messages'):
            error_details = {'detail': exc.messages}
        else:
            error_details = {'detail': str(exc)}
        
        return Response(
            {
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid input data',
                    'details': error_details,
                    'timestamp': get_timestamp(),
                    'request_id': request_id,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle Http404
    if isinstance(exc, Http404):
        return Response(
            {
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Resource not found',
                    'details': {'detail': str(exc)},
                    'timestamp': get_timestamp(),
                    'request_id': request_id,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # If response is None, it's an unhandled exception
    if response is None:
        return Response(
            {
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An unexpected error occurred. Please contact support.',
                    'details': {
                        'detail': str(exc) if settings.DEBUG else 'Internal server error'
                    },
                    'timestamp': get_timestamp(),
                    'request_id': request_id,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Customize the response format
    if response.status_code >= 400:
        error_code = get_error_code(response.status_code)
        error_message = get_error_message(response.status_code, response.data)
        
        response.data = {
            'error': {
                'code': error_code,
                'message': error_message,
                'details': response.data,
                'timestamp': get_timestamp(),
                'request_id': request_id,
            }
        }
    
    return response


def get_error_code(status_code):
    """Get error code based on HTTP status code"""
    error_codes = {
        400: 'VALIDATION_ERROR',
        401: 'AUTHENTICATION_FAILED',
        403: 'PERMISSION_DENIED',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        409: 'CONFLICT',
        429: 'RATE_LIMIT_EXCEEDED',
        500: 'SERVER_ERROR',
        503: 'SERVICE_UNAVAILABLE',
    }
    return error_codes.get(status_code, 'ERROR')


def get_error_message(status_code, data):
    """Get user-friendly error message"""
    default_messages = {
        400: 'Invalid input data',
        401: 'Authentication failed',
        403: 'Permission denied',
        404: 'Resource not found',
        405: 'Method not allowed',
        409: 'Resource conflict',
        429: 'Too many requests',
        500: 'Internal server error',
        503: 'Service temporarily unavailable',
    }
    
    # Try to extract a more specific message from the data
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        if 'message' in data:
            return str(data['message'])
    
    return default_messages.get(status_code, 'An error occurred')


def get_timestamp():
    """Get current timestamp in ISO format"""
    from django.utils import timezone
    return timezone.now().isoformat()


class ClinicalSafetyError(Exception):
    """
    Exception raised when a clinical safety check fails.
    This is a critical error that should prevent the operation.
    """
    pass


class PrescriptionSafetyError(ClinicalSafetyError):
    """Exception raised when prescription safety checks fail"""
    pass


class MLModelUnavailableError(Exception):
    """Exception raised when ML model is not available"""
    pass


class CDSSServiceError(Exception):
    """Exception raised when CDSS service fails"""
    pass


# Import settings at module level to avoid circular imports
from django.conf import settings
