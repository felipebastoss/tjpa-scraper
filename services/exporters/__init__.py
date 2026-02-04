"""Exporter interfaces and implementations."""

from typing import Protocol

from models.process import Process


class Exporter(Protocol):
    """Protocol for process exporters."""

    def export(self, process: Process, file_name: str) -> None:
        """Export a single process to the target format."""
        ...
