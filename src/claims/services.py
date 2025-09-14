import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from django.db import transaction, IntegrityError

from .models import Claim, ClaimDetail

logger = logging.getLogger(__name__)

# A type alias for our summary dictionary
LoadSummary = Dict[str, int]


class ClaimDataIngestor:
    """
    A service class to handle the ingestion of claim data from CSV files.
    This class encapsulates the logic for parsing, validating, and saving
    claim and claim detail data to the database.
    """

    def __init__(
        self,
        claims_csv_path: Union[Path, str],
        details_csv_path: Union[Path, str],
        delimiter: str = ",",
        mode: str = "append",
    ):
        """
        Initializes the ingestor with paths to the data files.

        Args:
            claims_csv_path: The file path for the main claims data.
            details_csv_path: The file path for the claim details data.
            delimiter: The character used to separate values in the CSV files.
        """
        self.claims_csv_path = Path(claims_csv_path)
        self.details_csv_path = Path(details_csv_path)
        self.delimiter = delimiter
        self.mode = mode  # 'append' (default) or 'overwrite'
        self.claims_created = 0
        self.claims_updated = 0
        self.claims_skipped = 0
        self.details_created = 0
        self.details_updated = 0
        self.details_skipped = 0
        self.errors: List[str] = []

    def _log_error(self, row_num: int, file_name: str, error_msg: str) -> None:
        """Helper method to format and store an error message."""
        full_error_msg = f"Error in {file_name} at row {row_num}: {error_msg}"
        logger.error(full_error_msg)  # Log as an ERROR
        self.errors.append(full_error_msg)  # Keep for the command's summary

    @transaction.atomic
    def run(self) -> Tuple[LoadSummary, List[str]]:
        """
        Executes the full data loading process within a single database transaction.
        If any part of the process fails, the transaction is rolled back.

        Returns:
            A tuple containing a summary dictionary of the load results and a
            list of any errors encountered.
        """
        if self.mode == "overwrite":
            self._purge_existing_data()

        self._load_claims()
        self._load_claim_details()

        summary: LoadSummary = {
            "claims_created": self.claims_created,
            "claims_updated": self.claims_updated,
            "claims_skipped": self.claims_skipped,
            "details_created": self.details_created,
            "details_updated": self.details_updated,
            "details_skipped": self.details_skipped,
        }
        return summary, self.errors

    def _purge_existing_data(self) -> None:
        """Deletes all existing claim-related data prior to overwrite reload."""
        logger.info("Overwrite mode: purging existing Claim data (cascade deletes details/notes)...")
        # Deleting Claims will cascade to ClaimDetail and Note via FK/OneToOne settings
        Claim.objects.all().delete()

    def _parse_claim_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parses and validates a single row from the claims CSV file."""
        claim_id = int(row["id"])
        billed_amount = Decimal(row["billed_amount"])
        paid_amount = Decimal(row["paid_amount"])
        discharge_date = datetime.strptime(row["discharge_date"], "%Y-%m-%d").date()

        return {
            "id": claim_id,
            "patient_name": row["patient_name"],
            "billed_amount": billed_amount,
            "paid_amount": paid_amount,
            "status": row["status"].upper(),
            "insurer_name": row["insurer_name"],
            "discharge_date": discharge_date,
        }

    def _write_claim(self, claim_data: Dict[str, Any]) -> None:
        """Create a Claim according to mode semantics."""
        claim_id = claim_data.pop("id")
        if self.mode == "append":
            if Claim.objects.filter(id=claim_id).exists():
                self.claims_skipped += 1
                return
            Claim.objects.create(id=claim_id, **claim_data)
            self.claims_created += 1
            return
        # overwrite mode: table was purged; create fresh rows only
        try:
            Claim.objects.create(id=claim_id, **claim_data)
            self.claims_created += 1
        except IntegrityError as e:
            # Duplicate IDs within the same CSV or DB state mismatch
            self._log_error(0, self.claims_csv_path.name, f"Integrity error for claim {claim_id}: {e}")

    def _load_claims(self) -> None:
        """Loads the main claim records from the provided CSV file."""
        logger.info(f"Processing the main claims file: {self.claims_csv_path.name}")
        try:
            with open(self.claims_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for i, row in enumerate(reader, start=2):
                    try:
                        claim_data = self._parse_claim_row(row)
                        self._write_claim(claim_data)
                    except (ValueError, InvalidOperation, KeyError) as e:
                        self._log_error(i, self.claims_csv_path.name, str(e))
        except FileNotFoundError:
            logger.critical(f"File not found: {self.claims_csv_path}")
            self.errors.append(f"File not found: {self.claims_csv_path}")
            raise

    def _load_claim_details(self) -> None:
        """Loads the claim detail records from the provided CSV file."""
        logger.info(f"Processing the details file: {self.details_csv_path.name}")
        try:
            with open(self.details_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for i, row in enumerate(reader, start=2):
                    try:
                        claim_id = int(row["claim_id"])
                        claim = Claim.objects.get(id=claim_id)

                        defaults = {
                            "cpt_codes": row["cpt_codes"],
                            "denial_reason": row.get("denial_reason", ""),
                        }
                        if self.mode == "append":
                            if ClaimDetail.objects.filter(claim=claim).exists():
                                self.details_skipped += 1
                            else:
                                ClaimDetail.objects.create(claim=claim, **defaults)
                                self.details_created += 1
                        else:
                            # overwrite mode: table was purged by deleting Claims
                            try:
                                ClaimDetail.objects.create(claim=claim, **defaults)
                                self.details_created += 1
                            except IntegrityError as e:
                                self._log_error(
                                    i,
                                    self.details_csv_path.name,
                                    f"Integrity error for claim detail {claim.id}: {e}",
                                )
                    except Claim.DoesNotExist:
                        self._log_error(
                            i,
                            self.details_csv_path.name,
                            f"Claim with id={claim_id} not found.",
                        )
                    except (ValueError, KeyError) as e:
                        self._log_error(i, self.details_csv_path.name, str(e))
        except FileNotFoundError:
            logger.critical(f"File not found: {self.details_csv_path}")
            self.errors.append(f"File not found: {self.details_csv_path}")
            raise
