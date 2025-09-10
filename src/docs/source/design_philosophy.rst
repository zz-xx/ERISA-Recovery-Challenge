.. _design_philosophy:

Backend Design
==============

This document outlines the design philosophy and architectural choices made during the development of the ERISA Recovery Challenge backend. Idiomatic and maintainable code practices were used wherever possible while also keeping in mind project requirements. In the end, architectural choices are subjective. Personally, I tried taking inspiration from standard practices from Django documentation.

Mapping Requirements to Design Choices
--------------------------------------

The following section details how each core requirement of the challenge was implemented in the backend.

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Challenge Requirement
     - Backend Implementation
   * - **Data Ingestion**
     - A custom management command, ``load_claim_data``, was created. This command delegates the core logic to a dedicated ``ClaimDataIngestor`` service class in ``claims/services.py``. This separates one-off data loading tasks from the web application's request-response cycle. Encapsulating the logic in a service class makes it modular, reusable, and easy to unit test independently of the command-line interface.
   * - **Claims List View**
     - A Django class-based view, ``ClaimListView``, was used. It inherits from Django's built-in ``ListView`` to handle pagination and object listing automatically. Using Django's generic CBVs is a best practice that reduces boilerplate code and promotes reusability. The core logic is contained within the ``get_queryset`` method, which is the standard place to implement filtering and sorting.
   * - **HTMX Detail View**
     - The application uses separate, focused views that return HTML partials (e.g., ``ClaimDetailView``, ``ToggleFlagView``). The main ``ClaimListView`` also contains logic in its ``get_template_names`` method to serve different partials based on the nature of the HTMX request. This approach keeps views small and focused on a single task. It allows the frontend to dynamically update specific parts of the page, creating a responsive user experience without the complexity of a full JavaScript framework, as intended by the HTMX requirement.
   * - **Flag & Annotate**
     - A boolean field ``is_flagged`` was added to the ``Claim`` model. A separate ``Note`` model with a ``ForeignKey`` to ``Claim`` was created to store annotations. User actions are handled by dedicated views (``ToggleFlagView``, ``AddNoteView``) that process ``POST`` requests. This makes sure that notes are cleanly associated with claims.
   * - **Search & Filter**
     - All searching and filtering logic is implemented within the ``ClaimListView.get_queryset`` method. It uses Django's ORM features like ``.filter()`` and ``Q`` objects, to build database queries. Performing data filtering at the database level via the ORM is preferred way to do this. It avoids loading unnecessary data into memory and leverages the database engine's query optimizer which is made for this kind of tasks.
   * - **User Authentication**
     - Implemented the bonus feature. All notes in detail view now can be attributed to a specific user.

Testing & Documentation
-----------------------

* **Testing:** Test suite was developed using Django's built-in test framework, achieving 94% code coverage. The tests verify model integrity, service logic, and view responses.
* **Documentation:** Project documentation is generated using Sphinx. It includes auto-generated API documentation from code docstrings, a "Getting Started" guide, and this design overview.