.. _url_endpoints:

URL Endpoint Reference
===============================

claims App Endpoints
------------------------

``/``


* **View:** ``ClaimListView``
* **URL Name:** ``claims:claim-list``
* **Method:** ``GET``
* **Description:** It renders the main claims table.
* **Query Parameters (Optional):**
    * ``search=<query>``: Filters the list to claims where the patient or insurer name contains the query string.
    * ``status=<STATUS>``: Filters the list to claims with a specific status (e.g., ``PAID``, ``DENIED``).
    * ``flagged=true``: Filters the list to show only claims that are flagged for review.
    * ``sort=<field>``: Sorts the list by the specified field. Prepending a hyphen (``-``) reverses the order (e.g., ``-billed_amount`` for descending). Allowed fields: ``id``, ``patient_name``, ``billed_amount``, ``paid_amount``, ``status``, ``insurer_name``, ``discharge_date``.
    * ``page=<number>``: Returns the specified page of results. The view is configured to show 50 claims per page.
* **HTMX Interaction:** When called with HTMX, this endpoint returns HTML partials instead of a full page:
    * If for sorting or filtering, it returns the updated table wrapper content (``claims/partials/_claims_table.html``) intended for ``#claims-table-wrapper``.
    * If the ``_partial=rows`` parameter is present (for infinite scroll), it returns only the next set of table rows (``claims/partials/_claim_rows.html``).

``/claim/<int:claim_id>/``


* **View:** ``ClaimDetailView``
* **URL Name:** ``claims:claim-detail``
* **Method:** ``GET``
* **Description:** Fetches and displays the detailed information for a single claim, including its associated CPT codes, denial reason, and user-submitted notes.
* **URL Parameters:**
    * ``claim_id`` (integer): The primary key of the ``Claim`` to display.
* **HTMX Interaction:** This endpoint is designed to be called via an HTMX ``GET`` request. It returns an HTML partial (``claims/partials/_claim_detail.html``) that is intended to be displayed on the main page without a full reload.

``/claim/<int:claim_id>/toggle-flag/``


* **View:** ``ToggleFlagView``
* **URL Name:** ``claims:toggle-flag``
* **Method:** ``POST``
* **Description:** Toggles the ``is_flagged`` status of a specific claim and records the user and timestamp of the action.
* **URL Parameters:**
    * ``claim_id`` (integer): The ID of the ``Claim`` to flag or unflag.
* **HTMX Interaction:** Called via an HTMX ``POST`` request. It returns an HTML partial of the updated flag button (``claims/partials/_flag_button.html``) and triggers a custom HTMX event (``refresh-claim-detail-<claim_id>``) to signal other components to refresh.

``/claim/<int:claim_id>/flag-button/``


* **View:** ``FlagButtonView``
* **URL Name:** ``claims:flag-button``
* **Method:** ``GET``
* **Description:** Returns the current flag button partial for the given claim without changing state. Used to refresh the list-row flag icon when a flag is toggled elsewhere.
* **HTMX Interaction:** Typically listens for ``refresh-claim-detail-<claim_id>`` and swaps the button HTML in-place.

``/claim/<int:claim_id>/add-note/``


* **View:** ``AddNoteView``
* **URL Name:** ``claims:add-note``
* **Method:** ``POST``
* **Description:** Creates a new ``Note`` associated with a specific claim.
* **URL Parameters:**
    * ``claim_id`` (integer): The ID of the ``Claim`` to which the note should be added.
* **Form Data:** Expects a ``note`` key in the POST body containing the text for the note.
* **HTMX Interaction:** Called via an HTMX ``POST`` request from the note submission form. It returns an HTML partial of the entire updated notes section (``claims/partials/_notes_section.html``).

---------------------------

Project-Level Endpoints
---------------------------

``/admin/``


* **View:** Django Admin Site
* **URL Name:** ``admin:*``
* **Methods:** ``GET``, ``POST``
* **Description:** The built-in Django administration interface. Requires superuser privileges.

``/login/``


* **View:** ``django.contrib.auth.views.LoginView``
* **URL Name:** ``login``
* **Methods:** ``GET``, ``POST``
* **Description:** Renders the login form (on GET) and handles user authentication (on POST).

``/logout/``


* **View:** ``django.contrib.auth.views.LogoutView``
* **URL Name:** ``logout``
* **Method:** ``GET`` or ``POST``
* **Description:** Logs out the currently authenticated user and redirects them to the login page.

``/register/``


* **View:** ``claims.views.RegisterView``
* **URL Name:** ``register``
* **Methods:** ``GET``, ``POST``
* **Description:** Renders a simple registration form and creates an account on POST. On success, redirects to the login page.
