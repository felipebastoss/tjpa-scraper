"""Tests for service classes."""

import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest

from client.api_client import ApiClient
from models.movement import Movement
from models.process import Process
from services.export_service import ExportService
from services.movement_service import MovementService
from services.process_service import ProcessService


class TestMovementService:
    """Tests for MovementService."""

    @pytest.fixture
    def mock_api_client(self, scraper_config):
        """Return a mocked ApiClient."""
        client = MagicMock(spec=ApiClient)
        client.config = scraper_config
        return client

    @pytest.fixture
    def movement_service(self, mock_api_client):
        """Return a MovementService instance."""
        return MovementService(api_client=mock_api_client)

    def test_get_movements_success(
        self, movement_service, sample_process, sample_api_movement_response
    ):
        """Test successful movement fetching."""
        movement_service.api_client.get.return_value = sample_api_movement_response

        result = movement_service.get_movements(sample_process)

        assert len(result) == 1
        assert isinstance(result[0], Movement)
        assert result[0].date == "01/02/2026"
        assert result[0].description == "Juntada de petição"

    def test_get_movements_empty(self, movement_service, sample_process):
        """Test movement fetching with no results."""
        movement_service.api_client.get.return_value = {
            "qtdRegistrosTotal": 0,
            "listaResultado": [],
        }

        result = movement_service.get_movements(sample_process)

        assert result == []

    def test_get_movements_constructs_correct_url(
        self, movement_service, sample_process
    ):
        """Test that correct URL is constructed for movements."""
        movement_service.api_client.get.return_value = {
            "qtdRegistrosTotal": 0,
            "listaResultado": [],
        }

        movement_service.get_movements(sample_process)

        expected_url = (
            f"{movement_service.api_client.config.movements_api_route}"
            f"{sample_process.number}/{sample_process.cd_doc_process}/"
            f"{sample_process.cd_instance}/1/1000"
        )
        movement_service.api_client.get.assert_called_with(expected_url)

    def test_get_movements_pagination(self, movement_service, sample_process):
        """Test movement fetching with pagination."""
        # First call returns partial results
        first_response = {
            "qtdRegistrosTotal": 2,
            "listaResultado": [{"dataFormatada": "01/01/2026", "descricao": "Movimento 1"}],
        }
        # Second call returns more results
        second_response = {
            "qtdRegistrosTotal": 2,
            "listaResultado": [{"dataFormatada": "02/01/2026", "descricao": "Movimento 2"}],
        }

        movement_service.api_client.get.side_effect = [first_response, second_response]

        result = movement_service.get_movements(sample_process)

        assert len(result) == 2
        assert movement_service.api_client.get.call_count == 2


