from django.urls import path
from .views import (
    ClaimListView,
    ClaimDetailView,
    ToggleFlagView,
    AddNoteView,
    FlagButtonView,
)

app_name = "claims"

urlpatterns = [
    path("", ClaimListView.as_view(), name="claim-list"),
    path("claim/<int:claim_id>/", ClaimDetailView.as_view(), name="claim-detail"),
    path(
        "claim/<int:claim_id>/toggle-flag/",
        ToggleFlagView.as_view(),
        name="toggle-flag",
    ),
    path(
        "claim/<int:claim_id>/flag-button/",
        FlagButtonView.as_view(),
        name="flag-button",
    ),
    path("claim/<int:claim_id>/add-note/", AddNoteView.as_view(), name="add-note"),
]
