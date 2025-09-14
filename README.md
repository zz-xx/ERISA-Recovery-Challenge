# ERISA-Recovery-Challenge

**My submission for [Erisa Recovery Challenge 2025](https://www.erisachallenge.dev/).**

## Documentation and Setup

Please visit the project Github Pages [here](https://zz-xx.github.io/ERISA-Recovery-Challenge/).

## Live Version

A live version hosted on PythonAnywhere can be found [here](https://yashr.pythonanywhere.com/).

## Brief Challenge Requirements

Build a lightweight web application that mimics how insurance claims are analyzed at ERISA Recovery.

### Mandated Tech Stack

- Backend - Django
- Database - SQLite
- Frontend - HTML/CSS + HTMX
- Client-Side - Alpine.js
- UI - Pico CSS (Slate)

### Core Requirements

 - Data Ingestion into database from CSV/JSON claim records.

 - Claims List View to display all claims with ID, patient name, billed amount, paid amount, status, and insurer name

 - HTMX Detail View to show claim-specific information without full page reload.

 - Allow users to flag claims for review and add custom notes stored in database.

 - Search & Filter functionality for for claim status or insurer name.

Please visit documentation for more details including implementation of bonus features.

## Implementation

### Core Requirements Implemented

- CSV ingestion: Management command `python manage.py load_claim_data <claims_csv> <details_csv> --delimiter <char> [--mode append|overwrite]` loads claims + claim details, with sample CSVs in `src/data`. Overwrite mode purges existing claims (cascades details/notes). JSON ingestion is not implemented.
- Claims list view: Paginated (50/page) table showing ID, patient, billed, paid, status, insurer, with server-side sorting and filters.
- HTMX detail view: Clicking a row loads a claim detail `<tr>` after the row (partial) without full page reload.
- Flag + notes: Toggle “Flag for Review” (tracks `flagged_by`/`flagged_at`) and add per-claim notes; both update via HTMX partial swaps.
- Search & filter: Search on patient or insurer; filter by status; filter flagged-only.

### Bonus / Extra Features Implemented

- Authentication: Login/Logout plus a simple Register flow (`/register/`), then redirect to login.
- Sorting UX: Clickable header links with ascending/descending toggle and inline arrow indicators (custom tags `sort_url` and `sort_indicator`).
- Infinite scroll: Appends additional rows via HTMX when scrolled to the bottom.
- Theming: Light/Dark theme toggle using Alpine.js.
- UI: Pico CSS (Slate) for a clean, responsive interface.
- Logging: Rotating file logs at `logs/app.log` for ingestion summaries and app events.
- Admin: Django admin configured for Claims, ClaimDetails, and Notes.
- CSRF + HTMX: Base template injects CSRF header on non-GET HTMX requests.
- Docs: Sphinx docs (autodoc + viewcode) with GitHub Pages published.