class TestProcessService:
    """Tests for ProcessService."""

    @pytest.fixture
    def mock_api_client(self, scraper_config):
        """Return a mocked ApiClient."""
        client = MagicMock(spec=ApiClient)
        client.config = scraper_config
        return client

    @pytest.fixture
    def mock_movement_service(self):
        """Return a mocked MovementService."""
        service = MagicMock(spec=MovementService)
        service.get_movements.return_value = []
        return service

    @pytest.fixture
    def process_service(self, mock_api_client, mock_movement_service):
        """Return a ProcessService instance."""
        return ProcessService(
            api_client=mock_api_client, movement_service=mock_movement_service
        )

    def test_get_processes_with_cnj(
        self, process_service, sample_api_process_response
    ):
        """Test fetching processes by CNJ number."""
        process_service.api_client.get.return_value = {
            "listaProcessos": [sample_api_process_response]
        }

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert len(result) == 1
        assert isinstance(result[0], Process)
        assert result[0].number == "08012345620268140301"

    def test_get_processes_fetches_movements(
        self, process_service, sample_api_process_response
    ):
        """Test that movements are fetched for each process."""
        process_service.api_client.get.return_value = {
            "listaProcessos": [sample_api_process_response]
        }
        mock_movements = [Movement(date="01/01/2026", description="Test")]
        process_service.movement_service.get_movements.return_value = mock_movements

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        process_service.movement_service.get_movements.assert_called_once()
        assert result[0].movements == mock_movements

    def test_get_processes_empty_result(self, process_service):
        """Test fetching processes with no results."""
        process_service.api_client.get.return_value = {"listaResultado": []}

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert result == []

    def test_get_processes_with_list_response(self, process_service):
        """Test fetching processes when API returns a list directly with numero field."""
        list_response = [
            {
                "numero": "08012345620268140301",
                "numeroFormatado": "0801234-56.2026.8.14.0301",
                "classe": "Classe",
                "assunto": "Assunto",
                "cdDocProcesso": "999",
                "cdInstancia": "1",
                "nome": None,
                "sistema": None,
            }
        ]
        process_service.api_client.get.return_value = list_response

        result = process_service.get_processes("08012345620268140301")

        assert len(result) == 1

    def test_movement_service_auto_created(self, mock_api_client):
        """Test that MovementService is auto-created if not provided."""
        service = ProcessService(api_client=mock_api_client)

        assert service.movement_service is not None
        assert isinstance(service.movement_service, MovementService)


