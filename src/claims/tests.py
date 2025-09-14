from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from pathlib import Path

from .models import Claim, ClaimDetail, Note
from .services import ClaimDataIngestor
from unittest.mock import patch, mock_open

class ClaimDataIngestorTests(TestCase):
    """
    Tests for the ClaimDataIngestor service.
    """

    def setUp(self):
        # Use simple strings. The mock doesn't care about the actual path,
        # only that the key used to create the mock matches the key used to look it up.
        self.dummy_claims_path = "dummy_claims.csv"
        self.dummy_details_path = "dummy_details.csv"

    def _run_ingestor_with_string_io(self, claims_csv_content: str, details_csv_content: str, *, mode: str = "append"):
        """Helper to run the ingestor with in-memory CSV data and a specific mode."""
        ingestor = ClaimDataIngestor(self.dummy_claims_path, self.dummy_details_path, mode=mode)

        # The keys for the mock_files dictionary MUST be Path objects,
        # because the service now uses Path objects internally to call open().
        mock_files = {
            Path(self.dummy_claims_path): mock_open(read_data=claims_csv_content).return_value,
            Path(self.dummy_details_path): mock_open(read_data=details_csv_content).return_value,
        }

        # The 'file' argument received here will be a Path object.
        with patch("builtins.open", lambda file, **kwargs: mock_files[file]):
            return ingestor.run()

    def test_successful_data_load(self):
        """Tests a clean, successful import of new data."""
        claim_id = 1
        claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},John Doe,1200.50,1000.00,PAID,Acme Insurance,2025-09-01"
        )
        details_csv = (
            "id,claim_id,cpt_codes,denial_reason\n"
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

    def test_overwrite_replaces_existing_data(self):
        """Re-running with overwrite should replace existing data (purge then load)."""
        claim_id = 1
        initial_claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Jane Smith,500.00,0.00,DENIED,Aetna,2025-08-15"
        )
        initial_details_csv = "id,claim_id,cpt_codes,denial_reason\n"

        self._run_ingestor_with_string_io(initial_claims_csv, initial_details_csv)
        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(Claim.objects.get(id=claim_id).status, "DENIED")

        updated_claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Jane Smith,500.00,500.00,PAID,CIGMA,2025-08-15"
        )

        summary, errors = self._run_ingestor_with_string_io(updated_claims_csv, initial_details_csv, mode="overwrite")

        self.assertEqual(len(errors), 0)
        self.assertEqual(summary["claims_updated"], 0)
        self.assertEqual(summary["claims_created"], 1)
        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(Claim.objects.get(id=claim_id).status, "PAID")
        self.assertEqual(Claim.objects.get(id=claim_id).paid_amount, Decimal("500.00"))

    def test_append_skips_existing_data(self):
        """Append mode should not modify existing records; it skips duplicates."""
        claim_id = 2
        claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Alpha,100.00,0.00,DENIED,Ins,2025-08-01"
        )
        details_csv = "id,claim_id,cpt_codes,denial_reason\n"

        # initial load creates one
        summary, errors = self._run_ingestor_with_string_io(claims_csv, details_csv, mode="append")
        self.assertEqual(len(errors), 0)
        self.assertEqual(summary["claims_created"], 1)

        # re-load same record in append mode: should skip
        summary2, errors2 = self._run_ingestor_with_string_io(claims_csv, details_csv, mode="append")
        self.assertEqual(len(errors2), 0)
        self.assertEqual(summary2.get("claims_skipped", 0), 1)

    def test_handles_bad_data_gracefully(self):
        """Tests that rows with errors are skipped and reported."""
        claim_id = 1
        claims_csv = (
            "id,patient_name,billed_amount,paid_amount,status,insurer_name,discharge_date\n"
            f"{claim_id},Kiryu Kazuma,100.00,50.00,PAID,CVS,2025-09-02\n"
            "bad-id,Majima Goro,not-a-decimal,50.00,PENDING,United,2025-09-03"
        )
        details_csv = "id,claim_id,cpt_codes,denial_reason\n"

        summary, errors = self._run_ingestor_with_string_io(claims_csv, details_csv)

        self.assertEqual(Claim.objects.count(), 1)
        self.assertEqual(summary["claims_created"], 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("invalid literal for int() with base 10: 'bad-id'", errors[0])

class ClaimsModelsTests(TestCase):
    """
    Tests for the models in the claims app.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.claim = Claim.objects.create(
            id=1,
            patient_name='John Doe',
            billed_amount=Decimal('1000.00'),
            paid_amount=Decimal('800.00'),
            status='PAID',
            insurer_name='Acme Insurance',
            discharge_date='2025-09-01'
        )
        self.claim_detail = ClaimDetail.objects.create(
            claim=self.claim,
            cpt_codes='99214,99215',
            denial_reason='Prior authorization required'
        )
        self.note = Note.objects.create(
            claim=self.claim,
            note='This is a test note.',
            user=self.user
        )

    def test_claim_str(self):
        self.assertEqual(str(self.claim), "Claim 1 for John Doe")

    def test_underpayment_property(self):
        self.assertEqual(self.claim.underpayment, Decimal('200.00'))

    def test_claim_detail_str(self):
        self.assertEqual(str(self.claim_detail), "Details for Claim 1")

    def test_note_str(self):
        self.assertIn("Note on 1", str(self.note))

class ClaimsViewsTests(TestCase):
    """
    Tests for the views in the claims app.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.claim1 = Claim.objects.create(
            id=1,
            patient_name='John Doe',
            billed_amount=Decimal('1000.00'),
            paid_amount=Decimal('800.00'),
            status='PAID',
            insurer_name='Acme Insurance',
            discharge_date='2025-09-01'
        )
        self.claim2 = Claim.objects.create(
            id=2,
            patient_name='Jane Smith',
            billed_amount=Decimal('2000.00'),
            paid_amount=Decimal('1500.00'),
            status='DENIED',
            insurer_name='Beta Insurance',
            discharge_date='2025-09-02',
            is_flagged=True
        )

    def test_claim_list_view(self):
        response = self.client.get(reverse('claims:claim-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")

    def test_claim_list_view_search(self):
        response = self.client.get(reverse('claims:claim-list') + '?search=Acme')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")

    def test_claim_list_view_filter_by_status(self):
        response = self.client.get(reverse('claims:claim-list') + '?status=DENIED')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")

    def test_claim_list_view_filter_by_flagged(self):
        response = self.client.get(reverse('claims:claim-list') + '?flagged=true')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")

    def test_claim_detail_view(self):
        response = self.client.get(reverse('claims:claim-detail', args=[self.claim1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")

    def test_toggle_flag_view(self):
        self.assertFalse(self.claim1.is_flagged)
        response = self.client.post(reverse('claims:toggle-flag', args=[self.claim1.id]))
        self.assertEqual(response.status_code, 200)
        self.claim1.refresh_from_db()
        self.assertTrue(self.claim1.is_flagged)

    def test_add_note_view(self):
        self.assertEqual(self.claim1.notes.count(), 0)
        response = self.client.post(reverse('claims:add-note', args=[self.claim1.id]), {'note': 'This is a new note.'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.claim1.notes.count(), 1)
        
class RegistrationFlowTests(TestCase):
    def test_register_with_weak_password_and_login(self):
        # GET register page
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)

        # POST weak password
        data = {
            'username': 'weakuser',
            'password1': '123',
            'password2': '123',
        }
        resp = self.client.post(reverse('register'), data)
        # should redirect to login
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('login'))

        # User exists and can login
        self.assertTrue(User.objects.filter(username='weakuser').exists())
        login_ok = self.client.login(username='weakuser', password='123')
        self.assertTrue(login_ok)
