from pathlib import Path
from django.core.management.base import BaseCommand, CommandError, CommandParser
from claims.services import ClaimDataIngestor


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
        # --- MODIFICATION: Add an optional argument for the delimiter ---
        parser.add_argument(
            "--delimiter",
            type=str,
            default=",",
            help="The delimiter character used in the CSV files. Defaults to a comma (,).",
        )

    def handle(self, *args, **options) -> None:
        """The main execution logic for the command."""
        claims_csv_path: Path = options["claims_csv"]
        details_csv_path: Path = options["details_csv"]
        delimiter: str = options["delimiter"]

        if not claims_csv_path.exists():
            raise CommandError(f"File not found at: {claims_csv_path}")
        if not details_csv_path.exists():
            raise CommandError(f"File not found at: {details_csv_path}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting data ingestion with '{delimiter}' as the delimiter..."
            )
        )

        # --- MODIFICATION: Pass the delimiter to the ingestor ---
        ingestor = ClaimDataIngestor(
            claims_csv_path, details_csv_path, delimiter=delimiter
        )

        try:
            summary, errors = ingestor.run()
        except Exception as e:
            raise CommandError(f"A critical error occurred during ingestion: {e}")

        # Report summary
        for key, value in summary.items():
            self.stdout.write(
                self.style.SUCCESS(f"{key.replace('_', ' ').title()}: {value}")
            )

        # Report errors
        if errors:
            self.stdout.write(self.style.WARNING("\nCompleted with some errors:"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f" - {error}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\nData ingestion completed successfully with no errors."
                )
            )
