"""
Tests for accounts serializers.
"""
from django.test import TestCase
from apps.accounts.models import User, Role, Permission
from apps.accounts.serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    RoleSerializer, PermissionSerializer
)


class UserSerializerTest(TestCase):
    """Test UserSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_serialization(self):
        """Test user serialization."""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['full_name'], 'Test User')
        self.assertIn('roles', data)
        self.assertIn('facilities', data)
        self.assertNotIn('password', data)


class UserCreateSerializerTest(TestCase):
    """Test UserCreateSerializer."""
    
    def test_valid_user_creation(self):
        """Test creating user with valid data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewSecurePass1!',
            'password_confirm': 'NewSecurePass1!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('NewSecurePass1!'))
    
    def test_password_mismatch(self):
        """Test validation fails with password mismatch."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewSecurePass1!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class LoginSerializerTest(TestCase):
    """Test LoginSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_valid_login(self):
        """Test login with valid credentials."""
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123!'
        }
        serializer = LoginSerializer(data=data, context={})
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'test@example.com',
            'password': 'WrongPassword!'
        }
        serializer = LoginSerializer(data=data, context={})
        
        self.assertFalse(serializer.is_valid())


class RoleSerializerTest(TestCase):
    """Test RoleSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.role = Role.objects.create(
            name='Doctor',
            code='doctor',
            description='Medical doctor role'
        )
    
    def test_role_serialization(self):
        """Test role serialization."""
        serializer = RoleSerializer(self.role)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Doctor')
        self.assertEqual(data['code'], 'doctor')
        self.assertIn('permissions_count', data)
        self.assertIn('users_count', data)


class PermissionSerializerTest(TestCase):
    """Test PermissionSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.permission = Permission.objects.create(
            code='patient:read',
            name='Read Patient Records',
            resource_type='patient',
            action='read'
        )
    
    def test_permission_serialization(self):
        """Test permission serialization."""
        serializer = PermissionSerializer(self.permission)
        data = serializer.data
        
        self.assertEqual(data['code'], 'patient:read')
        self.assertEqual(data['resource_type'], 'patient')
        self.assertEqual(data['action'], 'read')
