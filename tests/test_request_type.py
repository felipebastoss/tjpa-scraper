"""Tests for RequestType entity."""

import pytest
from urllib.parse import quote

from entities.request_type import RequestType
from exceptions import InvalidRequestError


class TestRequestTypeGetType:
    """Tests for RequestType.get_type method."""

    def test_cnj_formatted(self):
        """Test CNJ format with dashes and dots."""
        result = RequestType.get_type("0801234-56.2026.8.14.0301")
        assert result == RequestType.CNJ

    def test_cnj_unformatted(self):
        """Test CNJ format without formatting (20 digits)."""
        result = RequestType.get_type("08012345620268140301")
        assert result == RequestType.CNJ

    def test_cpf_unformatted(self):
        """Test CPF format without formatting (11 digits)."""
        result = RequestType.get_type("12345678901")
        assert result == RequestType.CPF

    def test_cpf_formatted(self):
        """Test CPF format with formatting."""
        result = RequestType.get_type("123.456.789-01")
        assert result == RequestType.CPF

    def test_cnpj_unformatted(self):
        """Test CNPJ format without formatting (14 digits)."""
        result = RequestType.get_type("12345678901234")
        assert result == RequestType.CNPJ

    def test_cnpj_formatted(self):
        """Test CNPJ format with formatting."""
        result = RequestType.get_type("12.345.678/9012-34")
        assert result == RequestType.CNPJ

    def test_oab(self):
        """Test OAB format."""
        result = RequestType.get_type("OAB:12345PA")
        assert result == RequestType.OAB

    def test_oab_lowercase(self):
        """Test OAB format in lowercase."""
        result = RequestType.get_type("oab:12345pa")
        assert result == RequestType.OAB

    def test_nome_parte(self):
        """Test party name format."""
        # Pattern requires: [letters]s[letters][optional more]
        result = RequestType.get_type("Jose Antonio")
        assert result == RequestType.NOME_PARTE

    def test_nome_parte_with_accents(self):
        """Test party name with Portuguese accents."""
        result = RequestType.get_type("José Antônio Ferreira")
        assert result == RequestType.NOME_PARTE

    def test_nome_parte_exato(self):
        """Test exact party name format (quoted)."""
        # Pattern requires: "[letters]s[letters][optional more]"
        result = RequestType.get_type('"Jose Antonio"')
        assert result == RequestType.NOME_PARTE_EXATO

    def test_inquerito(self):
        """Test police inquiry format."""
        result = RequestType.get_type("INQ:2026.12345")
        assert result == RequestType.INQ

    def test_inquerito_lowercase(self):
        """Test police inquiry format in lowercase."""
        result = RequestType.get_type("inq:2026.12345")
        assert result == RequestType.INQ

    def test_empty_string_raises_error(self):
        """Test that empty string raises InvalidRequestError."""
        with pytest.raises(InvalidRequestError) as exc_info:
            RequestType.get_type("")
        assert "vazia" in str(exc_info.value)

    def test_whitespace_only_raises_error(self):
        """Test that whitespace only string raises InvalidRequestError."""
        with pytest.raises(InvalidRequestError) as exc_info:
            RequestType.get_type("   ")
        assert "vazia" in str(exc_info.value)

    def test_single_name_raises_error(self):
        """Test that single name without surname raises InvalidRequestError."""
        with pytest.raises(InvalidRequestError) as exc_info:
            RequestType.get_type("João")
        assert "sobrenome" in str(exc_info.value)

    def test_invalid_format_raises_error(self):
        """Test that unrecognized format raises InvalidRequestError."""
        with pytest.raises(InvalidRequestError) as exc_info:
            RequestType.get_type("!@#$%")
        assert "não identificado" in str(exc_info.value)


class TestRequestTypeGetRouteByType:
    """Tests for RequestType.get_route_by_type method."""

    def test_cnj_route(self):
        """Test CNJ route."""
        assert RequestType.CNJ.get_route_by_type() == "/processobycnj/"

    def test_nome_parte_route(self):
        """Test party name route."""
        assert RequestType.NOME_PARTE.get_route_by_type() == "/processobynomeparte/"

    def test_nome_parte_exato_route(self):
        """Test exact party name route."""
        assert RequestType.NOME_PARTE_EXATO.get_route_by_type() == "/processobynomeparteexato/"

    def test_oab_route(self):
        """Test OAB route."""
        assert RequestType.OAB.get_route_by_type() == "/processobyoab/"

    def test_cpf_route(self):
        """Test CPF route."""
        assert RequestType.CPF.get_route_by_type() == "/processobycpf/"

    def test_cnpj_route(self):
        """Test CNPJ route."""
        assert RequestType.CNPJ.get_route_by_type() == "/processobycnpj/"

    def test_inq_route(self):
        """Test police inquiry route."""
        assert RequestType.INQ.get_route_by_type() == "/processobyinquerito/"


class TestRequestTypeGetRequestUrl:
    """Tests for RequestType.get_request_url method."""

    def test_cnj_url(self):
        """Test CNJ URL construction."""
        url = RequestType.CNJ.get_request_url("0801234-56.2026.8.14.0301")
        assert url == "/processobycnj/0801234-56.2026.8.14.0301"

    def test_nome_parte_url_encoded(self):
        """Test party name URL is URL-encoded."""
        url = RequestType.NOME_PARTE.get_request_url("João da Silva")
        assert quote("João da Silva") in url

    def test_nome_parte_exato_url_encoded(self):
        """Test exact party name URL is URL-encoded."""
        url = RequestType.NOME_PARTE_EXATO.get_request_url('"João da Silva"')
        assert quote('"João da Silva"') in url

    def test_url_with_system_name(self):
        """Test URL with system name."""
        url = RequestType.CNJ.get_request_url(
            "0801234-56.2026.8.14.0301", system_name="PROJUDI"
        )
        assert url == "/processobycnj/0801234-56.2026.8.14.0301/PROJUDI"

    def test_url_with_pagination(self):
        """Test URL with pagination parameters."""
        url = RequestType.CNJ.get_request_url(
            "0801234-56.2026.8.14.0301", page_number=2, page_size=50
        )
        assert url == "/processobycnj/0801234-56.2026.8.14.0301/2/50"

    def test_url_with_all_parameters(self):
        """Test URL with all parameters."""
        url = RequestType.CNJ.get_request_url(
            "0801234-56.2026.8.14.0301",
            system_name="PROJUDI",
            page_number=1,
            page_size=100,
        )
        assert url == "/processobycnj/0801234-56.2026.8.14.0301/PROJUDI/1/100"

    def test_cpf_url_forces_pagination(self):
        """Test CPF URL forces default pagination."""
        url = RequestType.CPF.get_request_url("12345678901")
        assert url == "/processobycpf/12345678901/1/1000"
