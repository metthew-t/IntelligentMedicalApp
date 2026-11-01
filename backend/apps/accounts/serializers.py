"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Role, Permission, UserRole, LoginAttempt


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'profile_photo', 'language_preference',
            'timezone', 'is_active', 'is_staff', 'date_joined',
            'last_login', 'roles', 'facilities', 'mfa_enabled'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_roles(self, obj):
        roles = obj.get_roles()
        return [
            {
                'id': str(ur.role.id),
                'name': ur.role.name,
                'code': ur.role.code,
                'facility_id': str(ur.facility.id) if ur.facility else None,
                'facility_name': ur.facility.name if ur.facility else None,
            }
            for ur in roles
        ]
    
    def get_facilities(self, obj):
        facilities = obj.get_facilities()
        return [
            {
                'id': str(f.id),
                'name': f.name,
                'code': f.code,
            }
            for f in facilities
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'language_preference'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'profile_photo',
            'language_preference', 'timezone'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.must_change_password = False
        user.save(update_fields=['password', 'password_changed_at', 'must_change_password'])
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Try to get user by email or username
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Check if account is locked
        if user.is_account_locked():
            raise serializers.ValidationError(
                "Account is locked due to too many failed login attempts. Please try again later."
            )
        
        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        # Authenticate
        user = authenticate(
            request=self.context.get('request'),
            username=user.email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        
        attrs['user'] = user
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description', 'is_system_role',
            'created_at', 'permissions_count', 'users_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_permissions_count(self, obj):
        return obj.role_permissions.count()
    
    def get_users_count(self, obj):
        return obj.user_assignments.filter(is_active=True).count()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model."""
    
    class Meta:
        model = Permission
        fields = [
            'id', 'code', 'name', 'description',
            'resource_type', 'action', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True, default=None)
    granted_by_name = serializers.CharField(source='granted_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'role', 'role_name',
            'facility', 'facility_name', 'granted_by', 'granted_by_name',
            'granted_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'granted_at', 'granted_by']
        extra_kwargs = {
            'facility': {'required': False, 'allow_null': True},
        }
        validators = []  # Suppress auto UniqueTogetherValidator; handled in validate()
    
    def validate(self, attrs):
        # Check if role assignment already exists
        user = attrs.get('user')
        role = attrs.get('role')
        facility = attrs.get('facility')
        
        if self.instance is None:  # Creating new assignment
            if UserRole.objects.filter(
                user=user,
                role=role,
                facility=facility,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    "User already has this role for the specified facility."
                )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['granted_by'] = self.context['request'].user
        return super().create(validated_data)


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer for LoginAttempt model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'user', 'user_email', 'username', 'ip_address',
            'user_agent', 'success', 'failure_reason', 'attempted_at'
        ]
        read_only_fields = ['id', 'attempted_at']


from django.utils import timezone
