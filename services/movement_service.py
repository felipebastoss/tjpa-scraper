""" "Service to handle fetching and processing movement data from the API."""

from dataclasses import dataclass
from typing import Any, Dict, List

from client.api_client import ApiClient
from models.movement import Movement
from models.process import Process


@dataclass
class MovementService:
    """
    Service to handle fetching and processing movement data from the API.
    """

    api_client: ApiClient

    def get_movements(
        self,
        process: Process,
        page_number: int = 1,
    ) -> List[Movement]:
        """Fetch movements for a given process."""
        movements_result = []
        movements = self.__fetch_movements__(process, page_number)
        for movement in movements:
            movements_result.append(Movement.from_dict(movement))
        return movements_result

    def __fetch_movements__(
        self,
        process: Process,
        page_number: int = 1,
        result: List[Dict[str, Any]] = None,
        total_records: int = 0,
    ) -> List[Dict[str, Any]]:
        result = result or []
        response = self.api_client.get(
            f"{self.api_client.config.movements_api_route}"
            f"{process.number}/"
            f"{process.cd_doc_process}/"
            f"{process.cd_instance}/"
            f"{page_number}/1000"
        )
        if isinstance(response, list) and len(response) == 0:
            return result
        total_records = total_records or response.get("qtdRegistrosTotal", 0)
        page_result = response.get("listaResultado", [])
        if not page_result or len(page_result) == 0:
            return result
        result.extend(page_result)
        result = list({frozenset(i.items()): i for i in result}.values())
        if len(result) < total_records:
            result = self.__fetch_movements__(
                process, page_number + 1, result, total_records
            )
        return result
