"""Main scraper script to fetch and export legal process data."""

import os
import sys

from client.api_client import ApiClient
from config import ScraperConfig
from exceptions import (
    InvalidRequestError,
    ProcessNotFoundError,
    ScraperException,
)
from services.export_service import ExportService
from services.movement_service import MovementService
from services.process_service import ProcessService
from utils.logging_config import setup_logging

base_dir = os.path.dirname(os.path.abspath(__file__))
logger = setup_logging(base_dir=base_dir)


def main():
    """Main entry point for the scraper."""
    if len(sys.argv) > 1:
        request_data = sys.argv[1]
    else:
        request_data = input("Digite aqui a sua busca processual: ")

    if not request_data:
        logger.error("Empty search not allowed")
        return

    try:
        config = ScraperConfig()
        api_client = ApiClient(config=config)
        export_service = ExportService(config=config, base_dir=base_dir)
        movement_service = MovementService(api_client=api_client)
        process_service = ProcessService(
            api_client=api_client,
            export_service=export_service,
            movement_service=movement_service,
        )

        logger.info("Searching processes for: %s", request_data)
        process_service.get_processes(request_data)
        logger.info("Export completed successfully!")

    except InvalidRequestError as e:
        logger.error("Invalid search format: %s", e)
    except ProcessNotFoundError as e:
        logger.warning(str(e))
    except ScraperException as e:
        logger.error("Scraper error: %s", e)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except (OSError, RuntimeError, ValueError, TypeError) as e:
        logger.exception("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
