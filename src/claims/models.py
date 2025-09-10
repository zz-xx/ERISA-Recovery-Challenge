from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Claim(models.Model):
    """
    Represents a single insurance claim, serving as the central record for all
    related financial and status information.
    """

    class ClaimStatus(models.TextChoices):
        """Defines the possible statuses for a claim."""

        PAID = "PAID", "Paid"
        DENIED = "DENIED", "Denied"
        UNDER_REVIEW = "UNDER REVIEW", "Under Review"

    id = models.IntegerField(primary_key=True, editable=False)
    patient_name = models.CharField(
        max_length=255, db_index=True, help_text="Full name of the patient."
    )
    billed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The amount originally billed to the insurer.",
    )
    paid_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="The amount paid by the insurer."
    )
    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        db_index=True,
        help_text="The current processing status of the claim.",
    )
    insurer_name = models.CharField(
        max_length=255, db_index=True, help_text="The name of the insurance company."
    )
    discharge_date = models.DateField()
    is_flagged = models.BooleanField(
        default=False, help_text="Mark this claim for special review or follow-up."
    )

    # Auditing fields for tracking who flagged a claim and when.
    flagged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flagged_claims",
        help_text="The user who flagged this claim.",
    )
    flagged_at = models.DateTimeField(
        null=True, blank=True, help_text="The timestamp when the claim was flagged."
    )

    # Timestamps for record creation and updates.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """String representation of the Claim model."""
        return f"Claim {self.id} for {self.patient_name}"

    @property
    def underpayment(self) -> Decimal:
        """
        Calculates the difference between the billed and paid amounts,
        representing the underpayment value.
        """
        return self.billed_amount - self.paid_amount


class ClaimDetail(models.Model):
    """
    Provides specific, detailed information related to a single claim,
    such as medical codes or denial reasons.
    """

    # A OneToOneField ensures that a claim can only have one detail record.
    claim = models.OneToOneField(
        Claim, on_delete=models.CASCADE, related_name="details"
    )
    cpt_codes = models.CharField(
        max_length=255,
        help_text="Comma-separated CPT (Current Procedural Terminology) codes.",
    )
    denial_reason = models.TextField(
        blank=True,
        null=True,
        help_text="The reason provided by the insurer for denying the claim.",
    )

    def __str__(self) -> str:
        """String representation of the ClaimDetail model."""
        return f"Details for Claim {self.claim.id}"


class Note(models.Model):
    """
    Stores user-generated annotations or notes for a specific claim,
    allowing for collaboration and record-keeping.
    """

    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField(help_text="The content of the note.")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The user who created this note.",
    )

    def __str__(self) -> str:
        """
        Provides a truncated preview of the note for display in the admin
        or other contexts.
        """
        note_preview: str = (
            (self.note[:75] + "...") if len(self.note) > 75 else self.note
        )
        return f"Note on {self.claim.id} at {self.created_at.strftime('%Y-%m-%d')}: {note_preview}"
