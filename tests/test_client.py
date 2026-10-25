import pytest
import requests_mock

from rdap import client
from rdap.exceptions import RdapHTTPError


def test_strip_auth_none():
    url = "https://example.com/entity/20C"

    # test no auth
    assert url == client.strip_auth(url)


def test_strip_auth():
    url = "https://example.com/entity/20C/?key=value"

    # test no auth
    assert url == client.strip_auth(url)

    # test only auth
    assert url == client.strip_auth(url + "&apikey=12345")


def test_lacnic_bad_apikey():
    url = "https://rdap.lacnic.net/rdap/autnum/28001"
    rdapc = client.RdapClient({"lacnic_apikey": "12345",
                               "bootstrap_url": "https://rdap.lacnic.net/rdap"})
    with requests_mock.Mocker() as mock:
        mock.get(url, status_code=400)
        with pytest.raises(RdapHTTPError) as excinfo:
            rdapc.get_asn(28001)
        assert mock.last_request.qs["apikey"] == ["12345"]
    assert "returned 400" in str(excinfo.value)
    assert "12345" not in str(excinfo.value)


@pytest.mark.network
def test_lacnic_no_apikey(rdapc):
    assert rdapc.get_asn(28001).parsed()


@pytest.mark.network
def test_ignore_recurse_errors():
    rdapc = client.RdapClient({"lacnic_apikey": "12345", "ignore_recurse_errors": True})
    rdapc.get_asn(28001).parsed()


@pytest.mark.network
def test_asdomain_lookup(rdapc):
    rdapc.get("as63311.net")
