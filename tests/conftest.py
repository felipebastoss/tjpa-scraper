"""Pytest fixtures and configuration for TJPA scraper tests."""

import pytest

from config import ScraperConfig
from models.movement import Movement
from models.party import Party
from models.process import Process


@pytest.fixture
def scraper_config():
    """Return a default ScraperConfig instance."""
    return ScraperConfig()


@pytest.fixture
def sample_party():
    """Return a sample Party instance."""
    return Party(name="João da Silva", party_type="Autor")


@pytest.fixture
def sample_movement():
    """Return a sample Movement instance."""
    return Movement(date="01/02/2026", description="Juntada de petição")


@pytest.fixture
def sample_process(sample_party, sample_movement):
    """Return a sample Process instance."""
    return Process(
        formatted_number="0801234-56.2026.8.14.0301",
        number="08012345620268140301",
        class_="Ação Civil Pública",
        topic="Direito Ambiental",
        cd_doc_process="12345",
        cd_instance="1",
        parties=[sample_party],
        movements=[sample_movement],
        jurisdiction="Belém",
        competence="Cível",
        instance="1º Grau",
        situation="Em andamento",
        court="1ª Vara Cível",
        police_inquiry="",
        cause_value="R$ 100.000,00",
        citation_date="01/01/2026",
        justice_secret="Não",
        distribution_date="01/01/2026",
    )


@pytest.fixture
def sample_api_process_response():
    """Return a sample API response for a process."""
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
        "numeroInqueritoPolicial": "",
        "valorCausaFormatado": "R$ 100.000,00",
        "dataAutuacaoFormatada": "01/01/2026",
        "segredoJustica": "Não",
        "dataDistribuicaoFormatada": "01/01/2026",
        "partes": [{"nome": "João da Silva", "tipo": "Autor"}],
    }


@pytest.fixture
def sample_api_movement_response():
    """Return a sample API response for movements."""
    return {
        "qtdRegistrosTotal": 1,
        "listaResultado": [
            {"dataFormatada": "01/02/2026", "descricao": "Juntada de petição"}
        ],
    }
