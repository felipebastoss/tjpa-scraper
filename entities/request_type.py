"""Module defining the RequestType class for identifying and handling different types of legal process requests."""

import re
from enum import Enum
from urllib.parse import quote

from exceptions import InvalidRequestError


class RequestType(Enum):
    """Class to identify and handle different types of legal process requests."""

    CNJ = "Numero do CNJ"
    NOME_PARTE = "Nome da Parte"
    NOME_PARTE_EXATO = "Nome da Parte Exato"
    OAB = "Numero da OAB"
    CPF = "Numero do CPF"
    CNPJ = "Numero do CNPJ"
    INQ = "Inquerito Policial"

    @classmethod
    def _get_patterns(cls) -> dict:
        patterns = {
            cls.CNJ: re.compile(
                r"^[0-9]{7}-[0-9]{2}.[0-9]{4}.[0-9]{1}.[0-9]{2}.[0-9]{4}$|^[0-9]{20}$"
            ),
            cls.CPF: re.compile(r"^[0-9]{11}$|^[0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2}$"),
            cls.CNPJ: re.compile(
                r"^[0-9]{14}$|^[0-9]{2}.[0-9]{3}.[0-9]{3}/[0-9]{4}-[0-9]{2}$"
            ),
            cls.OAB: re.compile(r"^(OAB):*[0-9]{1,}[a-zA-Z]{2}$", re.IGNORECASE),
            cls.NOME_PARTE: re.compile(
                r"^[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}s{1,2}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7\- ]{0,}.{0,}$",
                re.IGNORECASE,
            ),
            cls.NOME_PARTE_EXATO: re.compile(
                r"^\"[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}s{1,2}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7\- ]{0,}\"$",
                re.IGNORECASE,
            ),
            cls.INQ: re.compile(r"^(inq):[0-9]{4}.[0-9]{1,}$", re.IGNORECASE),
            "SINGLE_NAME": re.compile(
                r"^\"s{0,}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}s{0,1}\"$|^s{0,}[a-zA-Z\xf5\xe3\xe1\xed\xf3\xfa\xe9\xf4\xea\xe2\xe7-]{1,}s{0,1}$",
                re.IGNORECASE,
            ),
        }
        return patterns

    @classmethod
    def get_type(cls, request: str) -> "RequestType":
        """
        Identify the type of request based on the input string.

        Args:
            request: The search query string

        Returns:
            The identified RequestType

        Raises:
            InvalidRequestError: If the request format is not recognized
        """
        request = request.strip()
        if not request:
            raise InvalidRequestError("A busca não pode estar vazia.")

        patterns = cls._get_patterns()

        for request_type in RequestType:
            if patterns.get(request_type).match(request):
                return request_type

        if patterns.get("SINGLE_NAME").match(request):
            raise InvalidRequestError(
                "Nome da Parte deve conter ao menos um sobrenome."
            )

        raise InvalidRequestError(
            f"Tipo de requisição não identificado: '{request}'. "
            "Formatos aceitos: CNJ, CPF, CNPJ, OAB, Nome da Parte, Inquérito."
        )

    def get_route_by_type(self) -> str:
        """Get the API route corresponding to the request type."""
        match self:
            case RequestType.CNJ:
                return "/processobycnj/"
            case RequestType.NOME_PARTE:
                return "/processobynomeparte/"
            case RequestType.NOME_PARTE_EXATO:
                return "/processobynomeparteexato/"
            case RequestType.OAB:
                return "/processobyoab/"
            case RequestType.CPF:
                return "/processobycpf/"
            case RequestType.CNPJ:
                return "/processobycnpj/"
            case RequestType.INQ:
                return "/processobyinquerito/"

    def get_request_url(
        self,
        request_data: str,
        system_name: str = None,
        page_number: int = None,
        page_size: int = None,
    ) -> str:
        """Construct the full API request URL based on the request type and parameters."""
        route = self.get_route_by_type()
        if route is None:
            raise ValueError("Tipo de requisição inválido para construção da URL.")
        if self in [RequestType.NOME_PARTE, RequestType.NOME_PARTE_EXATO]:
            request_data = quote(request_data)
        if self not in [RequestType.NOME_PARTE, RequestType.CNJ]:
            page_number = 1
            page_size = 1000
        url = f"{route}{request_data}"
        if self is RequestType.OAB:
            match = re.search(r"(\d+)([a-z]{2})$", request_data, re.IGNORECASE)
            if match:
                oab_number = match.group(1)
                oab_state = match.group(2).upper()
                url = f"{route}{oab_number}/OAB-{oab_state}"
        if system_name:
            url += f"/{system_name}"
        if page_number:
            url += f"/{page_number}"
        if page_size:
            url += f"/{page_size}"
        return url
