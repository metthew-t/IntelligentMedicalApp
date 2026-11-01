"""
Custom permission classes for the Intelligent Medical System.
"""
from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class for system administrators.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('system_admin')
        )


class IsHospitalAdmin(permissions.BasePermission):
    """
    Permission class for hospital administrators.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.has_role('system_admin') or
             request.user.has_role('hospital_admin'))
        )


class IsDoctor(permissions.BasePermission):
    """
    Permission class for doctors.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('doctor')
        )


class IsNurse(permissions.BasePermission):
    """
    Permission class for nurses.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('nurse')
        )


class IsPharmacist(permissions.BasePermission):
    """
    Permission class for pharmacists.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('pharmacist')
        )


class IsLabStaff(permissions.BasePermission):
    """
    Permission class for laboratory staff.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('lab_staff')
        )


class IsClinicalStaff(permissions.BasePermission):
    """
    Permission class for any clinical staff (doctor, nurse, etc).
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        clinical_roles = ['doctor', 'nurse', 'triage_nurse']
        return any(request.user.has_role(role) for role in clinical_roles)


class HasPatientAccess(permissions.BasePermission):
    """
    Permission class to check if user has access to a specific patient.
    Should be used in combination with object-level permissions.
    """
    def has_object_permission(self, request, view, obj):
        # System admins have access to all patients
        if request.user.has_role('system_admin'):
            return True
        
        # Check if patient belongs to user's facility
        if hasattr(obj, 'registered_facility'):
            if obj.registered_facility not in request.user.get_facilities():
                return False
        
        # Doctors can access patients they're treating
        if request.user.has_role('doctor'):
            from apps.encounters.models import Encounter
            return Encounter.objects.filter(
                patient=obj,
                attending_physician=request.user,
                is_active=True
            ).exists()
        
        # Other clinical staff can access patients in their care
        if request.user.has_role('nurse') or request.user.has_role('triage_nurse'):
            # Check if they have active encounters with this patient
            from apps.encounters.models import Encounter
            return Encounter.objects.filter(
                patient=obj,
                facility__in=request.user.get_facilities(),
                is_active=True
            ).exists()
        
        return False


class HasPrescriptionAccess(permissions.BasePermission):
    """
    Permission class for prescription access.
    """
    def has_object_permission(self, request, view, obj):
        # System admins have full access
        if request.user.has_role('system_admin'):
            return True
        
        # Check facility access
        if obj.facility not in request.user.get_facilities():
            return False
        
        # Prescriber can access their own prescriptions
        if obj.prescriber == request.user:
            return True
        
        # Pharmacists can access prescriptions for dispensing
        if request.user.has_role('pharmacist'):
            return True
        
        # Doctors treating the patient can access
        if request.user.has_role('doctor'):
            return HasPatientAccess().has_object_permission(
                request, view, obj.patient
            )
        
        return False


class CanApproveContent(permissions.BasePermission):
    """
    Permission class for approving medical content.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('clinical_reviewer')
        )


class CanApproveMLModel(permissions.BasePermission):
    """
    Permission class for approving ML models.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('ml_reviewer')
        )


class IsAuditor(permissions.BasePermission):
    """
    Permission class for auditors.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('auditor')
        )


class ReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
