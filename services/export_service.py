"""Service to handle exporting process data to various formats."""

import os
from dataclasses import dataclass
from typing import List

from config import ScraperConfig
from models.process import Process
from services.exporters.csv_exporter import CSVExporter
from services.exporters.json_exporter import JSONExporter


@dataclass
class ExportService:
    """
    Service to handle exporting process data to various formats.
    """

    config: ScraperConfig
    base_dir: str

    def export(self, processes: List[Process]):
        """Export a list of Process instances to CSV and JSON files."""
        csv_exporter = CSVExporter(
            export_path=os.path.join(self.base_dir, "data", self.config.csv_export_path)
        )
        json_exporter = JSONExporter(
            export_path=os.path.join(
                self.base_dir, "data", self.config.json_export_path
            )
        )
        for process in processes:
            file_name = f"process_{process.number}_doc_{process.cd_doc_process}_instance_{process.cd_instance}"
            csv_exporter.export(process, file_name)
            json_exporter.export(process, file_name)
