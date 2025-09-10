from django.contrib import admin

from .models import Claim, ClaimDetail, Note


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    """Admin configuration for the Claim model."""

    list_display = (
        "id",
        "patient_name",
        "insurer_name",
        "status",
        "billed_amount",
        "paid_amount",
        "is_flagged",
        "discharge_date",
        "updated_at",
    )
    list_filter = ("status", "is_flagged", "insurer_name")
    search_fields = ("patient_name", "insurer_name")
    ordering = ("-discharge_date",)


@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    """Admin configuration for the ClaimDetail model."""

    list_display = ("claim", "cpt_codes")
    search_fields = ("claim__patient_name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin configuration for the Note model."""

    list_display = ("claim", "user", "created_at")
    search_fields = ("claim__patient_name", "user__username")
    autocomplete_fields = ("claim", "user")
