#!/usr/bin/env python
"""
Setup script for Intelligent Medical and Hospital Management System.
Creates initial data, roles, and permissions.
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from apps.accounts.models import Role, Permission

User = get_user_model()


def create_roles():
    """Create default roles"""
    print("Creating roles...")
    
    roles_data = [
        {
            'name': 'System Administrator',
            'code': 'system_admin',
            'description': 'Full system access and configuration',
            'is_system_role': True
        },
        {
            'name': 'Hospital Administrator',
            'code': 'hospital_admin',
            'description': 'Hospital management and configuration',
            'is_system_role': True
        },
        {
            'name': 'Receptionist',
            'code': 'receptionist',
            'description': 'Patient registration and appointments',
            'is_system_role': True
        },
        {
            'name': 'Triage Nurse',
            'code': 'triage_nurse',
            'description': 'Initial assessment and triage',
            'is_system_role': True
        },
        {
            'name': 'Doctor',
            'code': 'doctor',
            'description': 'Clinical diagnosis and treatment',
            'is_system_role': True
        },
        {
            'name': 'Nurse',
            'code': 'nurse',
            'description': 'Nursing care and medication administration',
            'is_system_role': True
        },
        {
            'name': 'Pharmacist',
            'code': 'pharmacist',
            'description': 'Medication dispensing and pharmacy management',
            'is_system_role': True
        },
        {
            'name': 'Laboratory Staff',
            'code': 'lab_staff',
            'description': 'Laboratory tests and results',
            'is_system_role': True
        },
        {
            'name': 'Radiology Staff',
            'code': 'radiology_staff',
            'description': 'Imaging orders and reports',
            'is_system_role': True
        },
        {
            'name': 'Medical Knowledge Editor',
            'code': 'medical_editor',
            'description': 'Edit medical knowledge content',
            'is_system_role': True
        },
        {
            'name': 'Clinical Reviewer',
            'code': 'clinical_reviewer',
            'description': 'Review and approve medical content',
            'is_system_role': True
        },
        {
            'name': 'ML Governance Reviewer',
            'code': 'ml_reviewer',
            'description': 'Review and approve ML models',
            'is_system_role': True
        },
        {
            'name': 'Auditor',
            'code': 'auditor',
            'description': 'Access audit logs and compliance reports',
            'is_system_role': True
        },
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )
        if created:
            print(f"  ✓ Created role: {role.name}")
        else:
            print(f"  - Role already exists: {role.name}")


def create_superuser():
    """Create superuser if it doesn't exist"""
    print("\nCreating superuser...")
    
    username = input("Enter superuser username (default: admin): ").strip() or "admin"
    email = input("Enter superuser email (default: admin@example.com): ").strip() or "admin@example.com"
    
    if User.objects.filter(username=username).exists():
        print(f"  - User '{username}' already exists")
        return
    
    password = input("Enter superuser password: ").strip()
    if not password:
        print("  ! Password cannot be empty")
        return
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name="System",
        last_name="Administrator"
    )
    
    # Assign system admin role
    system_admin_role = Role.objects.get(code='system_admin')
    from apps.accounts.models import UserRole
    UserRole.objects.create(
        user=user,
        role=system_admin_role,
        granted_by=user
    )
    
    print(f"  ✓ Created superuser: {username}")


def main():
    """Main setup function"""
    print("=" * 60)
    print("Intelligent Medical and Hospital Management System")
    print("Initial Setup")
    print("=" * 60)
    print()
    
    try:
        with transaction.atomic():
            create_roles()
            create_superuser()
        
        print()
        print("=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Create organizations and facilities")
        print("3. Import medical knowledge data")
        print("4. Start the development server: python manage.py runserver")
        print()
        
    except Exception as e:
        print(f"\n! Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
