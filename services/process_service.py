"""
Service to handle fetching and processing legal process data from the API.
"""

from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, List

from client.api_client import ApiClient
from entities.request_type import RequestType
from exceptions import ProcessNotFoundError
from models.process import Process
from services.export_service import ExportService
from services.movement_service import MovementService

logger = getLogger("tjpa_scraper")


@dataclass
class ProcessService:
    """
    Service to handle fetching and processing legal process data from the API.
    """

    api_client: ApiClient
    export_service: ExportService
    movement_service: MovementService

    def get_processes(
        self,
        request_data: str,
        system_name: str = None,
        page_number: int = None,
        page_size: int = None,
    ) -> None:
        """Fetch processes based on request data and system name."""
        processes = self.__fetch_processes__(
            request_data, system_name, page_number, page_size
        )
        if not processes or len(processes) == 0:
            raise ProcessNotFoundError(
                f"No processes found for: {request_data}"
            )
        logger.info("Found %d process(es)", len(processes))
        for process in processes:
            logger.info(
                "Exporting %d/%d: %s",
                processes.index(process) + 1,
                len(processes),
                process.get("numero"),
            )
            process_instance = Process.from_dict(process)
            process_instance.movements = self.movement_service.get_movements(
                process_instance
            )
            self.export_service.export(process_instance)

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
            if len(response) == 0:
                return result or []
            return self.__handle_list_data__(response)
        processes = response.get("listaProcessos")
        if not processes:
            search_results = response.get("listaResultado")
            if not search_results or len(search_results) == 0:
                return result or []
            total_records = total_records or response.get(
                "qtdRegistrosTotal", 0
            )
            for result_item in search_results:
                result_processes = result_item.get("listaProcessos")
                if result_processes:
                    result.extend(result_processes)
            result = self.__deduplicate_processes__(result)
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
                    "No processes found for the given request."
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

    def __make_hashable__(self, obj):
        if isinstance(obj, dict):
            return frozenset(
                (k, self.__make_hashable__(v)) for k, v in obj.items()
            )
        if isinstance(obj, list):
            return tuple(self.__make_hashable__(i) for i in obj)
        return obj

    def __deduplicate_processes__(self, processes):
        seen = set()
        unique_processes = []
        for process in processes:
            hashable_process = self.__make_hashable__(process)
            if hashable_process not in seen:
                seen.add(hashable_process)
                unique_processes.append(process)
        return unique_processes
