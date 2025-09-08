from typing import Any, Dict
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from .models import Claim, Note

# Create your views here.


class ClaimListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all claims in the Claims Dashboard.
    Supports searching by insurer name and filtering by status.
    """

    model = Claim
    template_name = "claims/claim_list.html"
    context_object_name = "claims"
    paginate_by = 50

    def get_queryset(self):
        """
        Overrides the default queryset to implement search and filter functionality.
        """
        # 
        queryset = super().get_queryset().select_related("details")

        # Get search/filter parameters from the URL
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        flagged_filter = self.request.GET.get("flagged", "")
        
        # Get sorting parameters from the URL
        sort_by = self.request.GET.get("sort", "id") # Default sort
        
        # Whitelist of fields that can be sorted
        allowed_sort_fields = ['id', 'patient_name', 'billed_amount', 'paid_amount', 'status', 'insurer_name', 'discharge_date']
        
        # Validate the sort_by parameter
        sort_field = sort_by.lstrip('-')
        if sort_field not in allowed_sort_fields:
            sort_by = '-discharge_date' # Fallback to default if invalid

        queryset = queryset.order_by(sort_by)

        if search_query:
            # Search by patient name or insurer name (case-insensitive)
            queryset = queryset.filter(
                Q(patient_name__icontains=search_query)
                | Q(insurer_name__icontains=search_query)
            )

        if status_filter:
            # Filter by status
            queryset = queryset.filter(status=status_filter.upper())

        # filter by flagged status
        if flagged_filter == "true":
            queryset = queryset.filter(is_flagged=True)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds filter and sorting values to the context for use in the template.
        """
        context = super().get_context_data(**kwargs)
        
        # 
        context['request'] = self.request

        # Current filter values
        context['claim_statuses'] = Claim.ClaimStatus.choices
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_flagged'] = self.request.GET.get('flagged', '')
        
        # Current sort values
        sort_param = self.request.GET.get("sort", "id")
        context['current_sort_param'] = sort_param
        context['current_sort_field'] = sort_param.lstrip('-')
        context['current_sort_dir'] = 'desc' if sort_param.startswith('-') else 'asc'

        return context

    def get_template_names(self):
        """
        If the request is from HTMX, return the correct partial.
        - For infinite scroll, return just the rows.
        - For sorting/filtering, return the entire table.
        """
        if self.request.htmx:
            # Check for our custom parameter to identify an infinite scroll request
            if self.request.GET.get('_partial') == 'rows':
                return ["claims/partials/_claim_rows.html"]
            # Otherwise, it's a sort or filter, so return the whole table
            return ["claims/partials/_claims_table.html"]
        return ["claims/claim_list.html"]


class ClaimDetailView(LoginRequiredMixin, DetailView):
    """
    Handles fetching and displaying the details for a single claim.
    This view is designed to be called via an HTMX request.
    """

    model = Claim
    template_name = "claims/partials/_claim_detail.html"
    context_object_name = "claim"
    pk_url_kwarg = "claim_id"  # Tells DetailView to look for 'claim_id' from the URL

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Adds the claim's notes to the context."""
        context = super().get_context_data(**kwargs)
        # Order notes by most recent first
        context["notes"] = self.object.notes.all().order_by("-created_at")
        return context


class ToggleFlagView(LoginRequiredMixin, View):
    """Toggles the 'is_flagged' status of a claim."""

    def post(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        claim.is_flagged = not claim.is_flagged

        # track user and timestamp
        if claim.is_flagged:
            # If the claim is now flagged, record who and when
            claim.flagged_by = request.user
            claim.flagged_at = timezone.now()
        else:
            # If the flag is removed, clear the fields
            claim.flagged_by = None
            claim.flagged_at = None
        
        claim.save(update_fields=["is_flagged", "flagged_by", "flagged_at"])
        
        # Render the button template 
        response = render(request, "claims/partials/_flag_button.html", {"claim": claim})
        
        # Add a special header that broadcasts an event with the claim's ID.
        response['HX-Trigger'] = f'refresh-claim-detail-{claim_id}'
        
        return response


class AddNoteView(LoginRequiredMixin, View):
    """Adds a new note to a claim."""

    def post(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        note_text = request.POST.get("note", "").strip()

        if note_text:
            # update to include user
            Note.objects.create(claim=claim, note=note_text, user=request.user)

        # Return the updated notes list
        notes = claim.notes.all().order_by("-created_at")
        return render(request, "claims/partials/_notes_section.html", {"notes": notes})
