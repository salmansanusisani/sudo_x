import pytest

from sudo_x.nmap_fixture import ScopePolicy, parse_fixture

FIXTURE = """
<nmaprun>
  <host><status state="up"/><address addr="192.0.2.10" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="8080"><state state="open"/><service name="http"/></port>
    </ports>
  </host>
</nmaprun>
"""


def test_fixture_parser_returns_scoped_evidence():
    result = parse_fixture(FIXTURE, ScopePolicy(("192.0.2.0/24",)))
    assert result.hosts[0].address == "192.0.2.10"
    assert result.hosts[0].ports[0].service == "http"
    assert result.scope == ("192.0.2.0/24",)


def test_fixture_rejects_out_of_scope_host():
    with pytest.raises(ValueError, match="outside the approved scope"):
        parse_fixture(
            FIXTURE.replace("192.0.2.10", "198.51.100.10"), ScopePolicy(("192.0.2.0/24",))
        )


@pytest.mark.parametrize("xml", ["<nmaprun>", "<evil/>", "x" * (256 * 1024 + 1)])
def test_fixture_rejects_invalid_or_oversized_xml(xml):
    with pytest.raises(ValueError):
        parse_fixture(xml, ScopePolicy(("192.0.2.0/24",)))


def test_fixture_rejects_invalid_port():
    xml = FIXTURE.replace('portid="8080"', 'portid="99999"')
    with pytest.raises(ValueError, match="invalid port"):
        parse_fixture(xml, ScopePolicy(("192.0.2.0/24",)))
