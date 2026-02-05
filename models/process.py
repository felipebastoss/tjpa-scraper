"""Module defining the Process data model for legal processes."""

from dataclasses import dataclass
from typing import Any, Dict, List

from models.movement import Movement
from models.party import Party


@dataclass
class Process:
    """
    Represents a legal process with all its metadata.
    """

    formatted_number: str
    number: str
    class_: str
    topic: str
    cd_doc_process: str
    cd_instance: str
    parties: List[Party]
    movements: List[Movement]
    jurisdiction: str = ""
    competence: str = ""
    instance: str = ""
    situation: str = ""
    court: str = ""
    police_inquiry: str = ""
    cause_value: str = ""
    citation_date: str = ""
    justice_secret: str = ""
    distribution_date: str = ""

    def __str__(self):
        return (
            f"Processo {self.formatted_number}, "
            f"Classe: {self.class_}, "
            f"Assunto: {self.topic}, "
            f"Jurisdição: {self.jurisdiction}, "
            f"Competência: {self.competence}, "
            f"Instância: {self.instance}, "
            f"Situação: {self.situation}, "
            f"Órgão Julgador: {self.court}, "
            f"Inquérito Policial: {self.police_inquiry}, "
            f"Valor da Causa: {self.cause_value}, "
            f"Data da Autuação: {self.citation_date}, "
            f"Segredo de Justiça: {self.justice_secret}, "
            f"Distribuído em {self.distribution_date}, "
            f"Partes: {len(self.parties)}, "
            f"Movimentações: {len(self.movements)}"
        )

    def to_csv_export(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "Número do Processo": self.formatted_number,
            "Classe": self.class_,
            "Assunto": self.topic,
            "Jurisdição": self.jurisdiction,
            "Competência": self.competence,
            "Instância": self.instance,
            "Situação": self.situation,
            "Órgão Julgador": self.court,
            "Inquérito Policial": self.police_inquiry,
            "Valor da Causa": self.cause_value,
            "Data da Autuação": self.citation_date,
            "Segredo de Justiça": self.justice_secret,
            "Data de Distribuição": self.distribution_date,
            "Partes": "\n".join([str(party) for party in self.parties]),
            "Movimentações": "\n".join([str(m) for m in self.movements]),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "number": self.number,
            "formatted_number": self.formatted_number,
            "class": self.class_,
            "topic": self.topic,
            "jurisdiction": self.jurisdiction,
            "competence": self.competence,
            "cd_doc_process": self.cd_doc_process,
            "instance": self.instance,
            "cd_instance": self.cd_instance,
            "situation": self.situation,
            "court": self.court,
            "police_inquiry": self.police_inquiry,
            "cause_value": self.cause_value,
            "citation_date": self.citation_date,
            "justice_secret": self.justice_secret,
            "distribution_date": self.distribution_date,
            "parties": [party.to_dict() for party in self.parties],
            "movements": [m.to_dict() for m in self.movements],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Process":
        """
        Create a Process instance from API response data.
        """
        parties = [
            Party(name=party["nome"], party_type=party["tipo"])
            for party in data.get("partes", [])
        ]
        return cls(
            number=data.get("numero"),
            formatted_number=data.get("numeroFormatado"),
            class_=data.get("classe"),
            topic=data.get("assunto"),
            jurisdiction=data.get("comarca", ""),
            competence=data.get("competencia", ""),
            instance=data.get("instancia", ""),
            situation=data.get("situacao", ""),
            court=data.get("vara", ""),
            police_inquiry=data.get("numeroInqueritoPolicial", ""),
            cause_value=data.get("valorCausaFormatado", ""),
            citation_date=data.get("dataAutuacaoFormatada", ""),
            justice_secret=data.get("segredoJustica", ""),
            cd_doc_process=data.get("cdDocProcesso"),
            cd_instance=data.get("cdInstancia"),
            distribution_date=data.get("dataDistribuicaoFormatada"),
            parties=parties,
            movements=[],
        )
