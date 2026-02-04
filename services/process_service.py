"""Service to handle fetching and processing legal process data from the API."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from client.api_client import ApiClient
from entities.request_type import RequestType
from exceptions import ApiConnectionError, ApiResponseError
from models.process import Process
from services.movement_service import MovementService
from utils.retry import retry


@dataclass
class ProcessService:
    """
    Service to handle fetching and processing legal process data from the API.
    """

    api_client: ApiClient
    movement_service: Optional[MovementService] = None

    def __post_init__(self):
        if self.movement_service is None:
            self.movement_service = MovementService(api_client=self.api_client)

    def get_processes(
        self,
        request_data: str,
        system_name: str = None,
        page_number: int = None,
        page_size: int = None,
    ) -> List[Process]:
        """Fetch processes based on request data and system name."""
        processes_result = []
        processes = self.__fetch_processes__(
            request_data, system_name, page_number, page_size
        )
        for process in processes:
            process_instance = Process.from_dict(process)
            process_instance.movements = self.movement_service.get_movements(
                process_instance
            )
            processes_result.append(process_instance)
        return processes_result

    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(ApiConnectionError, ApiResponseError, TimeoutError),
    )
    def __fetch_processes__(
        self,
        request_data: str,
        system_name: str = None,
        page_number: int = None,
        page_size: int = None,
        result: List[Dict[str, Any]] = None,
        total_records: int = 0,
    ) -> List[Dict[str, Any]]:
        result = result or []
        request_type = RequestType.get_type(request_data)
        url = request_type.get_request_url(
            request_data,
            system_name=system_name,
            page_number=page_number,
            page_size=page_size,
        )
        response = self.api_client.get(url)
        if isinstance(response, list):
            return self.__handle_list_data__(response)
        processes = response.get("listaProcessos")
        if not processes:
            search_results = response.get("listaResultado")
            if not search_results or len(search_results) == 0:
                return result or []
            total_records = total_records or response.get("qtdRegistrosTotal", 0)
            result = list({frozenset(item.items()): item for item in result}.values())
            result.extend(search_results)
            if len(result) < total_records:
                result = self.__fetch_processes__(
                    request_data,
                    system_name,
                    page_number + 1,
                    page_size,
                    result,
                    total_records,
                )
            return result
        result.extend(processes)
        return result

    def __handle_list_data__(self, request_data):
        if not request_data[0]["nome"] and not request_data[0]["sistema"]:
            if not request_data[0].get("numero"):
                raise AttributeError(
                    "Nenhum processo encontrado para a requisição informada."
                )
            return request_data
        return self.__handle_party_name_presearch__(request_data)

    def __handle_party_name_presearch__(self, request_data):
        processes_result = []
        for item in request_data:
            if item.get("nome") and item.get("sistema"):
                processes_data = self.__fetch_processes__(
                    item["nome"], item["sistema"], 1, 1000
                )
                processes_result.extend(processes_data)
        return processes_result
