.. _template_reference:

Frontend: Template Reference
============================

Reference for the templates and HTMX partials used by the UI.

Core Layout
---------------

``base.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** This is the main site-wide layout template. All other full-page templates extend from it.
* **Features:**
    * Includes Pico CSS (Slate) via CDN.
    * Defines the main navigation bar, including the user's name and a logout button.
    * Contains a main content block (``{% block content %}``) that child templates populate.
    * Manages the light/dark theme toggle functionality using Alpine.js.
    * Injects the CSRF token into all non-GET HTMX requests for security.

Authentication
------------------

``registration/login.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Renders the user login form.
* **Extends:** ``base.html``
* **Features:**
    * Displays a standard username and password form.
    * Includes a CSRF token for security.
    * Shows form errors if the login attempt is unsuccessful.

Claims Application Templates
--------------------------------

``claims/claim_list.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** The main page of the application. It renders the full dashboard view, including the search/filter controls and the claims table.
* **Extends:** ``base.html``
* **Key Sections:**
    * **Filter Form:** A form with inputs for searching, filtering by status, and showing flagged claims. These controls use HTMX attributes (``hx-get``, ``hx-trigger``, ``hx-target``) to reload the claims table without a full page refresh.
    * **Claims Table:** The main table structure. The actual content of the table is included from a partial template (``_claims_table.html``).
    * **Claim Detail Rendering:** Clicking a claim row loads a detail ``<tr>`` after that row via HTMX (not a separate ``div`` container).

HTMX Partials
-----------------

These templates are not meant to be displayed on their own. They are loaded into other pages via HTMX requests.

``claims/partials/_claims_table.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Renders the entire body of the claims table, including the headers and all rows for the current page.
* **Loaded By:** The filter/sort controls in ``claim_list.html``.
* **HTMX Interaction:** When a user filters or sorts the list, an HTMX request is sent to the ``ClaimListView``, which returns this partial to replace the existing table content. It also includes the logic for the "infinite scroll".

``claims/partials/_claim_rows.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Renders only the ``<tr>`` (table row) elements for a set of claims.
* **Loaded By:** The "infinite scroll" trigger at the bottom of ``_claims_table.html``.
* **HTMX Interaction:** As the user scrolls to the bottom of the list, an HTMX request is made to fetch the next page of results. The backend returns this partial, which is appended to the end of the existing table.

``claims/partials/_claim_detail.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Displays all detailed information for a single claim, including CPT codes, denial reasons, and the notes section.
* **Loaded By:** Clicking on a claim row in the main table.
* **HTMX Interaction:** An HTMX ``GET`` request is sent to ``ClaimDetailView``. This partial is returned and loaded into the designated detail section on the main page.

``claims/partials/_notes_section.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Renders the list of notes for a claim and the form to add a new note.
* **Loaded By:** The ``_claim_detail.html`` partial initially, and then by itself after a new note is submitted.
* **HTMX Interaction:** When the "Add Note" form is submitted, an HTMX ``POST`` request is sent to ``AddNoteView``. The view processes the request and returns this partial, which replaces the existing notes section to show the newly added note.

``claims/partials/_flag_button.html``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Purpose:** Renders the "Flag for Review" button, showing the correct state (flagged or unflagged).
* **Loaded By:** The ``_claim_detail.html`` partial initially, and then by itself after the button is clicked.
* **HTMX Interaction:** When the button is clicked, an HTMX ``POST`` request is sent to ``ToggleFlagView``. The view toggles the claim's status and returns this partial, which replaces the button on the page with its new state.
