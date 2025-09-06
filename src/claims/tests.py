import io
import uuid
from decimal import Decimal
from pathlib import Path

from django.test import TestCase
from .models import Claim, ClaimDetail
from .services import ClaimDataIngestor

# Create your tests here.


class ClaimDataIngestorTests(TestCase):
    """
    Tests for the ClaimDataIngestor service.
    """

    def setUp(self):
        # Create some dummy file paths for the ingestor (they don't need to exist for these tests)
        self.dummy_claims_path = Path("dummy_claims.csv")
        self.dummy_details_path = Path("dummy_details.csv")

    def _run_ingestor_with_string_io(
        self, claims_csv_content: str, details_csv_content: str
    ):
        """Helper method to run the ingestor with in-memory CSV data."""
        ingestor = ClaimDataIngestor(self.dummy_claims_path, self.dummy_details_path)

        # We patch the open method inside the test to return our in-memory files
        from unittest.mock import patch, mock_open

        mock_files = {
            str(self.dummy_claims_path): mock_open(read_data=claims_csv_content),
            str(self.dummy_details_path): mock_open(read_data=details_csv_content),
        }

        # Convert the 'file' Path object to a string before dictionary lookup
        with patch("builtins.open", lambda file, **kwargs: mock_files[str(file)]()):
            return ingestor.run()

    def test_successful_data_load(self):
        """Tests a clean, successful import of new data."""
        claim_id = uuid.uuid4()
        claims_csv = (
            f"id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},John Doe,1200.50,1000.00,PENDING,Acme Insurance,2025-09-01"
        )
        # We wrap the CPT codes and the denial reason in quotes so the inner commas and spaces are treated as part of the value.
        details_csv = (
            f"id,claim_id,cpt_codes,denial_reason\n"
            f'1,{claim_id},"99214,99215","Prior authorization required"'
        )

        summary, errors = self._run_ingestor_with_string_io(claims_csv, details_csv)

        self.assertEqual(len(errors), 0)
        self.assertEqual(summary["claims_created"], 1)
        self.assertEqual(summary["details_created"], 1)
        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(ClaimDetail.objects.count(), 1)

        claim = Claim.objects.get(id=claim_id)
        self.assertEqual(claim.patient_name, "John Doe")
        self.assertEqual(claim.billed_amount, Decimal("1200.50"))
        self.assertIsNotNone(claim.details)
        self.assertEqual(claim.details.cpt_codes, "99214,99215")

    def test_update_existing_data(self):
        """Tests that re-running the import updates existing records instead of creating duplicates."""
        claim_id = uuid.uuid4()
        initial_claims_csv = (
            f"id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Jane Smith,500.00,0.00,DENIED,Aetna,2025-08-15"
        )
        initial_details_csv = "id,claim_id,cpt_codes,denial_reason\n"

        # First run
        self._run_ingestor_with_string_io(initial_claims_csv, initial_details_csv)
        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(Claim.objects.get(id=claim_id).status, "DENIED")

        # Second run with updated data
        updated_claims_csv = (
            f"id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Jane Smith,500.00,500.00,PAID,CIGMA,2025-08-15"
        )

        summary, errors = self._run_ingestor_with_string_io(
            updated_claims_csv, initial_details_csv
        )

        self.assertEqual(len(errors), 0)
        self.assertEqual(summary["claims_updated"], 1)
        self.assertEqual(summary["claims_created"], 0)
        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(Claim.objects.get(id=claim_id).status, "PAID")
        self.assertEqual(Claim.objects.get(id=claim_id).paid_amount, Decimal("500.00"))

    def test_handles_bad_data_gracefully(self):
        """Tests that rows with errors are skipped and reported."""
        claim_id = uuid.uuid4()
        claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Kiryu Kazuma,100.00,50.00,PENDING,CVS,2025-09-02\n"
            "bad-uuid,Majima Goro,not-a-decimal,50.00,PENDING,United,2025-09-03"
        )
        details_csv = "id,claim_id,cpt_codes,denial_reason\n"

        summary, errors = self._run_ingestor_with_string_io(claims_csv, details_csv)

        self.assertEqual(
            Claim.objects.count(), 1
        )  # Only the good record should be created
        self.assertEqual(summary["claims_created"], 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("badly formed hexadecimal UUID string", errors[0])
