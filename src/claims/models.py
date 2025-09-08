from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Optional

from django.contrib.auth.models import User

# Create your models here.


class Claim(models.Model):
    """
    Represents a single insurance claim.
    """
    
    class ClaimStatus(models.TextChoices):
        PAID = 'PAID', 'Paid'
        DENIED = 'DENIED', 'Denied'
        UNDER_REVIEW = 'UNDER REVIEW', 'Under Review'

    id = models.IntegerField(primary_key=True, editable=False)
    # Add index for faster searching
    patient_name = models.CharField(max_length=255, db_index=True)
    billed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        db_index=True  # Add index for faster filtering
    )
    # Add index for faster searching
    insurer_name = models.CharField(max_length=255, db_index=True)
    discharge_date = models.DateField()
    is_flagged = models.BooleanField(default=False, help_text="Flag this claim for special review.") # Renamed for clarity
    
    # for keeping track of flags
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='flagged_claims')
    flagged_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Claim {self.id} for {self.patient_name}"

    @property
    def underpayment(self) -> Decimal:
        """Calculates the difference between billed and paid amounts."""
        return self.billed_amount - self.paid_amount


class ClaimDetail(models.Model):
    """
    Provides specific, detailed information related to a single claim.
    """

    claim = models.OneToOneField(
        Claim, on_delete=models.CASCADE, related_name="details"
    )
    cpt_codes = models.CharField(max_length=255, help_text="Comma-separated CPT codes.")
    denial_reason = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Details for Claim {self.claim.id}"


class Note(models.Model):
    """
    User-generated annotations or notes for a claim.
    """

    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # For user auth

    def __str__(self) -> str:
        note_preview: str = (
            (self.note[:75] + "...") if len(self.note) > 75 else self.note
        )
        return f"Note on {self.claim.id} at {self.created_at.strftime('%Y-%m-%d')}: {note_preview}"
