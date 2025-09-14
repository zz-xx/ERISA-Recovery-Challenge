import logging
from pathlib import Path

from django.core.management.base import (BaseCommand, CommandError, CommandParser)

from claims.services import ClaimDataIngestor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Loads claim and claim detail data from specified CSV files into the database."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Add the command line arguments for the CSV file paths."""
        parser.add_argument(
            "claims_csv",
            type=Path,
            help="The path to the CSV file containing claim data.",
        )
        parser.add_argument(
            "details_csv",
            type=Path,
            help="The path to the CSV file containing claim detail data.",
        )
        # Add an optional argument for the delimiter
        parser.add_argument(
            "--delimiter",
            type=str,
            default=",",
            help="The delimiter character used in the CSV files. Defaults to a comma (,).",
        )
        parser.add_argument(
            "--mode",
            type=str,
            choices=("overwrite", "append"),
            default="append",
            help=(
                "Data load mode: 'overwrite' clears existing Claim data then loads new rows; "
                "'append' only creates new rows and leaves existing ones unchanged. "
                "Defaults to 'append'."
            ),
        )

    def handle(self, *args, **options) -> None:
        """The main execution logic for the command."""
        claims_csv_path: Path = options["claims_csv"]
        details_csv_path: Path = options["details_csv"]
        delimiter: str = options["delimiter"]
        mode: str = options["mode"]

        if not claims_csv_path.exists():
            raise CommandError(f"File not found at: {claims_csv_path}")
        if not details_csv_path.exists():
            raise CommandError(f"File not found at: {details_csv_path}")

        logger.info(
            f"Starting data ingestion with delimiter='{delimiter}', mode='{mode}'..."
        )

        ingestor = ClaimDataIngestor(
            claims_csv_path, details_csv_path, delimiter=delimiter, mode=mode
        )

        try:
            summary, errors = ingestor.run()
        except Exception as e:
            logger.critical(f"A critical error occurred during ingestion: {e}")
            raise CommandError(f"A critical error occurred during ingestion: {e}")

        # Report summary
        logger.info("--- Ingestion Summary ---")
        for key, value in summary.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")
        logger.info("-------------------------")

        # Report errors
        if errors:
            logger.warning("Data ingestion completed with some errors.")
        else:
            logger.info("Data ingestion completed successfully with no errors.")
