"""
Tests for organizations models.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.organizations.models import (
    Organization, FacilityType, Facility, Department, Ward
)


class OrganizationModelTest(TestCase):
    """Test Organization model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Hospital Group',
            code='THG001',
            email='info@testhospital.com',
            phone='+251911123456',
            city='Addis Ababa',
            region='Addis Ababa',
            country='Ethiopia'
        )
    
    def test_organization_creation(self):
        """Test organization creation."""
        self.assertEqual(self.organization.name, 'Test Hospital Group')
        self.assertEqual(self.organization.code, 'THG001')
        self.assertTrue(self.organization.is_active)
    
    def test_organization_str(self):
        """Test string representation."""
        self.assertEqual(str(self.organization), 'Test Hospital Group')


class FacilityTypeModelTest(TestCase):
    """Test FacilityType model."""
    
    def setUp(self):
        """Set up test data."""
        self.facility_type = FacilityType.objects.create(
            name='General Hospital',
            code='GH',
            description='Full-service general hospital'
        )
    
    def test_facility_type_creation(self):
        """Test facility type creation."""
        self.assertEqual(self.facility_type.name, 'General Hospital')
        self.assertEqual(self.facility_type.code, 'GH')
    
    def test_facility_type_str(self):
        """Test string representation."""
        self.assertEqual(str(self.facility_type), 'General Hospital')


class FacilityModelTest(TestCase):
    """Test Facility model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Hospital Group',
            code='THG001'
        )
        self.facility_type = FacilityType.objects.create(
            name='Hospital',
            code='HOSP'
        )
        self.facility = Facility.objects.create(
            organization=self.organization,
            facility_type=self.facility_type,
            name='Test General Hospital',
            code='TGH001',
            city='Addis Ababa',
            region='Addis Ababa',
            bed_capacity=200,
            license_number='LIC123456',
            license_issue_date=timezone.now().date(),
            license_expiry_date=timezone.now().date() + timedelta(days=365)
        )
    
    def test_facility_creation(self):
        """Test facility creation."""
        self.assertEqual(self.facility.name, 'Test General Hospital')
        self.assertEqual(self.facility.code, 'TGH001')
        self.assertEqual(self.facility.bed_capacity, 200)
        self.assertTrue(self.facility.is_active)
    
    def test_facility_str(self):
        """Test string representation."""
        self.assertEqual(str(self.facility), 'Test General Hospital (TGH001)')
    
    def test_license_validation(self):
        """Test license validation."""
        self.assertTrue(self.facility.is_license_valid())
        
        # Set expired license
        self.facility.license_expiry_date = timezone.now().date() - timedelta(days=1)
        self.facility.save()
        self.assertFalse(self.facility.is_license_valid())


class DepartmentModelTest(TestCase):
    """Test Department model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Hospital Group',
            code='THG001'
        )
        self.facility_type = FacilityType.objects.create(
            name='Hospital',
            code='HOSP'
        )
        self.facility = Facility.objects.create(
            organization=self.organization,
            facility_type=self.facility_type,
            name='Test Hospital',
            code='TH001'
        )
        self.user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='DoctorPass123!'
        )
        self.department = Department.objects.create(
            facility=self.facility,
            name='Emergency Department',
            code='ER',
            head_of_department=self.user,
            bed_count=50
        )
    
    def test_department_creation(self):
        """Test department creation."""
        self.assertEqual(self.department.name, 'Emergency Department')
        self.assertEqual(self.department.code, 'ER')
        self.assertEqual(self.department.bed_count, 50)
        self.assertTrue(self.department.is_active)
    
    def test_department_str(self):
        """Test string representation."""
        self.assertIn('Test Hospital', str(self.department))
        self.assertIn('Emergency Department', str(self.department))
    
    def test_department_hierarchy(self):
        """Test department hierarchy."""
        sub_department = Department.objects.create(
            facility=self.facility,
            name='Pediatric Emergency',
            code='PED-ER',
            parent_department=self.department
        )
        
        hierarchy = sub_department.get_full_hierarchy()
        self.assertIn('Emergency Department', hierarchy)
        self.assertIn('Pediatric Emergency', hierarchy)


class WardModelTest(TestCase):
    """Test Ward model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Hospital',
            code='TH001'
        )
        self.facility_type = FacilityType.objects.create(
            name='Hospital',
            code='HOSP'
        )
        self.facility = Facility.objects.create(
            organization=self.organization,
            facility_type=self.facility_type,
            name='Test Hospital',
            code='TH001'
        )
        self.department = Department.objects.create(
            facility=self.facility,
            name='Internal Medicine',
            code='IM'
        )
        self.ward = Ward.objects.create(
            department=self.department,
            name='General Ward A',
            code='GW-A',
            ward_type='general',
            bed_capacity=30,
            occupied_beds=20
        )
    
    def test_ward_creation(self):
        """Test ward creation."""
        self.assertEqual(self.ward.name, 'General Ward A')
        self.assertEqual(self.ward.bed_capacity, 30)
        self.assertEqual(self.ward.occupied_beds, 20)
        self.assertTrue(self.ward.is_active)
    
    def test_ward_str(self):
        """Test string representation."""
        self.assertIn('Internal Medicine', str(self.ward))
        self.assertIn('General Ward A', str(self.ward))
    
    def test_available_beds(self):
        """Test available beds calculation."""
        available = self.ward.get_available_beds()
        self.assertEqual(available, 10)
    
    def test_occupancy_rate(self):
        """Test occupancy rate calculation."""
        rate = self.ward.get_occupancy_rate()
        self.assertAlmostEqual(rate, 66.67, places=1)
    
    def test_full_occupancy(self):
        """Test full occupancy."""
        self.ward.occupied_beds = 30
        self.ward.save()
        
        self.assertEqual(self.ward.get_available_beds(), 0)
        self.assertEqual(self.ward.get_occupancy_rate(), 100.0)
