from django.urls import path
from .views import ClaimListView, ClaimDetailView

app_name = "claims"

urlpatterns = [
    path("", ClaimListView.as_view(), name="claim-list"),
    # The <int:claim_id> part captures the claim's ID from the URL
    path("claim/<int:claim_id>/", ClaimDetailView.as_view(), name="claim-detail"),
]
