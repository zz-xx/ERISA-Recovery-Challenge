from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Claim
from typing import Any, Dict

# Create your views here.


class ClaimListView(ListView):
    """
    Displays a list of all claims in the Claims Dashboard.
    Supports searching by insurer name and filtering by status.
    """

    model = Claim
    template_name = "claims/claim_list.html"
    context_object_name = "claims"
    # paginate_by = 20

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

        if search_query:
            # Search by patient name or insurer name (case-insensitive)
            queryset = queryset.filter(
                Q(patient_name__icontains=search_query)
                | Q(insurer_name__icontains=search_query)
            )

        if status_filter:
            # Filter by status
            queryset = queryset.filter(status=status_filter.upper())

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds the claim status choices and current filter values to the context.
        """
        context = super().get_context_data(**kwargs)
        context["claim_statuses"] = Claim.ClaimStatus.choices
        context["current_search"] = self.request.GET.get("search", "")
        context["current_status"] = self.request.GET.get("status", "")
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
