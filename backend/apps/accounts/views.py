"""
Views for the accounts app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from django.db import transaction

from .models import User, Role, Permission, UserRole, LoginAttempt
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, LoginSerializer, RoleSerializer,
    PermissionSerializer, UserRoleSerializer, LoginAttemptSerializer
)
from apps.core.permissions import IsSystemAdmin, IsHospitalAdmin


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')


class LoginView(APIView):
    """User login endpoint."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            # Record failed login attempt
            username = request.data.get('username', '')
            LoginAttempt.objects.create(
                username=username,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                success=False,
                failure_reason=str(serializer.errors)
            )
            
            # Try to get user and record failed attempt
            try:
                user = User.objects.get(email=username)
                user.record_failed_login()
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username)
                    user.record_failed_login()
                except User.DoesNotExist:
                    pass
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        # Record successful login
        user.record_successful_login()
        
        # Create login attempt record
        LoginAttempt.objects.create(
            user=user,
            username=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=True
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'expires_in': 900,  # 15 minutes in seconds
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout endpoint."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    queryset = User.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'destroy']:
            return [IsSystemAdmin()]
        elif self.action in ['update', 'partial_update', 'list']:
            return [IsHospitalAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get user roles."""
        user = self.get_object()
        roles = user.get_roles()
        serializer = UserRoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assign role to user."""
        user = self.get_object()
        serializer = UserRoleSerializer(
            data={
                **request.data,
                'user': str(user.id)
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def lock_account(self, request, pk=None):
        """Lock user account."""
        user = self.get_object()
        duration = int(request.data.get('duration_minutes', 30))
        user.lock_account(duration)
        return Response(
            {'message': f'Account locked for {duration} minutes.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unlock_account(self, request, pk=None):
        """Unlock user account."""
        user = self.get_object()
        user.unlock_account()
        return Response(
            {'message': 'Account unlocked successfully.'},
            status=status.HTTP_200_OK
        )


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role model."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """System admins can create/update/delete roles."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSystemAdmin()]
        return [permissions.IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of system roles."""
        role = self.get_object()
        if role.is_system_role:
            return Response(
                {'error': 'Cannot delete system role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get role permissions."""
        role = self.get_object()
        permissions = Permission.objects.filter(
            permission_roles__role=role
        )
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Add permission to role."""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.role_permissions.get_or_create(
                role=role,
                permission=permission
            )
            return Response(
                {'message': 'Permission added successfully.'},
                status=status.HTTP_200_OK
            )
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Permission model (read-only)."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for UserRole model."""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsHospitalAdmin]
    
    def get_queryset(self):
        """Filter by query parameters."""
        queryset = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        role_id = self.request.query_params.get('role_id')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        facility_id = self.request.query_params.get('facility_id')
        if facility_id:
            queryset = queryset.filter(facility_id=facility_id)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class LoginAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LoginAttempt model (read-only for auditing)."""
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    permission_classes = [IsSystemAdmin]
    
    def get_queryset(self):
        """Filter by query parameters."""
        queryset = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        ip_address = self.request.query_params.get('ip_address')
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        return queryset
