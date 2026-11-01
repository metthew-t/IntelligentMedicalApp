"""
Tests for accounts models.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, Role, Permission, UserRole, LoginAttempt


class UserModelTest(TestCase):
    """Test User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('TestPass123!'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        self.assertEqual(self.user.get_full_name(), 'Test User')
    
    def test_account_locking(self):
        """Test account locking functionality."""
        self.assertFalse(self.user.is_account_locked())
        
        # Lock account
        self.user.lock_account(duration_minutes=30)
        self.assertTrue(self.user.is_account_locked())
        self.assertIsNotNone(self.user.locked_until)
        
        # Unlock account
        self.user.unlock_account()
        self.assertFalse(self.user.is_account_locked())
        self.assertIsNone(self.user.locked_until)
        self.assertEqual(self.user.failed_login_attempts, 0)
    
    def test_failed_login_attempts(self):
        """Test failed login attempt tracking."""
        self.assertEqual(self.user.failed_login_attempts, 0)
        
        # Record failed attempts
        for i in range(4):
            self.user.record_failed_login()
        
        self.assertEqual(self.user.failed_login_attempts, 4)
        self.assertFalse(self.user.is_account_locked())
        
        # 5th attempt should lock account
        self.user.record_failed_login()
        self.assertTrue(self.user.is_account_locked())
    
    def test_successful_login_resets_failed_attempts(self):
        """Test successful login resets failed attempts."""
        self.user.failed_login_attempts = 3
        self.user.save()
        
        self.user.record_successful_login()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNotNone(self.user.last_login)
        self.assertIsNotNone(self.user.last_activity)
    
    def test_update_activity(self):
        """Test update_activity method."""
        old_activity = self.user.last_activity
        self.user.update_activity()
        self.assertNotEqual(self.user.last_activity, old_activity)


class RoleModelTest(TestCase):
    """Test Role model."""
    
    def setUp(self):
        """Set up test data."""
        self.role = Role.objects.create(
            name='Doctor',
            code='doctor',
            description='Medical doctor role'
        )
    
    def test_role_creation(self):
        """Test role creation."""
        self.assertEqual(self.role.name, 'Doctor')
        self.assertEqual(self.role.code, 'doctor')
        self.assertFalse(self.role.is_system_role)
    
    def test_role_str(self):
        """Test string representation."""
        self.assertEqual(str(self.role), 'Doctor')


class PermissionModelTest(TestCase):
    """Test Permission model."""
    
    def setUp(self):
        """Set up test data."""
        self.permission = Permission.objects.create(
            code='patient:read',
            name='Read Patient Records',
            description='Permission to view patient records',
            resource_type='patient',
            action='read'
        )
    
    def test_permission_creation(self):
        """Test permission creation."""
        self.assertEqual(self.permission.code, 'patient:read')
        self.assertEqual(self.permission.resource_type, 'patient')
        self.assertEqual(self.permission.action, 'read')
    
    def test_permission_str(self):
        """Test string representation."""
        self.assertIn('patient:read', str(self.permission))


class UserRoleModelTest(TestCase):
    """Test UserRole model."""
    
    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='DoctorPass123!'
        )
        self.role = Role.objects.create(
            name='Doctor',
            code='doctor'
        )
    
    def test_user_role_creation(self):
        """Test user role assignment."""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            granted_by=self.admin
        )
        
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertEqual(user_role.granted_by, self.admin)
        self.assertTrue(user_role.is_active)
    
    def test_user_role_expiration(self):
        """Test user role expiration."""
        # Create expired role
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            granted_by=self.admin,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(user_role.is_expired())
    
    def test_user_has_role(self):
        """Test user has_role method."""
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            granted_by=self.admin
        )
        
        self.assertTrue(self.user.has_role('doctor'))
        self.assertFalse(self.user.has_role('admin'))


class LoginAttemptModelTest(TestCase):
    """Test LoginAttempt model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_login_attempt_creation(self):
        """Test login attempt creation."""
        attempt = LoginAttempt.objects.create(
            user=self.user,
            username='test@example.com',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        self.assertEqual(attempt.user, self.user)
        self.assertTrue(attempt.success)
        self.assertIsNotNone(attempt.attempted_at)
    
    def test_failed_login_attempt(self):
        """Test failed login attempt."""
        attempt = LoginAttempt.objects.create(
            username='test@example.com',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=False,
            failure_reason='Invalid credentials'
        )
        
        self.assertFalse(attempt.success)
        self.assertEqual(attempt.failure_reason, 'Invalid credentials')
