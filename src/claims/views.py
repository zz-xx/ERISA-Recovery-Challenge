import logging
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from .models import Claim, Note

logger = logging.getLogger(__name__)


class ClaimListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all claims in the Claims Dashboard.

    This view supports:
    - Searching by insurer name and patient name.
    - Filtering by claim status and flagged status.
    - Sorting on multiple fields.
    - HTMX-powered partial updates for filtering, sorting, and infinite scroll.
    """

    model = Claim
    template_name = "claims/claim_list.html"
    context_object_name = "claims"
    paginate_by = 50

    def _apply_search_filter(self, queryset: QuerySet, search_query: str) -> QuerySet:
        """Applies a search filter to the queryset based on patient or insurer name."""
        if search_query:
            return queryset.filter(
                Q(patient_name__icontains=search_query)
                | Q(insurer_name__icontains=search_query)
            )
        return queryset

    def _apply_status_filter(self, queryset: QuerySet, status_filter: str) -> QuerySet:
        """Applies a filter for a specific claim status."""
        if status_filter:
            return queryset.filter(status=status_filter.upper())
        return queryset

    def _apply_flagged_filter(
        self, queryset: QuerySet, flagged_filter: str
    ) -> QuerySet:
        """Applies a filter to show only flagged claims."""
        if flagged_filter == "true":
            return queryset.filter(is_flagged=True)
        return queryset

    def _apply_sorting(self, queryset: QuerySet, sort_by: str) -> QuerySet:
        """Applies sorting to the queryset based on the provided field."""
        allowed_sort_fields = [
            "id",
            "patient_name",
            "billed_amount",
            "paid_amount",
            "status",
            "insurer_name",
            "discharge_date",
        ]
        # Fallback to a default sort order if the requested field is not allowed.
        sort_field = sort_by.lstrip("-")
        if sort_field not in allowed_sort_fields:
            sort_by = "-discharge_date"
        return queryset.order_by(sort_by)

    def get_queryset(self) -> QuerySet[Claim]:
        """
        Overrides the default queryset to implement search, filter, and sorting logic.
        """
        queryset = super().get_queryset().select_related("details")

        # Get search/filter parameters from the request URL.
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        flagged_filter = self.request.GET.get("flagged", "")
        sort_by = self.request.GET.get("sort", "id")  # Default sort.

        # Chain the filtering and sorting methods.
        queryset = self._apply_search_filter(queryset, search_query)
        queryset = self._apply_status_filter(queryset, status_filter)
        queryset = self._apply_flagged_filter(queryset, flagged_filter)
        queryset = self._apply_sorting(queryset, sort_by)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds filter and sorting values to the context for use in the template.
        """
        context = super().get_context_data(**kwargs)

        # Pass the request object to the template for the custom template tags.
        context["request"] = self.request

        # Provide current filter values to the template to repopulate controls.
        context["claim_statuses"] = Claim.ClaimStatus.choices
        context["current_search"] = self.request.GET.get("search", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_flagged"] = self.request.GET.get("flagged", "")

        # Provide current sort values to the template.
        sort_param = self.request.GET.get("sort", "-discharge_date")
        context["current_sort_param"] = sort_param
        context["current_sort_field"] = sort_param.lstrip("-")
        context["current_sort_dir"] = "desc" if sort_param.startswith("-") else "asc"

        return context

    def get_template_names(self) -> list[str]:
        """
        If the request is from HTMX, return the appropriate partial template.
        - For infinite scroll, return just the table rows.
        - For sorting/filtering, return the entire table body.
        """
        if self.request.htmx:
            if self.request.GET.get("_partial") == "rows":
                return ["claims/partials/_claim_rows.html"]
            return ["claims/partials/_claims_table.html"]
        return [self.template_name]


class ClaimDetailView(LoginRequiredMixin, DetailView):
    """
    Handles fetching and displaying the details for a single claim. This view
    is designed to be rendered within the main list view via an HTMX request,
    to avoid a full page reload.
    """

    model = Claim
    template_name = "claims/partials/_claim_detail.html"
    context_object_name = "claim"
    pk_url_kwarg = "claim_id"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Adds the claim's notes to the context, ordered by most recent first."""
        context = super().get_context_data(**kwargs)
        context["notes"] = self.object.notes.all().order_by("-created_at")
        return context


class ToggleFlagView(LoginRequiredMixin, View):
    """
    Handles POST requests to toggle the 'is_flagged' status of a claim.
    This view returns an HTML partial of the updated flag button and triggers
    an HTMX event to refresh the claim detail view if it's open.
    """

    def post(self, request: HttpRequest, claim_id: int) -> HttpResponse:
        claim = get_object_or_404(Claim, id=claim_id)
        claim.is_flagged = not claim.is_flagged

        if claim.is_flagged:
            claim.flagged_by = request.user
            claim.flagged_at = timezone.now()
        else:
            claim.flagged_by = None
            claim.flagged_at = None

        claim.save(update_fields=["is_flagged", "flagged_by", "flagged_at"])

        logger.info(
            f"User '{request.user.username}' (ID: {request.user.id}) "
            f"set is_flagged to {claim.is_flagged} for Claim ID {claim_id}."
        )

        # Render the button's HTML partial in response to the POST request.
        response = render(
            request, "claims/partials/_flag_button.html", {"claim": claim}
        )

        # Add a special HTMX header to broadcast an event with the claim's ID.
        # This allows other components on the page to react to the change.
        response["HX-Trigger"] = f"refresh-claim-detail-{claim_id}"

        return response


class AddNoteView(LoginRequiredMixin, View):
    """
    Handles POST requests to add a new note to a claim.
    Returns an HTML partial of the updated notes section.
    """

    def post(self, request: HttpRequest, claim_id: int) -> HttpResponse:
        claim = get_object_or_404(Claim, id=claim_id)
        note_text = request.POST.get("note", "").strip()

        if note_text:
            note = Note.objects.create(claim=claim, note=note_text, user=request.user)
            logger.info(
                f"User '{request.user.username}' (ID: {request.user.id}) "
                f"added Note ID {note.id} to Claim ID {claim_id}."
            )

        # Return the updated notes list, ordered by most recent first.
        notes = claim.notes.all().order_by("-created_at")
        return render(request, "claims/partials/_notes_section.html", {"notes": notes})
