"""Main scraper script to fetch and export legal process data."""

import os
import sys

from client.api_client import ApiClient
from config import ScraperConfig
from exceptions import (InvalidRequestError, ProcessNotFoundError,
                        ScraperException)
from services.export_service import ExportService
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
        logger.error("Busca vazia não permitida")
        return

    try:
        config = ScraperConfig()
        api_client = ApiClient(config=config)
        export_service = ExportService(config=config, base_dir=base_dir)
        process_service = ProcessService(api_client=api_client)

        logger.info("Buscando processos para: %s", request_data)
        processes = process_service.get_processes(request_data)

        if not processes or len(processes) == 0:
            raise ProcessNotFoundError(
                f"Nenhum processo encontrado para: {request_data}"
            )

        logger.info("Encontrados %d processo(s)", len(processes))
        export_service.export(processes)
        logger.info("Exportação concluída com sucesso!")

    except InvalidRequestError as e:
        logger.error("Formato de busca inválido: %s", e)
    except ProcessNotFoundError as e:
        logger.warning(str(e))
    except ScraperException as e:
        logger.error("Erro no scraper: %s", e)
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
    except (OSError, RuntimeError, ValueError, TypeError) as e:
        logger.exception("Erro inesperado: %s", e)


if __name__ == "__main__":
    main()
