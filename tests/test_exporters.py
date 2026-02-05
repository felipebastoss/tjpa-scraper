"""Tests for exporter classes."""

import json
import os
import tempfile

import pytest

from models.movement import Movement
from models.party import Party
from models.process import Process
from services.exporters.csv_exporter import CSVExporter
from services.exporters.json_exporter import JSONExporter


class TestCSVExporter:
    """Tests for CSVExporter."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def csv_exporter(self, temp_dir):
        """Return a CSVExporter instance."""
        return CSVExporter(export_path=temp_dir)

    def test_creates_export_directory(self, temp_dir):
        """Test that export directory is created on initialization."""
        export_path = os.path.join(temp_dir, "new_dir")
        CSVExporter(export_path=export_path)

        assert os.path.exists(export_path)

    def test_export_creates_csv_file(
        self, csv_exporter, sample_process, temp_dir
    ):
        """Test that export creates a CSV file."""
        csv_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.csv")
        assert os.path.exists(file_path)

    def test_export_csv_content(self, csv_exporter, sample_process, temp_dir):
        """Test that exported CSV has correct content."""
        csv_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.csv")
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()

        # Check headers and values
        assert "Número do Processo" in content
        assert sample_process.formatted_number in content
        assert sample_process.class_ in content

    def test_export_overwrites_existing_file(
        self, csv_exporter, sample_process, temp_dir
    ):
        """Test that export overwrites existing file."""
        csv_exporter.export(sample_process, "test_process")

        # Modify process and export again
        sample_process.class_ = "Nova Classe"
        csv_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.csv")
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()

        assert "Nova Classe" in content


class TestJSONExporter:
    """Tests for JSONExporter."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def json_exporter(self, temp_dir):
        """Return a JSONExporter instance."""
        return JSONExporter(export_path=temp_dir)

    def test_creates_export_directory(self, temp_dir):
        """Test that export directory is created on initialization."""
        export_path = os.path.join(temp_dir, "new_dir")
        JSONExporter(export_path=export_path)

        assert os.path.exists(export_path)

    def test_export_creates_json_file(
        self, json_exporter, sample_process, temp_dir
    ):
        """Test that export creates a JSON file."""
        json_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.json")
        assert os.path.exists(file_path)

    def test_export_json_content(
        self, json_exporter, sample_process, temp_dir
    ):
        """Test that exported JSON has correct content."""
        json_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["number"] == sample_process.number
        assert data["formatted_number"] == sample_process.formatted_number
        assert data["class"] == sample_process.class_
        assert data["topic"] == sample_process.topic
        assert len(data["parties"]) == 1
        assert len(data["movements"]) == 1

    def test_export_json_is_formatted(
        self, json_exporter, sample_process, temp_dir
    ):
        """Test that exported JSON is properly formatted with indentation."""
        json_exporter.export(sample_process, "test_process")

        file_path = os.path.join(temp_dir, "test_process.json")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for indentation (4 spaces)
        assert "    " in content

    def test_export_json_handles_unicode(self, json_exporter, temp_dir):
        """Test that exported JSON handles Unicode characters correctly."""
        process = Process(
            formatted_number="1234-5",
            number="12345",
            class_="Ação Civil Pública",
            topic="Direito Ambiental - Área de Proteção",
            cd_doc_process="999",
            cd_instance="1",
            parties=[Party(name="José Açaí", party_type="Autor")],
            movements=[
                Movement(date="01/01/2026", description="Petição juntada")
            ],
            jurisdiction="São Paulo",
            competence="Cível",
            instance="1º Grau",
            situation="Em andamento",
            court="1ª Vara",
            police_inquiry="",
            cause_value="R$ 100.000,00",
            citation_date="01/01/2026",
            justice_secret="Não",
            distribution_date="01/01/2026",
        )

        json_exporter.export(process, "unicode_test")

        file_path = os.path.join(temp_dir, "unicode_test.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["class"] == "Ação Civil Pública"
        assert data["jurisdiction"] == "São Paulo"
        assert data["parties"][0]["name"] == "José Açaí"
