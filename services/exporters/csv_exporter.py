"""CSV exporter implementation."""

import os
from dataclasses import dataclass

import pandas as pd

from models.process import Process


@dataclass
class CSVExporter:
    """Exports process data to CSV format."""

    export_path: str

    def __post_init__(self):
        os.makedirs(self.export_path, exist_ok=True)

    def export(self, process: Process, file_name: str) -> None:
        """Export a single process to CSV."""
        df = pd.DataFrame([process.to_csv_export()])
        file_path = os.path.join(self.export_path, f"{file_name}.csv")
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
