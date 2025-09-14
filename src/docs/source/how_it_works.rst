.. _how_it_works:

How the Application Works
=========================

Typical User Session
---------------------------

**a. The Initial Page Load**

1.  The user navigates to the root URL (``/``).
2.  Django's URL resolver matches this path to the ``ClaimListView``.
3.  The ``ClaimListView`` fetches the first 50 claim records from the database.
4.  It then renders the main ``claim_list.html`` template. This template extends ``base.html`` to create the full page, and includes the ``_claims_table.html`` partial to render the initial set of data.
5.  The final, complete HTML page is sent to the user's browser.

**b. The User Clicks a Claim**

1.  The user clicks on a table row (e.g., Claim ID 101).
2.  HTMX intercepts this click. The ``<tr>`` element has an attribute like ``hx-get="/claim/101/"``.
3.  HTMX sends a ``GET`` request to ``/claim/101/`` in the background.
4.  Django's URL resolver matches this to the ``ClaimDetailView``.
5.  The view fetches the specific details for Claim 101, including its notes.
6.  It renders the ``_claim_detail.html`` partial without rendering a full page.
7.  This small snippet of HTML is sent back to the browser. HTMX then takes this snippet and inserts it as a detail table row (a new ``<tr>``) immediately after the clicked row — no full page reload.

**c. The User Flags the Claim**

1.  Inside the claim detail view, the user clicks the "Flag for Review" button.
2.  This button has HTMX attributes like ``hx-post="/claim/101/toggle-flag/"``.
3.  HTMX sends a ``POST`` request to that URL.
4.  Django's URL resolver routes this to the ``ToggleFlagView``.
5.  The view finds Claim 101, toggles its ``is_flagged`` status, and saves the change to the database.
6.  The view then renders the ``_flag_button.html`` partial with the button's new state.
7.  This tiny HTML snippet is sent back, and HTMX swaps the old button with the new one. The user sees the button change state immediately.

**d. The User Searches for "Aetna"**

1.  The user types "Aetna" into the search box and presses Enter.
2.  The search input has HTMX attributes: ``hx-get="/"``, ``hx-target="#claims-table-wrapper"``.
3.  HTMX sends a ``GET`` request to the root URL, but this time it includes the search query: ``/?search=Aetna``.
4.  This request goes back to the **same** ``ClaimListView`` as the initial page load.
5.  However, the view detects the ``search`` parameter in the URL. Its ``get_queryset`` method adds a ``.filter()`` clause to the database query, fetching only the claims matching "Aetna".
6.  The view also detects that this is an HTMX request, so it renders the ``_claims_table.html`` partial, not the full page.
7.  HTMX receives the updated table and replaces the content of the wrapper (``#claims-table-wrapper``) to show only the search results.
