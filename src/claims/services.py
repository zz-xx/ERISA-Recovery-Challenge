import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, List
import uuid

from django.db import transaction
from .models import Claim, ClaimDetail

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, List
import uuid

from django.db import transaction
from .models import Claim, ClaimDetail

# A type alias for our summary dictionary
LoadSummary = Dict[str, int]


class ClaimDataIngestor:
    """
    A service class to handle the ingestion of claim data from CSV files.
    """

    # --- MODIFICATION 1: Add delimiter to the constructor ---
    def __init__(
        self, claims_csv_path: Path, details_csv_path: Path, delimiter: str = ","
    ):
        self.claims_csv_path = claims_csv_path
        self.details_csv_path = details_csv_path
        self.delimiter = delimiter  # Store the delimiter
        self.claims_created = 0
        self.claims_updated = 0
        self.details_created = 0
        self.details_updated = 0
        self.errors: List[str] = []

    def _log_error(self, row_num: int, file_name: str, error_msg: str) -> None:
        """Logs an error encountered during processing."""
        self.errors.append(f"Error in {file_name} at row {row_num}: {error_msg}")

    @transaction.atomic
    def run(self) -> Tuple[LoadSummary, List[str]]:
        """
        Executes the data loading process within a database transaction.
        Returns a summary dictionary and a list of errors.
        """
        self._load_claims()
        self._load_claim_details()

        summary: LoadSummary = {
            "claims_created": self.claims_created,
            "claims_updated": self.claims_updated,
            "details_created": self.details_created,
            "details_updated": self.details_updated,
        }
        return summary, self.errors

    def _load_claims(self) -> None:
        """Loads the main claim records from the provided CSV file."""
        print("Processing the main claims file...")
        try:
            with open(self.claims_csv_path, mode="r", encoding="utf-8") as f:
                # --- MODIFICATION 2: Use the specified delimiter ---
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for i, row in enumerate(reader, start=2):
                    try:
                        claim_id = int(row["id"])
                        billed_amount = Decimal(row["billed_amount"])
                        paid_amount = Decimal(row["paid_amount"])
                        discharge_date = datetime.strptime(
                            row["discharge_date"], "%Y-%m-%d"
                        ).date()

                        defaults = {
                            "patient_name": row["patient_name"],
                            "billed_amount": billed_amount,
                            "paid_amount": paid_amount,
                            "status": row["status"].upper(),
                            "insurer_name": row["insurer_name"],
                            "discharge_date": discharge_date,
                        }
                        _, created = Claim.objects.update_or_create(
                            id=claim_id, defaults=defaults
                        )
                        if created:
                            self.claims_created += 1
                        else:
                            self.claims_updated += 1
                    except (ValueError, InvalidOperation, KeyError) as e:
                        self._log_error(i, self.claims_csv_path.name, str(e))
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.claims_csv_path}")
            raise

    def _load_claim_details(self) -> None:
        """Loads the claim detail records from the provided CSV file."""
        print("Processing the details file...")
        try:
            with open(self.details_csv_path, mode="r", encoding="utf-8") as f:
                # --- MODIFICATION 3: Use the specified delimiter here as well ---
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for i, row in enumerate(reader, start=2):
                    try:
                        claim_id = int(row["claim_id"])
                        claim = Claim.objects.get(id=claim_id)

                        defaults = {
                            "cpt_codes": row["cpt_codes"],
                            "denial_reason": row.get("denial_reason", ""),
                        }
                        _, created = ClaimDetail.objects.update_or_create(
                            claim=claim, defaults=defaults
                        )
                        if created:
                            self.details_created += 1
                        else:
                            self.details_updated += 1
                    except Claim.DoesNotExist:
                        self._log_error(
                            i,
                            self.details_csv_path.name,
                            f"Claim with id={claim_id} not found.",
                        )
                    except (ValueError, KeyError) as e:
                        self._log_error(i, self.details_csv_path.name, str(e))
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.details_csv_path}")
            raise
