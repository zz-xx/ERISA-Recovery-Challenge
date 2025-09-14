.. _getting_started:

Getting Started Guide
=====================

These are steps required to set up the project, load the initial data, and run the test suite.

Prerequisites
-----------------

* Python 3.13+
* pip (Python package installer)
* A virtual environment tool

Project Setup
-----------------

1.  Clone the Repository

    First, clone the project repository to local machine.

    .. code-block:: bash

        git clone https://github.com/zz-xx/ERISA-Recovery-Challenge.git

2.  Create and Activate a Virtual Environment

    Create a virtual environment. ``venv`` was used in development since it's bundled with python but ``virtualenv`` can also be used.

    .. code-block:: bash

        # On Windows
        python -m venv env
        .\\env\\Scripts\\activate

        # On macOS/Linux
        python3 -m venv env
        source env/bin/activate

3.  Install Dependencies

    Make sure virtual environment is active. Then install all the required Python packages from the ``requirements.txt`` file.

    .. code-block:: bash

        pip install -r requirements.txt

Database Setup and Data Loading
-----------------------------------
0. Switch to project directory

    .. code-block:: bash

        cd src

1.  Run Database Migrations

    Before loading data, we need to create the database schema.

    .. code-block:: bash

        python manage.py makemigrations claims
    
    .. code-block:: bash

        python manage.py migrate

2.  Load Claim Data

    Use the custom ``load_claim_data`` command to populate the database from the CSV files. This command requires the paths to the claims and details files and supports ``--delimiter`` and ``--mode``.

    .. note::
        The sample data files use a pipe (``|``) as a delimiter.

    .. code-block:: bash

        python manage.py load_claim_data data/claim_list_data.csv data/claim_detail_data.csv --delimiter "|"

        python manage.py load_claim_data data/claim_list_data.csv data/claim_detail_data.csv --delimiter "|" --mode overwrite

    .. note::
        - ``append`` (default) only creates missing records and skips existing ones. Skipped counts are reported in the summary.
        - ``overwrite`` clears existing Claim data (cascades remove related details/notes), then inserts the rows from the CSVs.
        - On Windows PowerShell, escape the pipe delimiter as ``"`|"`` instead of ``"|"``.

    .. caution::
        Using ``--mode overwrite`` deletes all existing Claim rows and cascades to related ClaimDetail and Note records. Back up annotations/flags if you need to preserve them.

    Sample tiny CSVs for local testing are included at ``src/data/dummy`` using the ``|`` delimiter:

    .. code-block:: bash

        python manage.py load_claim_data data/dummy/dummy_claims.csv data/dummy/dummy_details.csv --delimiter "|"

        python manage.py load_claim_data data/dummy/dummy_claims.csv data/dummy/dummy_details.csv --delimiter "|" --mode overwrite

3.  Create a Superuser Account

    To log in to the application and the Django admin dashboard, create a superuser account. Follow the prompts to set a username, email, and password.

    .. code-block:: bash

        python manage.py createsuperuser

Running the Application
---------------------------

Once the setup is complete, run the local development server:

.. code-block:: bash

    python manage.py runserver

Access the application at `http://127.0.0.1:8000/`. Login with the username and password created in previous step.

Running the Test Suite
--------------------------

Run the test suite.

1.  Run Basic Tests

    This command runs all tests within the ``claims`` app and provides detailed output.

    .. code-block:: bash

        python manage.py test claims --verbosity=2

2.  Check Test Coverage

    To see total test coverage, use the ``coverage`` package.

    .. code-block:: bash

        # First, run the tests under coverage monitoring
        coverage run manage.py test claims

        # Then, generate a simple report in the terminal
        coverage report -m

        # Or, generate a detailed, interactive HTML report
        coverage html

    The HTML report ``index.html`` will be available in the ``src/htmlcov`` directory.
