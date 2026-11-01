# Testing Guide - Intelligent Medical System

## Overview

This document provides comprehensive testing instructions for the Intelligent Medical and Hospital Management System, focusing on the accounts and organizations modules.

## Prerequisites

Ensure you have completed the initial setup:

```powershell
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

## Database Setup

### 1. Create Migrations

```powershell
python manage.py makemigrations accounts
python manage.py makemigrations organizations
python manage.py makemigrations
```

### 2. Apply Migrations

```powershell
python manage.py migrate
```

### 3. Initialize System Data

Create default roles, permissions, and facility types:

```powershell
python manage.py init_system
```

### 4. Create Superuser

```powershell
python manage.py createsuperuser
```

When prompted, provide:
- Email: admin@example.com
- Username: admin
- Password: (your secure password)

## Running Tests

### Run All Tests

```powershell
python manage.py test
```

### Run Specific App Tests

```powershell
# Test accounts app
python manage.py test apps.accounts

# Test organizations app
python manage.py test apps.organizations
```

### Run Specific Test Files

```powershell
# Test accounts models
python manage.py test apps.accounts.tests.test_models

# Test accounts views
python manage.py test apps.accounts.tests.test_views

# Test accounts serializers
python manage.py test apps.accounts.tests.test_serializers

# Test organizations models
python manage.py test apps.organizations.tests.test_models
```

### Run Tests with Coverage

```powershell
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Run Tests with Verbosity

```powershell
# Verbose output (shows each test)
python manage.py test --verbosity=2

# Very verbose output (shows all test details)
python manage.py test --verbosity=3
```

## Manual Testing with Django Shell

### 1. Start Django Shell

```powershell
python manage.py shell
```

### 2. Test User Creation and Authentication

```python
from apps.accounts.models import User, Role, UserRole

# Create a user
user = User.objects.create_user(
    username='doctor1',
    email='doctor1@example.com',
    password='DoctorPass123!',
    first_name='John',
    last_name='Doe'
)

# Get doctor role
doctor_role = Role.objects.get(code='doctor')

# Assign role to user
UserRole.objects.create(
    user=user,
    role=doctor_role,
    granted_by=User.objects.get(is_superuser=True)
)

# Check if user has role
print(user.has_role('doctor'))  # Should print True

# Test authentication
from django.contrib.auth import authenticate
auth_user = authenticate(username='doctor1@example.com', password='DoctorPass123!')
print(auth_user)  # Should print the user object
```

### 3. Test Organization and Facility Creation

```python
from apps.organizations.models import Organization, FacilityType, Facility

# Create organization
org = Organization.objects.create(
    name='Test Hospital Group',
    code='THG001',
    email='info@testhospital.com',
    city='Addis Ababa',
    region='Addis Ababa'
)

# Get facility type
facility_type = FacilityType.objects.get(code='GH')

# Create facility
facility = Facility.objects.create(
    organization=org,
    facility_type=facility_type,
    name='Test General Hospital',
    code='TGH001',
    city='Addis Ababa',
    region='Addis Ababa',
    bed_capacity=200
)

print(f"Created facility: {facility}")
```

### 4. Test Account Locking

```python
from apps.accounts.models import User

user = User.objects.get(email='doctor1@example.com')

# Record failed login attempts
for i in range(5):
    user.record_failed_login()

# Check if account is locked
print(user.is_account_locked())  # Should print True

# Unlock account
user.unlock_account()
print(user.is_account_locked())  # Should print False
```

## API Testing with curl or Postman

### Start Development Server

```powershell
python manage.py runserver
```

### 1. Login

```powershell
curl -X POST http://localhost:8000/api/v1/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{\"username\": \"admin@example.com\", \"password\": \"your-password\"}'
```

Response includes access and refresh tokens.

### 2. Get Current User Profile

```powershell
curl http://localhost:8000/api/v1/accounts/users/me/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. List Users

```powershell
curl http://localhost:8000/api/v1/accounts/users/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. List Roles

```powershell
curl http://localhost:8000/api/v1/accounts/roles/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. List Facilities

```powershell
curl http://localhost:8000/api/v1/organizations/facilities/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Create a Facility

```powershell
curl -X POST http://localhost:8000/api/v1/organizations/facilities/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    \"organization\": \"ORGANIZATION_UUID\",
    \"facility_type\": \"FACILITY_TYPE_UUID\",
    \"name\": \"New Hospital\",
    \"code\": \"NH001\",
    \"city\": \"Addis Ababa\",
    \"bed_capacity\": 150
  }'
```

## Test Coverage Goals

- **Models**: 90%+ coverage
- **Views/ViewSets**: 85%+ coverage
- **Serializers**: 90%+ coverage
- **Utilities**: 95%+ coverage

## Common Test Scenarios

### Authentication Tests
- ✓ User creation with valid data
- ✓ Login with email and username
- ✓ Login with invalid credentials
- ✓ Account locking after failed attempts
- ✓ Password change
- ✓ Token refresh
- ✓ Logout

### Authorization Tests
- ✓ Role assignment
- ✓ Permission checking
- ✓ Role-based access control
- ✓ Facility-scoped permissions

### Organization Tests
- ✓ Organization creation
- ✓ Facility management
- ✓ Department hierarchy
- ✓ Ward occupancy tracking
- ✓ License validation

## Troubleshooting

### Database Errors

If you encounter database errors:

```powershell
# Reset database (development only!)
python manage.py flush --no-input
python manage.py migrate
python manage.py init_system
python manage.py createsuperuser
```

### Import Errors

If you encounter import errors:

```powershell
# Add current directory to Python path
$env:PYTHONPATH = "."
python manage.py test
```

### Permission Errors

If tests fail due to missing permissions:

```powershell
# Re-run system initialization
python manage.py init_system
```

## Continuous Integration

For CI/CD pipelines, use:

```powershell
# Run tests with no input prompts
python manage.py test --noinput --parallel

# With coverage
coverage run --source='.' manage.py test --noinput
coverage xml  # For CI reporting
```

## Next Steps

After successful testing:

1. Review test coverage reports
2. Add tests for edge cases
3. Implement integration tests
4. Set up automated testing in CI/CD
5. Proceed to implement remaining modules (patients, encounters, CDSS, etc.)

## Support

For issues or questions:
- Review test output for detailed error messages
- Check Django logs in logs/ directory
- Review API documentation at http://localhost:8000/api/docs/
- Consult the main README.md for setup instructions
