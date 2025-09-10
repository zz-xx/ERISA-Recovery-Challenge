.. _getting_started:

Getting Started Guide
=====================

This guide will walk you through the steps required to set up the project, load the initial data, and run the test suite.

Prerequisites
-------------

* Python 3.8+
* Pip (Python package installer)
* A virtual environment tool (e.g., ``venv``, ``virtualenv``)

Project Setup
-------------

1.  **Clone the Repository**

    First, clone the project repository to your local machine.

2.  **Create and Activate a Virtual Environment**

    Navigate into the project's ``src`` directory and create a virtual environment.

    .. code-block:: bash

        # On Windows
        python -m venv env
        .\\env\\Scripts\\activate

        # On macOS/Linux
        python3 -m venv env
        source env/bin/activate

3.  **Install Dependencies**

    Install all the required Python packages from the ``requirements.txt`` file.

    .. code-block:: bash

        pip install -r requirements.txt

Database Setup and Data Loading
-------------------------------

1.  **Run Database Migrations**

    Before you can load data, you need to create the database schema. The ``migrate`` command applies all the necessary database changes.

    .. code-block:: bash

        python manage.py migrate

2.  **Load the Initial Claim Data**

    Use the custom ``load_claim_data`` command to populate the database from the provided CSV files. This command requires the paths to the claims and details files and an optional ``--delimiter``.

    .. note::
        The sample data files use a pipe (``|``) as a delimiter.

    .. code-block:: bash

        python manage.py load_claim_data data/claim_list_data.csv data/claim_detail_data.csv --delimiter "|"

3.  **Create a Superuser Account**

    To log in to the application and the Django admin area, you must create a superuser account. Follow the prompts to set a username, email, and password.

    .. code-block:: bash

        python manage.py createsuperuser

Running the Application
-----------------------

Once the setup is complete, you can run the local development server:

.. code-block:: bash

    python manage.py runserver

You can now access the application at `http://127.0.0.1:8000/`. Login with the username and password created in previous step.

Running the Test Suite
----------------------

To verify that everything is working correctly, you can run the automated test suite.

1.  **Run Basic Tests**

    This command runs all tests within the ``claims`` app and provides detailed output.

    .. code-block:: bash

        python manage.py test claims --verbosity=2

2.  **Check Test Coverage**

    To see which lines of code are covered by the tests, use the ``coverage`` package.

    .. code-block:: bash

        # First, run the tests under coverage monitoring
        coverage run manage.py test claims

        # Then, generate a simple report in the terminal
        coverage report -m

        # Or, generate a detailed, interactive HTML report
        coverage html

    The HTML report will be available in the ``src/htmlcov`` directory. Open the ``index.html`` file to explore it.
