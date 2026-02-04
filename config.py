"""Configuration settings for the scraper."""

from dataclasses import dataclass, field


@dataclass
class ScraperConfig:
    """Configuration settings for the scraper."""

    base_url: str = "https://consulta-processual-unificada-prd.tjpa.jus.br"
    base_api_route: str = "/consilium-rest"
    movements_api_route: str = "/movimentacaopublicobycnj/"
    default_page_size: int = 1000
    default_page_number: int = 1
    csv_export_path: str = field(default_factory=lambda: "csv_exports")
    json_export_path: str = field(default_factory=lambda: "json_exports")
    request_timeout: int = 30
    min_wait_time: float = 1.0
    max_wait_time: float = 3.0
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
