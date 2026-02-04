"""Module defining the Party data model for legal process parties."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Party:
    """
    Represents a party (person or entity) in a legal process.

    Attributes:
        name: Full name of the party
        party_type: Role in the process (e.g., "Autor", "Réu", "Advogado")
    """

    name: str
    party_type: str

    def __str__(self):
        return f"{self.name} ({self.party_type})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"name": self.name, "type": self.party_type}
