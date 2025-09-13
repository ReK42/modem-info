"""Abstract base classes and protocols for modem drivers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from httpx import Client

if TYPE_CHECKING:
    from ipaddress import IPv4Address, IPv6Address

    from pydantic import BaseModel


SCHEMES = [
    "http",
    "https",
]


class ModemDriverProtocol(Protocol):
    """Protocol for a generic modem driver."""

    @property
    def system_info(self) -> BaseModel:
        """Get basic system information from the modem."""
        ...

    @property
    def link_status(self) -> BaseModel:
        """Get link status from the modem."""
        ...


class DOCSISModemDriverProtocol(ModemDriverProtocol, Protocol):
    """Protocol for a generic DOCSIS modem driver."""

    @property
    def docsis_provisioning(self) -> BaseModel:
        """Get DOCSIS provisioning status from the modem."""
        ...

    @property
    def docsis_overview(self) -> BaseModel:
        """Get DOCSIS overview information from the modem."""
        ...

    @property
    def docsis_downstream(self) -> BaseModel:
        """Get DOCSIS downstream information from the modem."""
        ...

    @property
    def docsis_downstream_flattened(self) -> BaseModel:
        """Get flattened DOCSIS downstream information from the modem."""
        ...

    @property
    def docsis_downstream_ofdm(self) -> BaseModel:
        """Get DOCSIS downstream OFDM information from the modem."""
        ...

    @property
    def docsis_downstream_ofdm_flattened(self) -> BaseModel | None:
        """Get flattened DOCSIS downstream OFDM information from the modem."""
        ...

    @property
    def docsis_upstream(self) -> BaseModel:
        """Get DOCSIS upstream information from the modem."""
        ...

    @property
    def docsis_upstream_flattened(self) -> BaseModel:
        """Get flattened DOCSIS upstream information from the modem."""
        ...

    @property
    def docsis_upstream_ofdm(self) -> BaseModel:
        """Get DOCSIS upstream OFDM information from the modem."""
        ...

    @property
    def docsis_upstream_ofdm_flattened(self) -> BaseModel | None:
        """Get flattened DOCSIS upstream OFDM information from the modem."""
        ...

    @property
    def docsis_events(self) -> BaseModel | None:
        """Get DOCSIS events from the modem."""
        ...

    @property
    def docsis_statistics(self) -> BaseModel:
        """Get DOCSIS statistics from the modem."""
        ...

    @property
    def docsis_statistics_flattened(self) -> dict[str, Any]:
        """Get flattened DOCSIS statistics from the modem."""
        ...


class HTTPModemDriverProtocol(ModemDriverProtocol, Protocol):
    """Protocol for a generic HTTP-based modem driver."""

    address: IPv4Address | IPv6Address
    scheme: str
    params: dict[str, str]


class HTTPDOCSISModemDriverProtocol(HTTPModemDriverProtocol, DOCSISModemDriverProtocol, Protocol):
    """Protocol for a generic HTTP-based DOCSIS modem driver."""


class HTTPModemDriver:
    """Base class for a generic HTTP-based modem driver."""

    def __init__(
        self,
        address: IPv4Address | IPv6Address,
        scheme: str = "http",
        params: dict[str, str] | None = None,
    ) -> None:
        """Initialize the HTTP client to connect to the modem."""
        if scheme not in SCHEMES:
            msg = f"{scheme:!r} is not a value scheme"
            raise ValueError(msg)
        self.address = address
        self.scheme = scheme
        if params is None:
            self.params = {}
        else:
            self.params = params
        self._client = Client(base_url=f"{scheme}://{address}", params=params)
