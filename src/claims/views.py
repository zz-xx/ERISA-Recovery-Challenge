from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Claim
from typing import Any, Dict

from urllib.parse import urlencode

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

        if search_query:
            # Search by patient name or insurer name (case-insensitive)
            queryset = queryset.filter(
                Q(patient_name__icontains=search_query)
                | Q(insurer_name__icontains=search_query)
            )

        if status_filter:
            # Filter by status
            queryset = queryset.filter(status=status_filter.upper())
        
        # --- New Sorting Logic ---
        sort_by = self.request.GET.get('sort', 'id') # Default sort by 'id'
        direction = self.request.GET.get('dir', 'asc')  # Default direction 'asc'

        # Whitelist of fields we allow sorting on to prevent misuse
        allowed_sort_fields = [
            'id', 'patient_name', 'billed_amount', 'paid_amount', 
            'status', 'insurer_name', 'discharge_date'
        ]

        if sort_by in allowed_sort_fields:
            if direction == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds the claim status choices and current filter values to the context.
        """
        context = super().get_context_data(**kwargs)
        context['claim_statuses'] = Claim.ClaimStatus.choices
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        
        # --- New Sorting Context --- 
        current_sort = self.request.GET.get('sort', 'id')
        current_dir = self.request.GET.get('dir', 'asc')
        context['current_sort'] = current_sort
        context['current_dir'] = current_dir
        
        # Helper for the template to easily flip the direction
        context['next_dir'] = 'desc' if current_dir == 'asc' else 'asc'

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
