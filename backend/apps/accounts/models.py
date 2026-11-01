"""
User and authentication models for the Intelligent Medical System.
"""
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses UUID as primary key and email for authentication.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address for login and communication"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Contact phone number"
    )
    
    # Profile information
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        help_text="User profile photo"
    )
    language_preference = models.CharField(
        max_length=10,
        default='en',
        choices=[
            ('en', 'English'),
            ('am', 'Amharic'),
            ('om', 'Afaan Oromo'),
        ],
        help_text="Preferred language"
    )
    timezone = models.CharField(
        max_length=50,
        default='Africa/Addis_Ababa',
        help_text="User timezone"
    )
    
    # Security
    must_change_password = models.BooleanField(
        default=False,
        help_text="User must change password on next login"
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last password change timestamp"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time"
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last user activity timestamp"
    )
    
    # MFA
    mfa_enabled = models.BooleanField(
        default=False,
        help_text="Multi-factor authentication enabled"
    )
    mfa_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="MFA secret key"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_role(self, role_code):
        """Check if user has a specific role. Superusers implicitly have all roles."""
        if self.is_superuser:
            return True
        return self.user_roles.filter(
            role__code=role_code,
            is_active=True
        ).exists()
    
    def get_facilities(self):
        """Get all facilities user has access to."""
        from apps.organizations.models import Facility
        facility_ids = self.user_roles.filter(
            is_active=True,
            facility__isnull=False
        ).values_list('facility_id', flat=True)
        return Facility.objects.filter(id__in=facility_ids, is_active=True)
    
    def get_roles(self):
        """Get all active roles for user."""
        return self.user_roles.filter(is_active=True).select_related('role')
    
    def is_account_locked(self):
        """Check if account is locked."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration."""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """Unlock account."""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def record_failed_login(self):
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        self.save(update_fields=['failed_login_attempts'])
    
    def record_successful_login(self):
        """Record a successful login."""
        self.failed_login_attempts = 0
        self.last_login = timezone.now()
        self.last_activity = timezone.now()
        self.save(update_fields=['failed_login_attempts', 'last_login', 'last_activity'])
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class Role(models.Model):
    """
    Role model for role-based access control.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name of the role"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for the role"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of role responsibilities"
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text="System role cannot be deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """
    Permission model for granular access control.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique permission code (e.g., patient:read)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Display name of the permission"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this permission allows"
    )
    resource_type = models.CharField(
        max_length=50,
        help_text="Resource this permission applies to"
    )
    action = models.CharField(
        max_length=50,
        help_text="Action allowed (e.g., read, write, delete)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['resource_type', 'action']
        indexes = [
            models.Index(fields=['resource_type', 'action']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class RolePermission(models.Model):
    """
    Many-to-many relationship between roles and permissions.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_role_permission'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.code}"


class UserRole(models.Model):
    """
    Many-to-many relationship between users and roles with additional context.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    facility = models.ForeignKey(
        'organizations.Facility',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_roles',
        help_text="Facility this role assignment applies to"
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='roles_granted'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiration date for temporary roles"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_user_role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = ['user', 'role', 'facility']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['facility']),
        ]
    
    def __str__(self):
        facility_str = f" at {self.facility.name}" if self.facility else ""
        return f"{self.user.get_full_name()} - {self.role.name}{facility_str}"
    
    def is_expired(self):
        """Check if role assignment has expired."""
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False
    
    def save(self, *args, **kwargs):
        """Override save to check expiration."""
        if self.is_expired():
            self.is_active = False
        super().save(*args, **kwargs)


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='login_attempts'
    )
    username = models.CharField(
        max_length=150,
        help_text="Username or email used for login attempt"
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for failed login"
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_login_attempt'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
            models.Index(fields=['success', '-attempted_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} at {self.attempted_at}"
