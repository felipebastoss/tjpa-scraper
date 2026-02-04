"""Module defining the Movement data model for legal process movements/events."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Movement:
    """
    Represents a single movement/event in a legal process.

    Attributes:
        date: The formatted date string (e.g., "01/02/2026")
        description: The movement description
    """

    date: str
    description: str

    def __str__(self):
        return f"{self.date}: {self.description}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"date": self.date, "description": self.description}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Movement":
        """
        Create a Movement instance from API response data.

        Args:
            data: Dictionary with 'dataFormatada' and 'descricao' keys

        Returns:
            A new Movement instance
        """
        return cls(date=data.get("dataFormatada"), description=data.get("descricao"))
