"""
Management command to initialize system with default data.
Creates default roles, permissions, and facility types.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import Role, Permission, RolePermission
from apps.organizations.models import FacilityType


class Command(BaseCommand):
    help = 'Initialize system with default roles, permissions, and facility types'
    
    def handle(self, *args, **kwargs):
        """Execute the command."""
        self.stdout.write('Initializing system...')
        
        with transaction.atomic():
            # Create default permissions
            self.stdout.write('Creating permissions...')
            permissions_created = self.create_permissions()
            self.stdout.write(self.style.SUCCESS(
                f'Created {permissions_created} permissions'
            ))
            
            # Create default roles
            self.stdout.write('Creating roles...')
            roles_created = self.create_roles()
            self.stdout.write(self.style.SUCCESS(
                f'Created {roles_created} roles'
            ))
            
            # Assign permissions to roles
            self.stdout.write('Assigning permissions to roles...')
            self.assign_permissions_to_roles()
            self.stdout.write(self.style.SUCCESS(
                'Permissions assigned to roles'
            ))
            
            # Create facility types
            self.stdout.write('Creating facility types...')
            facility_types_created = self.create_facility_types()
            self.stdout.write(self.style.SUCCESS(
                f'Created {facility_types_created} facility types'
            ))
        
        self.stdout.write(self.style.SUCCESS(
            'System initialization completed successfully!'
        ))
    
    def create_permissions(self):
        """Create default permissions."""
        permissions_data = [
            # Patient permissions
            ('patient:read', 'Read Patient Records', 'patient', 'read',
             'View patient demographic and medical information'),
            ('patient:write', 'Write Patient Records', 'patient', 'write',
             'Create and update patient records'),
            ('patient:delete', 'Delete Patient Records', 'patient', 'delete',
             'Delete patient records'),
            
            # Encounter permissions
            ('encounter:read', 'Read Encounters', 'encounter', 'read',
             'View patient encounters and visits'),
            ('encounter:write', 'Write Encounters', 'encounter', 'write',
             'Create and update encounters'),
            ('encounter:delete', 'Delete Encounters', 'encounter', 'delete',
             'Delete encounters'),
            
            # Prescription permissions
            ('prescription:read', 'Read Prescriptions', 'prescription', 'read',
             'View prescriptions'),
            ('prescription:write', 'Write Prescriptions', 'prescription', 'write',
             'Create and update prescriptions'),
            ('prescription:approve', 'Approve Prescriptions', 'prescription', 'approve',
             'Approve and sign prescriptions'),
            
            # Laboratory permissions
            ('lab:read', 'Read Lab Results', 'laboratory', 'read',
             'View laboratory test results'),
            ('lab:write', 'Write Lab Orders', 'laboratory', 'write',
             'Create laboratory orders'),
            ('lab:approve', 'Approve Lab Results', 'laboratory', 'approve',
             'Verify and approve lab results'),
            
            # Imaging permissions
            ('imaging:read', 'Read Imaging Results', 'imaging', 'read',
             'View imaging studies and reports'),
            ('imaging:write', 'Write Imaging Orders', 'imaging', 'write',
             'Create imaging orders'),
            ('imaging:approve', 'Approve Imaging Reports', 'imaging', 'approve',
             'Verify and approve imaging reports'),
            
            # Pharmacy permissions
            ('pharmacy:read', 'Read Pharmacy Records', 'pharmacy', 'read',
             'View pharmacy inventory and dispensing records'),
            ('pharmacy:dispense', 'Dispense Medications', 'pharmacy', 'dispense',
             'Dispense medications to patients'),
            ('pharmacy:manage', 'Manage Pharmacy', 'pharmacy', 'manage',
             'Manage pharmacy inventory and operations'),
            
            # Appointment permissions
            ('appointment:read', 'Read Appointments', 'appointment', 'read',
             'View appointments'),
            ('appointment:write', 'Write Appointments', 'appointment', 'write',
             'Create and update appointments'),
            
            # Admission permissions
            ('admission:read', 'Read Admissions', 'admission', 'read',
             'View patient admissions'),
            ('admission:write', 'Write Admissions', 'admission', 'write',
             'Admit and discharge patients'),
            
            # Billing permissions
            ('billing:read', 'Read Billing', 'billing', 'read',
             'View billing information'),
            ('billing:write', 'Write Billing', 'billing', 'write',
             'Create and update bills'),
            ('billing:approve', 'Approve Billing', 'billing', 'approve',
             'Approve and finalize bills'),
            
            # User management permissions
            ('user:read', 'Read Users', 'user', 'read',
             'View user accounts'),
            ('user:write', 'Write Users', 'user', 'write',
             'Create and update user accounts'),
            ('user:manage_roles', 'Manage User Roles', 'user', 'manage_roles',
             'Assign and revoke user roles'),
            
            # System administration permissions
            ('system:manage', 'System Administration', 'system', 'manage',
             'Full system administration access'),
        ]
        
        count = 0
        for code, name, resource_type, action, description in permissions_data:
            _, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'resource_type': resource_type,
                    'action': action,
                    'description': description
                }
            )
            if created:
                count += 1
        
        return count
    
    def create_roles(self):
        """Create default roles."""
        roles_data = [
            ('System Administrator', 'system_admin',
             'Full system access with all permissions', True),
            ('Hospital Administrator', 'hospital_admin',
             'Hospital-level administrative access', True),
            ('Doctor', 'doctor',
             'Medical doctor with clinical access', True),
            ('Nurse', 'nurse',
             'Registered nurse with patient care access', True),
            ('Pharmacist', 'pharmacist',
             'Pharmacy operations and medication dispensing', True),
            ('Lab Technician', 'lab_tech',
             'Laboratory testing and result entry', True),
            ('Radiologist', 'radiologist',
             'Imaging interpretation and reporting', True),
            ('Receptionist', 'receptionist',
             'Front desk and appointment management', True),
            ('Billing Clerk', 'billing_clerk',
             'Billing and financial operations', True),
        ]
        
        count = 0
        for name, code, description, is_system_role in roles_data:
            _, created = Role.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'is_system_role': is_system_role
                }
            )
            if created:
                count += 1
        
        return count
    
    def assign_permissions_to_roles(self):
        """Assign permissions to roles."""
        role_permissions = {
            'system_admin': [
                'system:manage', 'user:read', 'user:write', 'user:manage_roles'
            ],
            'hospital_admin': [
                'user:read', 'user:write', 'user:manage_roles',
                'patient:read', 'billing:read', 'billing:approve'
            ],
            'doctor': [
                'patient:read', 'patient:write',
                'encounter:read', 'encounter:write',
                'prescription:read', 'prescription:write', 'prescription:approve',
                'lab:read', 'lab:write',
                'imaging:read', 'imaging:write',
                'admission:read', 'admission:write'
            ],
            'nurse': [
                'patient:read', 'patient:write',
                'encounter:read', 'encounter:write',
                'prescription:read',
                'lab:read', 'imaging:read',
                'admission:read'
            ],
            'pharmacist': [
                'patient:read',
                'prescription:read',
                'pharmacy:read', 'pharmacy:dispense', 'pharmacy:manage'
            ],
            'lab_tech': [
                'patient:read',
                'lab:read', 'lab:write', 'lab:approve'
            ],
            'radiologist': [
                'patient:read',
                'imaging:read', 'imaging:approve'
            ],
            'receptionist': [
                'patient:read', 'patient:write',
                'appointment:read', 'appointment:write'
            ],
            'billing_clerk': [
                'patient:read',
                'billing:read', 'billing:write'
            ],
        }
        
        for role_code, permission_codes in role_permissions.items():
            try:
                role = Role.objects.get(code=role_code)
                for perm_code in permission_codes:
                    try:
                        permission = Permission.objects.get(code=perm_code)
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=permission
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'Permission {perm_code} not found'
                        ))
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Role {role_code} not found'
                ))
    
    def create_facility_types(self):
        """Create default facility types."""
        facility_types_data = [
            ('Primary Hospital', 'PH',
             'Primary level hospital providing basic healthcare services'),
            ('General Hospital', 'GH',
             'General hospital providing comprehensive healthcare services'),
            ('Specialized Hospital', 'SH',
             'Hospital specialized in specific medical fields'),
            ('Referral Hospital', 'RH',
             'Tertiary referral hospital with advanced medical services'),
            ('Health Center', 'HC',
             'Primary health center providing community healthcare'),
            ('Clinic', 'CL',
             'Outpatient clinic for primary care'),
            ('Diagnostic Center', 'DC',
             'Facility specialized in diagnostic services'),
        ]
        
        count = 0
        for name, code, description in facility_types_data:
            _, created = FacilityType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description
                }
            )
            if created:
                count += 1
        
        return count
