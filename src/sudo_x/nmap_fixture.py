"""Offline Nmap XML fixture parser; never launches Nmap or performs network I/O."""

import ipaddress
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

MAX_XML_BYTES = 256 * 1024
MAX_HOSTS = 32
MAX_PORTS_PER_HOST = 64


class NmapPort(BaseModel):
    model_config = ConfigDict(frozen=True)

    port: int = Field(ge=1, le=65535)
    protocol: str = Field(pattern=r"^(tcp|udp)$")
    state: str = Field(pattern=r"^(open|closed|filtered|open\|filtered|unfiltered)$")
    service: str | None = None


class NmapHost(BaseModel):
    model_config = ConfigDict(frozen=True)

    address: str
    status: str = Field(pattern=r"^(up|down|unknown)$")
    ports: tuple[NmapPort, ...]


class NmapFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    hosts: tuple[NmapHost, ...]
    scope: tuple[str, ...]
    source: str = "offline_fixture"


@dataclass(frozen=True)
class ScopePolicy:
    allowed_networks: tuple[str, ...]

    def contains(self, address: str) -> bool:
        ip = ipaddress.ip_address(address)
        return any(
            ip in ipaddress.ip_network(network, strict=False)
            for network in self.allowed_networks
        )


def parse_fixture(xml: str | bytes, policy: ScopePolicy) -> NmapFixture:
    raw = xml.encode() if isinstance(xml, str) else xml
    if len(raw) > MAX_XML_BYTES:
        raise ValueError("Nmap fixture exceeds the allowed size.")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("Nmap fixture is not valid XML.") from exc
    if root.tag != "nmaprun":
        raise ValueError("Nmap fixture must have an nmaprun root.")
    hosts: list[NmapHost] = []
    for host_element in root.findall("host"):
        if len(hosts) >= MAX_HOSTS:
            raise ValueError("Nmap fixture exceeds the host limit.")
        address_element = host_element.find("address")
        address = address_element.get("addr") if address_element is not None else None
        if not address:
            raise ValueError("Nmap host has no address.")
        try:
            ipaddress.ip_address(address)
        except ValueError as exc:
            raise ValueError("Nmap host address is invalid.") from exc
        if not policy.contains(address):
            raise ValueError("Nmap fixture contains an address outside the approved scope.")
        status_element = host_element.find("status")
        state = status_element.get("state", "unknown") if status_element is not None else "unknown"
        ports: list[NmapPort] = []
        for port_element in host_element.findall("./ports/port"):
            if len(ports) >= MAX_PORTS_PER_HOST:
                raise ValueError("Nmap fixture exceeds the port limit.")
            protocol = port_element.get("protocol", "")
            port_id = port_element.get("portid", "")
            state_element = port_element.find("state")
            port_state = state_element.get("state", "") if state_element is not None else ""
            service_element = port_element.find("service")
            service = service_element.get("name") if service_element is not None else None
            try:
                ports.append(NmapPort(
                    port=int(port_id), protocol=protocol, state=port_state, service=service
                ))
            except (TypeError, ValueError) as exc:
                raise ValueError("Nmap fixture contains an invalid port record.") from exc
        hosts.append(NmapHost(address=address, status=state, ports=tuple(ports)))
    return NmapFixture(hosts=tuple(hosts), scope=policy.allowed_networks)
