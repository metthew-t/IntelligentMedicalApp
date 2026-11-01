"""
Organization models for the Intelligent Medical System.
Includes healthcare facilities, departments, and organizational hierarchy.
"""
import uuid
from django.db import models
from apps.core.models import BaseModel


class Organization(BaseModel):
    """
    Top-level organization (e.g., hospital chain, health system).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Organization name")
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique organization code"
    )
    description = models.TextField(blank=True, help_text="Organization description")
    
    # Contact information
    email = models.EmailField(blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone")
    website = models.URLField(blank=True, help_text="Organization website")
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True, help_text="Region/State")
    country = models.CharField(max_length=100, default='Ethiopia')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Logo and branding
    logo = models.ImageField(
        upload_to='organization_logos/',
        blank=True,
        null=True,
        help_text="Organization logo"
    )
    
    class Meta:
        db_table = 'organizations_organization'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_facilities_count(self):
        """Get count of facilities in organization."""
        return self.facilities.filter(is_active=True).count()


class FacilityType(models.Model):
    """
    Types of healthcare facilities (Hospital, Clinic, Health Center, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organizations_facility_type'
        verbose_name = 'Facility Type'
        verbose_name_plural = 'Facility Types'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Facility(BaseModel):
    """
    Healthcare facility (hospital, clinic, health center).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='facilities',
        help_text="Parent organization"
    )
    facility_type = models.ForeignKey(
        FacilityType,
        on_delete=models.PROTECT,
        related_name='facilities',
        help_text="Type of facility"
    )
    
    # Basic information
    name = models.CharField(max_length=255, help_text="Facility name")
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique facility code"
    )
    description = models.TextField(blank=True, help_text="Facility description")
    
    # Contact information
    email = models.EmailField(blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone")
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Emergency contact number"
    )
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True, help_text="Region/State")
    woreda = models.CharField(max_length=100, blank=True, help_text="Woreda/District")
    kebele = models.CharField(max_length=100, blank=True, help_text="Kebele")
    country = models.CharField(max_length=100, default='Ethiopia')
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS latitude"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS longitude"
    )
    
    # Licensing and accreditation
    license_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Government license number"
    )
    license_issue_date = models.DateField(null=True, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    accreditation_level = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('level_1', 'Level 1'),
            ('level_2', 'Level 2'),
            ('level_3', 'Level 3'),
            ('level_4', 'Level 4'),
            ('level_5', 'Level 5'),
        ],
        help_text="Ethiopian facility accreditation level"
    )
    
    # Capacity
    bed_capacity = models.IntegerField(
        default=0,
        help_text="Total number of beds"
    )
    staff_count = models.IntegerField(
        default=0,
        help_text="Total staff count"
    )
    
    # Operating hours
    operating_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text="Operating hours by day of week"
    )
    is_24_7 = models.BooleanField(
        default=False,
        help_text="Facility operates 24/7"
    )
    
    # Services
    services_offered = models.JSONField(
        default=list,
        blank=True,
        help_text="List of medical services offered"
    )
    
    class Meta:
        db_table = 'organizations_facility'
        verbose_name = 'Facility'
        verbose_name_plural = 'Facilities'
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['facility_type']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_license_valid(self):
        """Check if facility license is valid."""
        if not self.license_expiry_date:
            return False
        from django.utils import timezone
        return self.license_expiry_date > timezone.now().date()


class Department(BaseModel):
    """
    Department within a facility (Emergency, Surgery, Pediatrics, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='departments',
        help_text="Facility this department belongs to"
    )
    
    # Basic information
    name = models.CharField(max_length=255, help_text="Department name")
    code = models.CharField(max_length=50, help_text="Department code")
    description = models.TextField(blank=True, help_text="Department description")
    
    # Hierarchy
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
        help_text="Parent department for hierarchical structure"
    )
    
    # Department head
    head_of_department = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_led',
        help_text="Current head of department"
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True, help_text="Phone extension")
    email = models.EmailField(blank=True)
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Physical location within facility"
    )
    
    # Capacity
    bed_count = models.IntegerField(default=0, help_text="Number of beds in department")
    staff_count = models.IntegerField(default=0, help_text="Number of staff")
    
    # Specialization
    specializations = models.JSONField(
        default=list,
        blank=True,
        help_text="Medical specializations offered"
    )
    
    class Meta:
        db_table = 'organizations_department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['facility', 'name']
        unique_together = ['facility', 'code']
        indexes = [
            models.Index(fields=['facility', 'is_active']),
            models.Index(fields=['parent_department']),
        ]
    
    def __str__(self):
        return f"{self.facility.name} - {self.name}"
    
    def get_full_hierarchy(self):
        """Get full department hierarchy path."""
        if self.parent_department:
            return f"{self.parent_department.get_full_hierarchy()} > {self.name}"
        return self.name


class Ward(BaseModel):
    """
    Ward within a department (ICU, General Ward, Private Rooms, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='wards',
        help_text="Department this ward belongs to"
    )
    
    # Basic information
    name = models.CharField(max_length=255, help_text="Ward name")
    code = models.CharField(max_length=50, help_text="Ward code")
    description = models.TextField(blank=True)
    
    # Ward type
    ward_type = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General Ward'),
            ('icu', 'Intensive Care Unit'),
            ('nicu', 'Neonatal ICU'),
            ('picu', 'Pediatric ICU'),
            ('private', 'Private Rooms'),
            ('semi_private', 'Semi-Private Rooms'),
            ('isolation', 'Isolation Ward'),
            ('emergency', 'Emergency'),
        ],
        default='general'
    )
    
    # Capacity
    bed_capacity = models.IntegerField(default=0, help_text="Total beds")
    occupied_beds = models.IntegerField(default=0, help_text="Currently occupied beds")
    
    # Location
    floor = models.CharField(max_length=10, blank=True, help_text="Floor number")
    building = models.CharField(max_length=100, blank=True, help_text="Building name/code")
    
    # Gender restriction
    gender_specific = models.CharField(
        max_length=10,
        choices=[
            ('mixed', 'Mixed'),
            ('male', 'Male Only'),
            ('female', 'Female Only'),
        ],
        default='mixed'
    )
    
    class Meta:
        db_table = 'organizations_ward'
        verbose_name = 'Ward'
        verbose_name_plural = 'Wards'
        ordering = ['department', 'name']
        unique_together = ['department', 'code']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
    
    def get_available_beds(self):
        """Get count of available beds."""
        return self.bed_capacity - self.occupied_beds
    
    def get_occupancy_rate(self):
        """Calculate occupancy rate as percentage."""
        if self.bed_capacity == 0:
            return 0
        return (self.occupied_beds / self.bed_capacity) * 100
