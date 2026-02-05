"""Tests for the ScraperConfig class."""

from config import ScraperConfig


class TestScraperConfig:
    """Tests for ScraperConfig dataclass."""

    def test_default_values(self):
        """Test that ScraperConfig has correct default values."""
        config = ScraperConfig()

        assert (
            config.base_url
            == "https://consulta-processual-unificada-prd.tjpa.jus.br"
        )
        assert config.base_api_route == "/consilium-rest"
        assert config.movements_api_route == "/movimentacaopublicobycnj/"
        assert config.default_page_size == 1000
        assert config.default_page_number == 1
        assert config.csv_export_path == "csv_exports"
        assert config.json_export_path == "json_exports"
        assert config.request_timeout == 30
        assert config.min_wait_time == 1.0
        assert config.max_wait_time == 3.0
        assert "Mozilla" in config.user_agent

    def test_custom_values(self):
        """Test that ScraperConfig accepts custom values."""
        config = ScraperConfig(
            base_url="https://custom.url.com",
            request_timeout=60,
            min_wait_time=0.5,
            max_wait_time=1.5,
        )

        assert config.base_url == "https://custom.url.com"
        assert config.request_timeout == 60
        assert config.min_wait_time == 0.5
        assert config.max_wait_time == 1.5

    def test_export_paths_are_independent(self):
        """Test that export paths are independent instances."""
        config1 = ScraperConfig()
        config2 = ScraperConfig()

        # Default factory creates independent instances
        assert config1.csv_export_path == config2.csv_export_path
        assert config1.json_export_path == config2.json_export_path
