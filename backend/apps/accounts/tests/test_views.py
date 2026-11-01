"""
Tests for accounts views and API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role, Permission, UserRole


class LoginViewTest(TestCase):
    """Test login endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.url = reverse('login')
    
    def test_successful_login_with_email(self):
        """Test successful login with email."""
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_successful_login_with_username(self):
        """Test successful login with username."""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'test@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_locked_account(self):
        """Test login with locked account."""
        self.user.lock_account()
        
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_inactive_account(self):
        """Test login with inactive account."""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserViewSetTest(TestCase):
    """Test user viewset endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='UserPass123!'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_users(self):
        """Test listing users."""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_retrieve_user(self):
        """Test retrieving a specific user."""
        url = reverse('user-detail', args=[self.regular_user.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')
    
    def test_get_current_user_profile(self):
        """Test getting current user profile."""
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@example.com')
    
    def test_create_user(self):
        """Test creating a new user."""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPass123!',
            'password_confirm': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_create_user_password_mismatch(self):
        """Test creating user with mismatched passwords."""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPass123!',
            'password_confirm': 'DifferentPassword!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password(self):
        """Test changing password."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-change-password')
        data = {
            'old_password': 'UserPass123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password('NewPassword123!'))
    
    def test_lock_user_account(self):
        """Test locking user account."""
        url = reverse('user-lock-account', args=[self.regular_user.id])
        response = self.client.post(url, {'duration_minutes': 30})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_account_locked())
    
    def test_unlock_user_account(self):
        """Test unlocking user account."""
        self.regular_user.lock_account()
        
        url = reverse('user-unlock-account', args=[self.regular_user.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_account_locked())


class RoleViewSetTest(TestCase):
    """Test role viewset endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.role = Role.objects.create(
            name='Doctor',
            code='doctor',
            description='Medical doctor role'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_roles(self):
        """Test listing roles."""
        url = reverse('role-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_role(self):
        """Test creating a new role."""
        url = reverse('role-list')
        data = {
            'name': 'Nurse',
            'code': 'nurse',
            'description': 'Registered nurse role'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(code='nurse').exists())
    
    def test_cannot_delete_system_role(self):
        """Test that system roles cannot be deleted."""
        system_role = Role.objects.create(
            name='System Admin',
            code='system_admin',
            is_system_role=True
        )
        
        url = reverse('role-detail', args=[system_role.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Role.objects.filter(id=system_role.id).exists())


class PermissionViewSetTest(TestCase):
    """Test permission viewset endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.permission = Permission.objects.create(
            code='patient:read',
            name='Read Patient Records',
            resource_type='patient',
            action='read'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_permissions(self):
        """Test listing permissions."""
        url = reverse('permission-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_permission(self):
        """Test retrieving a specific permission."""
        url = reverse('permission-detail', args=[self.permission.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'patient:read')


class UserRoleViewSetTest(TestCase):
    """Test user role assignment endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='UserPass123!'
        )
        self.role = Role.objects.create(
            name='Doctor',
            code='doctor'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_assign_role_to_user(self):
        """Test assigning role to user."""
        url = reverse('user-role-list')
        data = {
            'user': str(self.user.id),
            'role': str(self.role.id)
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserRole.objects.filter(
            user=self.user,
            role=self.role
        ).exists())
    
    def test_list_user_roles(self):
        """Test listing user role assignments."""
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            granted_by=self.admin_user
        )
        
        url = reverse('user-role-list')
        response = self.client.get(url, {'user_id': self.user.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