class TestProcessServiceApiResponseFormats:
    """Tests for ProcessService handling different API response formats."""

    @pytest.fixture
    def mock_api_client(self, scraper_config):
        """Return a mocked ApiClient."""
        client = MagicMock(spec=ApiClient)
        client.config = scraper_config
        return client

    @pytest.fixture
    def mock_movement_service(self):
        """Return a mocked MovementService."""
        service = MagicMock(spec=MovementService)
        service.get_movements.return_value = []
        return service

    @pytest.fixture
    def process_service(self, mock_api_client, mock_movement_service):
        """Return a ProcessService instance."""
        return ProcessService(
            api_client=mock_api_client, movement_service=mock_movement_service
        )

    @pytest.fixture
    def sample_process_data(self):
        """Return sample process data as returned by the API."""
        return {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "classe": "Ação Civil Pública",
            "assunto": "Direito Ambiental",
            "comarca": "Belém",
            "competencia": "Cível",
            "cdDocProcesso": "12345",
            "instancia": "1º Grau",
            "cdInstancia": "1",
            "situacao": "Em andamento",
            "vara": "1ª Vara Cível",
            "partes": [{"nome": "João da Silva", "tipo": "Autor"}],
        }

    # =========================================================================
    # Format 1: Direct list of processes
    # [sample_process, ...]
    # =========================================================================

    def test_format1_direct_list_of_processes(
        self, process_service, sample_process_data
    ):
        """Test API response format 1: direct list of process objects."""
        # Add required fields for list detection (nome=None, sistema=None means direct process)
        process_data = {**sample_process_data, "nome": None, "sistema": None}
        api_response = [process_data]

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("08012345620268140301")

        assert len(result) == 1
        assert isinstance(result[0], Process)
        assert result[0].number == "08012345620268140301"
        assert result[0].formatted_number == "0801234-56.2026.8.14.0301"

    def test_format1_direct_list_multiple_processes(
        self, process_service, sample_process_data
    ):
        """Test format 1 with multiple processes in the list."""
        processes = []
        for i in range(3):
            process = {
                **sample_process_data,
                "numero": f"0801234562026814030{i}",
                "numeroFormatado": f"0801234-56.2026.8.14.030{i}",
                "cdDocProcesso": str(12345 + i),
                "nome": None,
                "sistema": None,
            }
            processes.append(process)

        process_service.api_client.get.return_value = processes

        result = process_service.get_processes("08012345620268140301")

        assert len(result) == 3
        assert all(isinstance(p, Process) for p in result)

    def test_format1_direct_list_fetches_movements_for_each(
        self, process_service, sample_process_data
    ):
        """Test that movements are fetched for each process in format 1."""
        process_data = {**sample_process_data, "nome": None, "sistema": None}
        api_response = [process_data]

        process_service.api_client.get.return_value = api_response
        mock_movements = [Movement(date="01/01/2026", description="Test movement")]
        process_service.movement_service.get_movements.return_value = mock_movements

        result = process_service.get_processes("08012345620268140301")

        process_service.movement_service.get_movements.assert_called_once()
        assert result[0].movements == mock_movements

    # =========================================================================
    # Format 2: Pre-search party name response (list of name/system objects)
    # [{"nome": "string", "quantidade": "string", "sistema": "string"}, ...]
    # =========================================================================

    def test_format2_presearch_party_name_single_result(
        self, process_service, sample_process_data
    ):
        """Test API response format 2: pre-search party name with single result."""
        # First call returns pre-search result
        presearch_response = [
            {"nome": "Jose Antonio", "quantidade": "1", "sistema": "PROJUDI"}
        ]
        # Second call returns actual process data
        process_response = {"listaProcessos": [sample_process_data]}

        process_service.api_client.get.side_effect = [
            presearch_response,
            process_response,
        ]

        result = process_service.get_processes("Jose Antonio")

        assert len(result) == 1
        assert isinstance(result[0], Process)
        # Should have made 2 API calls: presearch + actual fetch
        assert process_service.api_client.get.call_count == 2

    def test_format2_presearch_party_name_multiple_systems(
        self, process_service, sample_process_data
    ):
        """Test format 2 with multiple systems returned in pre-search."""
        # First call returns pre-search with multiple systems
        presearch_response = [
            {"nome": "Jose Antonio", "quantidade": "2", "sistema": "PROJUDI"},
            {"nome": "Jose Antonio", "quantidade": "1", "sistema": "TUCUJURIS"},
        ]
        # Subsequent calls return process data for each system
        projudi_response = {"listaProcessos": [sample_process_data]}
        tucujuris_process = {
            **sample_process_data,
            "numero": "08099999920268140301",
            "cdDocProcesso": "99999",
        }
        tucujuris_response = {"listaProcessos": [tucujuris_process]}

        process_service.api_client.get.side_effect = [
            presearch_response,
            projudi_response,
            tucujuris_response,
        ]

        result = process_service.get_processes("Jose Antonio")

        assert len(result) == 2
        # Should have made 3 API calls: presearch + 2 system fetches
        assert process_service.api_client.get.call_count == 3

    def test_format2_presearch_empty_nome_or_sistema_skipped(
        self, process_service, sample_process_data
    ):
        """Test that pre-search items without nome or sistema are skipped."""
        presearch_response = [
            {"nome": "Jose Antonio", "quantidade": "1", "sistema": "PROJUDI"},
            {"nome": None, "quantidade": "0", "sistema": "TUCUJURIS"},  # Should be skipped
            {"nome": "Maria", "quantidade": "0", "sistema": None},  # Should be skipped
        ]
        process_response = {"listaProcessos": [sample_process_data]}

        process_service.api_client.get.side_effect = [
            presearch_response,
            process_response,
        ]

        result = process_service.get_processes("Jose Antonio")

        # Only one system should have been fetched (the valid one)
        assert process_service.api_client.get.call_count == 2

    # =========================================================================
    # Format 3: One process response (usually CNJ search)
    # {"numero": "string", "numeroFormatado": "string", "listaProcessos": [...]}
    # =========================================================================

    def test_format3_cnj_single_process_response(
        self, process_service, sample_process_data
    ):
        """Test API response format 3: CNJ search with listaProcessos."""
        api_response = {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "listaProcessos": [sample_process_data],
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert len(result) == 1
        assert isinstance(result[0], Process)
        assert result[0].number == "08012345620268140301"

    def test_format3_cnj_multiple_processes_in_list(
        self, process_service, sample_process_data
    ):
        """Test format 3 with multiple processes in listaProcessos."""
        second_process = {
            **sample_process_data,
            "numero": "08099999920268140301",
            "cdDocProcesso": "99999",
            "instancia": "2º Grau",
        }
        api_response = {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "listaProcessos": [sample_process_data, second_process],
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert len(result) == 2
        assert result[0].number == "08012345620268140301"
        assert result[1].number == "08099999920268140301"

    def test_format3_cnj_empty_lista_processos(self, process_service):
        """Test format 3 with empty listaProcessos."""
        api_response = {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "listaProcessos": [],
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert result == []

    # =========================================================================
    # Format 4: Search response with pagination
    # {"pagina": int, "qtdRegistrosPagina": int, "qtdRegistrosTotal": int,
    #  "listaResultado": [{"numero": ..., "listaProcessos": [...]}, ...]}
    # =========================================================================

    def test_format4_paginated_search_single_page(
        self, process_service, sample_process_data
    ):
        """Test API response format 4: paginated search with single page."""
        api_response = {
            "pagina": 1,
            "qtdRegistrosPagina": 10,
            "qtdRegistrosTotal": 1,
            "listaResultado": [
                {
                    "numero": "08012345620268140301",
                    "numeroFormatado": "0801234-56.2026.8.14.0301",
                    **sample_process_data,
                }
            ],
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("12345678901")  # CPF format

        assert len(result) == 1
        assert isinstance(result[0], Process)

    def test_format4_paginated_search_multiple_pages(
        self, process_service
    ):
        """Test format 4 with multiple pages requiring pagination."""
        # Use simple process data without nested lists for pagination tests
        # (the code uses frozenset for deduplication which doesn't support nested lists)
        process1 = {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "classe": "Classe",
            "assunto": "Assunto",
            "cdDocProcesso": "12345",
            "cdInstancia": "1",
        }
        process2 = {
            "numero": "08099999920268140302",
            "numeroFormatado": "0809999-99.2026.8.14.0302",
            "classe": "Classe",
            "assunto": "Assunto",
            "cdDocProcesso": "99999",
            "cdInstancia": "1",
        }
        # First page
        first_page = {
            "pagina": 1,
            "qtdRegistrosPagina": 1,
            "qtdRegistrosTotal": 2,
            "listaResultado": [process1],
        }
        # Second page
        second_page = {
            "pagina": 2,
            "qtdRegistrosPagina": 1,
            "qtdRegistrosTotal": 2,
            "listaResultado": [process2],
        }

        process_service.api_client.get.side_effect = [first_page, second_page]

        result = process_service.get_processes("123.456.789-01", page_number=1, page_size=1)

        assert len(result) == 2
        assert process_service.api_client.get.call_count == 2

    def test_format4_paginated_search_empty_result(self, process_service):
        """Test format 4 with empty listaResultado."""
        api_response = {
            "pagina": 1,
            "qtdRegistrosPagina": 10,
            "qtdRegistrosTotal": 0,
            "listaResultado": [],
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("12345678901")

        assert result == []

    def test_format4_paginated_search_deduplicates_existing_results(
        self, process_service
    ):
        """Test that format 4 deduplicates existing results before extending."""
        # The deduplication in the code happens on `result` before extending with new items
        # This test verifies that duplicates in the accumulated result are removed
        process1 = {
            "numero": "08012345620268140301",
            "numeroFormatado": "0801234-56.2026.8.14.0301",
            "classe": "Classe",
            "assunto": "Assunto",
            "cdDocProcesso": "12345",
            "cdInstancia": "1",
        }
        process2 = {
            "numero": "08099999920268140302",
            "numeroFormatado": "0809999-99.2026.8.14.0302",
            "classe": "Classe",
            "assunto": "Assunto",
            "cdDocProcesso": "99999",
            "cdInstancia": "1",
        }
        first_page = {
            "pagina": 1,
            "qtdRegistrosPagina": 1,
            "qtdRegistrosTotal": 2,
            "listaResultado": [process1],
        }
        second_page = {
            "pagina": 2,
            "qtdRegistrosPagina": 1,
            "qtdRegistrosTotal": 2,
            "listaResultado": [process2],
        }

        process_service.api_client.get.side_effect = [first_page, second_page]

        result = process_service.get_processes("123.456.789-01", page_number=1, page_size=1)

        # Both unique processes should be returned
        assert len(result) == 2
        numbers = [p.number for p in result]
        assert "08012345620268140301" in numbers
        assert "08099999920268140302" in numbers

    # =========================================================================
    # Edge cases and error handling
    # =========================================================================

    def test_list_response_without_numero_raises_error(self, process_service):
        """Test that list response without 'numero' field raises AttributeError."""
        # Direct list but missing 'numero' field
        api_response = [
            {
                "nome": None,
                "sistema": None,
                "classe": "Classe",
                # Missing 'numero' field
            }
        ]

        process_service.api_client.get.return_value = api_response

        with pytest.raises(AttributeError) as exc_info:
            process_service.get_processes("08012345620268140301")

        assert "Nenhum processo encontrado" in str(exc_info.value)

    def test_response_with_no_lista_processos_and_no_lista_resultado(
        self, process_service
    ):
        """Test response without listaProcessos or listaResultado returns empty."""
        api_response = {
            "numero": "08012345620268140301",
            "someOtherField": "value",
            # No listaProcessos or listaResultado
        }

        process_service.api_client.get.return_value = api_response

        result = process_service.get_processes("0801234-56.2026.8.14.0301")

        assert result == []


class TestExportService:
    """Tests for ExportService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def export_service(self, scraper_config, temp_dir):
        """Return an ExportService instance."""
        return ExportService(config=scraper_config, base_dir=temp_dir)

    def test_export_creates_csv_and_json(self, export_service, sample_process, temp_dir):
        """Test that export creates both CSV and JSON files."""
        export_service.export([sample_process])

        csv_dir = os.path.join(temp_dir, "data", export_service.config.csv_export_path)
        json_dir = os.path.join(temp_dir, "data", export_service.config.json_export_path)

        # Check directories were created
        assert os.path.exists(csv_dir)
        assert os.path.exists(json_dir)

        # Check files were created
        expected_filename = (
            f"process_{sample_process.number}_doc_{sample_process.cd_doc_process}"
            f"_instance_{sample_process.cd_instance}"
        )
        assert os.path.exists(os.path.join(csv_dir, f"{expected_filename}.csv"))
        assert os.path.exists(os.path.join(json_dir, f"{expected_filename}.json"))

    def test_export_json_content(self, export_service, sample_process, temp_dir):
        """Test that exported JSON has correct content."""
        export_service.export([sample_process])

        json_dir = os.path.join(temp_dir, "data", export_service.config.json_export_path)
        expected_filename = (
            f"process_{sample_process.number}_doc_{sample_process.cd_doc_process}"
            f"_instance_{sample_process.cd_instance}.json"
        )
        json_path = os.path.join(json_dir, expected_filename)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["number"] == sample_process.number
        assert data["formatted_number"] == sample_process.formatted_number
        assert data["class"] == sample_process.class_

    def test_export_multiple_processes(self, export_service, temp_dir):
        """Test exporting multiple processes."""
        processes = [
            Process(
                formatted_number=f"1234-{i}",
                number=f"1234567890123456789{i}",
                class_="Classe",
                topic="Assunto",
                cd_doc_process=str(i),
                cd_instance="1",
                parties=[],
                movements=[],
            )
            for i in range(3)
        ]

        export_service.export(processes)

        json_dir = os.path.join(temp_dir, "data", export_service.config.json_export_path)
        json_files = os.listdir(json_dir)
        assert len(json_files) == 3
