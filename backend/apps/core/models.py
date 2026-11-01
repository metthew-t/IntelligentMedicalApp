"""
Base models for the Intelligent Medical System.
All models should inherit from these base classes.
"""
import uuid
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    Provides UUID primary key, timestamps, and audit fields.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        null=True,
        blank=True,
        help_text="User who created this record"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
        null=True,
        blank=True,
        help_text="User who last updated this record"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this record is active"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self, user):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.updated_by = user
        self.save(update_fields=['is_active', 'updated_by', 'updated_at'])

    def restore(self, user):
        """Restore a soft-deleted record"""
        self.is_active = True
        self.updated_by = user
        self.save(update_fields=['is_active', 'updated_by', 'updated_at'])


class VersionedContentModel(BaseModel):
    """
    Abstract model for versioned medical content.
    Used for diseases, symptoms, medicines, and other knowledge base content.
    """
    
    class ContentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        IN_REVIEW = 'in_review', 'In Review'
        APPROVED = 'approved', 'Approved'
        ACTIVE = 'active', 'Active'
        SUPERSEDED = 'superseded', 'Superseded'
        RETIRED = 'retired', 'Retired'
    
    version = models.IntegerField(
        default=1,
        help_text="Version number of this content"
    )
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.DRAFT,
        help_text="Current status of this content"
    )
    
    # Review and approval
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_reviewed',
        null=True,
        blank=True,
        help_text="User who reviewed this content"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this content was reviewed"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_approved',
        null=True,
        blank=True,
        help_text="User who approved this content"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this content was approved"
    )
    
    # Version chain
    superseded_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_versions',
        help_text="Newer version that supersedes this content"
    )

    class Meta:
        abstract = True

    def submit_for_review(self, user):
        """Submit content for review"""
        self.status = self.ContentStatus.IN_REVIEW
        self.updated_by = user
        self.save(update_fields=['status', 'updated_by', 'updated_at'])

    def approve_content(self, approver):
        """Approve content for use"""
        from django.utils import timezone
        self.status = self.ContentStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])

    def activate_content(self, user):
        """Activate approved content"""
        if self.status != self.ContentStatus.APPROVED:
            raise ValueError("Content must be approved before activation")
        self.status = self.ContentStatus.ACTIVE
        self.updated_by = user
        self.save(update_fields=['status', 'updated_by', 'updated_at'])

    def supersede(self, new_version, user):
        """Mark this version as superseded"""
        self.status = self.ContentStatus.SUPERSEDED
        self.superseded_by = new_version
        self.updated_by = user
        self.save(update_fields=['status', 'superseded_by', 'updated_by', 'updated_at'])


class FacilityScopedModel(BaseModel):
    """
    Abstract model for data that is scoped to a specific facility.
    Provides facility-level data isolation.
    """
    facility = models.ForeignKey(
        'organizations.Facility',
        on_delete=models.PROTECT,
        related_name='%(class)s_records',
        help_text="Facility this record belongs to"
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['facility', '-created_at']),
        ]


class TimeStampedModel(models.Model):
    """
    Simple timestamped model without audit fields.
    Use for models that don't need full audit trail.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
