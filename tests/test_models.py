"""Tests for data models."""

from models.movement import Movement
from models.party import Party
from models.process import Process


class TestParty:
    """Tests for the Party model."""

    def test_creation(self):
        """Test Party instance creation."""
        party = Party(name="João da Silva", party_type="Autor")
        assert party.name == "João da Silva"
        assert party.party_type == "Autor"

    def test_str_representation(self):
        """Test Party string representation."""
        party = Party(name="Maria Santos", party_type="Réu")
        assert str(party) == "Maria Santos (Réu)"

    def test_to_dict(self):
        """Test Party to_dict method."""
        party = Party(name="Pedro Lima", party_type="Advogado")
        result = party.to_dict()

        assert result == {"name": "Pedro Lima", "type": "Advogado"}


class TestMovement:
    """Tests for the Movement model."""

    def test_creation(self):
        """Test Movement instance creation."""
        movement = Movement(
            date="01/02/2026", description="Juntada de petição"
        )
        assert movement.date == "01/02/2026"
        assert movement.description == "Juntada de petição"

    def test_str_representation(self):
        """Test Movement string representation."""
        movement = Movement(date="15/03/2026", description="Despacho")
        assert str(movement) == "15/03/2026: Despacho"

    def test_to_dict(self):
        """Test Movement to_dict method."""
        movement = Movement(
            date="20/04/2026", description="Sentença proferida"
        )
        result = movement.to_dict()

        assert result == {
            "date": "20/04/2026",
            "description": "Sentença proferida",
        }

    def test_from_dict(self):
        """Test Movement from_dict class method."""
        data = {
            "dataFormatada": "10/05/2026",
            "descricao": "Audiência realizada",
        }
        movement = Movement.from_dict(data)

        assert movement.date == "10/05/2026"
        assert movement.description == "Audiência realizada"

    def test_from_dict_with_missing_keys(self):
        """Test Movement from_dict with missing keys returns None values."""
        data = {}
        movement = Movement.from_dict(data)

        assert movement.date is None
        assert movement.description is None


class TestProcess:
    """Tests for the Process model."""

    def test_creation(self, sample_party, sample_movement):
        """Test Process instance creation."""
        process = Process(
            formatted_number="0801234-56.2026.8.14.0301",
            number="08012345620268140301",
            class_="Ação Civil Pública",
            topic="Direito Ambiental",
            cd_doc_process="12345",
            cd_instance="1",
            parties=[sample_party],
            movements=[sample_movement],
            jurisdiction="Belém",
            competence="Cível",
            instance="1º Grau",
            situation="Em andamento",
            court="1ª Vara Cível",
            police_inquiry="",
            cause_value="R$ 100.000,00",
            citation_date="01/01/2026",
            justice_secret="Não",
            distribution_date="01/01/2026",
        )

        assert process.number == "08012345620268140301"
        assert process.formatted_number == "0801234-56.2026.8.14.0301"
        assert process.class_ == "Ação Civil Pública"
        assert len(process.parties) == 1
        assert len(process.movements) == 1

    def test_str_representation(self, sample_process):
        """Test Process string representation."""
        result = str(sample_process)

        assert "0801234-56.2026.8.14.0301" in result
        assert "Ação Civil Pública" in result
        assert "Direito Ambiental" in result
        assert "Partes: 1" in result
        assert "Movimentações: 1" in result

    def test_to_csv_export(self, sample_process):
        """Test Process to_csv_export method."""
        result = sample_process.to_csv_export()

        assert result["Número do Processo"] == "0801234-56.2026.8.14.0301"
        assert result["Classe"] == "Ação Civil Pública"
        assert result["Assunto"] == "Direito Ambiental"
        assert result["Jurisdição"] == "Belém"
        assert "João da Silva (Autor)" in result["Partes"]
        assert "01/02/2026: Juntada de petição" in result["Movimentações"]

    def test_to_dict(self, sample_process):
        """Test Process to_dict method."""
        result = sample_process.to_dict()

        assert result["number"] == "08012345620268140301"
        assert result["formatted_number"] == "0801234-56.2026.8.14.0301"
        assert result["class"] == "Ação Civil Pública"
        assert result["topic"] == "Direito Ambiental"
        assert len(result["parties"]) == 1
        assert len(result["movements"]) == 1
        assert result["parties"][0]["name"] == "João da Silva"
        assert result["movements"][0]["date"] == "01/02/2026"

    def test_from_dict(self, sample_api_process_response):
        """Test Process from_dict class method."""
        process = Process.from_dict(sample_api_process_response)

        assert process.number == "08012345620268140301"
        assert process.formatted_number == "0801234-56.2026.8.14.0301"
        assert process.class_ == "Ação Civil Pública"
        assert process.topic == "Direito Ambiental"
        assert process.jurisdiction == "Belém"
        assert len(process.parties) == 1
        assert process.parties[0].name == "João da Silva"
        assert process.movements == []  # movements are empty by default

    def test_from_dict_with_missing_optional_fields(self):
        """Test Process from_dict with minimal required fields."""
        data = {
            "numero": "12345",
            "numeroFormatado": "1234-5",
            "classe": "Classe",
            "assunto": "Assunto",
            "cdDocProcesso": "999",
            "cdInstancia": "1",
        }
        process = Process.from_dict(data)

        assert process.number == "12345"
        assert process.jurisdiction == ""  # default empty string
        assert process.competence == ""
        assert process.parties == []
