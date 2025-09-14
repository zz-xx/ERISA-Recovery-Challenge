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

### Required Core Features

 - Data Ingestion into database from CSV/JSON claim records.

 - Claims List View to display all claims with ID, patient name, billed amount, paid amount, status, and insurer name

 - HTMX Detail View to show claim-specific information without full page reload.

 - Allow users to flag claims for review and add custom notes stored in database.

 - Search & Filter functionality for for claim status or insurer name.

### Implemented Requirements

- **CSV ingestion**: Management command `python manage.py load_claim_data <claims_csv> <details_csv> --delimiter <char>` loads claims + claim details, with sample CSVs in `src/data`.
- **Claims list view**: Paginated (50/page) table showing ID, patient, billed, paid, status, insurer, with server-side sorting and filters.
- **HTMX detail view**: Clicking a row loads a claim detail `<tr>` after the row (partial) without full page reload.
- **Flag + notes**: Toggle “Flag for Review” (tracks `flagged_by`/`flagged_at`) and add per-claim notes; both updated via HTMX partial swaps.
- **Search & filter**: Search on patient or insurer; filter by status; filter flagged-only.

### Implemented Bonus / Extra Features

- **Authentication**: Login/Logout plus a simple Register flow (`/register/`).
- **CSV Ingestion (append/overwrite)**: `python manage.py load_claim_data <claims_csv> <details_csv> --delimiter <char> [--mode append|overwrite]` Overwrite mode purges existing claims. Append mode adds to existing records, skipping duplicate claim IDs. 
- **Sorting UX**: Clickable header links for ascending/descending order with inline arrow indicators (custom tags `sort_url` and `sort_indicator`).
- **Infinite scroll**: Appends additional rows via HTMX when scrolled to the bottom.
- **Theming**: Light/Dark theme toggle using Alpine.js.
- **Logging**: Rotating file logs at `logs/app.log`.
- **Admin**: Django admin configured for Claims, ClaimDetails, and Notes.
- **Sphinx Docs**:  Sphinx docs (autodoc + viewcode) with GitHub Pages published.

Please visit documentation for more info including implementation details.