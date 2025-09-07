from typing import Any, Dict
from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View

from .models import Claim, Note

# Create your views here.


class ClaimListView(ListView):
    """
    Displays a list of all claims in the Claims Dashboard.
    Supports searching by insurer name and filtering by status.
    """

    model = Claim
    template_name = "claims/claim_list.html"
    context_object_name = "claims"
    # paginate_by = 50

    def get_queryset(self):
        """
        Overrides the default queryset to implement search and filter functionality.
        """
        queryset = (
            super().get_queryset().select_related("details").order_by("-discharge_date")
        )

        # Get search/filter parameters from the URL
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        flagged_filter = self.request.GET.get("flagged", "") # Add this line

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
        if flagged_filter == 'true':
            queryset = queryset.filter(is_flagged=True)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds the claim status choices and current filter values to the context.
        """
        context = super().get_context_data(**kwargs)
        context['claim_statuses'] = Claim.ClaimStatus.choices
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_flagged'] = self.request.GET.get('flagged', '')

        return context
    

    def get_template_names(self):
        """
        If the request is from HTMX, return the partial template containing
        only the table rows. Otherwise, return the full template.
        """
        if self.request.htmx:
            return ["claims/partials/_claim_rows.html"]
        return ["claims/claim_list.html"]


class ClaimDetailView(DetailView):
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
        context['notes'] = self.object.notes.all().order_by('-created_at')
        return context


class ToggleFlagView(View):
    """Toggles the 'is_flagged' status of a claim."""

    def post(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        claim.is_flagged = not claim.is_flagged
        claim.save(update_fields=['is_flagged'])
        
        # Return the updated button template
        return render(request, 'claims/partials/_flag_button.html', {'claim': claim})


class AddNoteView(View):
    """Adds a new note to a claim."""

    def post(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        note_text = request.POST.get('note', '').strip()

        if note_text:
            Note.objects.create(claim=claim, note=note_text)
        
        # Return the updated notes list
        notes = claim.notes.all().order_by('-created_at')
        return render(request, 'claims/partials/_notes_section.html', {'notes': notes})
