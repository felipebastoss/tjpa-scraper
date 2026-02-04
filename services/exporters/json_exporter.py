"""JSON exporter implementation."""

import json
import os
from dataclasses import dataclass

from models.process import Process


@dataclass
class JSONExporter:
    """Exports process data to JSON format."""

    export_path: str

    def __post_init__(self):
        os.makedirs(self.export_path, exist_ok=True)

    def export(self, process: Process, file_name: str) -> None:
        """Export a single process to JSON."""
        file_path = os.path.join(self.export_path, f"{file_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(process.to_dict(), f, ensure_ascii=False, indent=4)
