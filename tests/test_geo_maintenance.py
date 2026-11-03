import pytest

import rdap.normalize.geo as geo
from rdap.context import RdapRequestContext, RdapRequestState, rdap_request
from rdap.schema.normalized import Location


class FakeClient:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def geocode(self, address):
        self.calls += 1
        return self.result


def _reset_state():
    token = rdap_request.set(RdapRequestState())
    return token


def test_normalize_is_quiet_and_returns_expected_fields(capsys):
    token = _reset_state()
    try:
        fake = FakeClient(
            [
                {
                    "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
                    "address_components": [
                        {
                            "long_name": "Mountain View",
                            "short_name": "Mountain View",
                            "types": ["locality", "political"],
                        },
                        {
                            "long_name": "94043",
                            "short_name": "94043",
                            "types": ["postal_code"],
                        },
                        {
                            "long_name": "United States",
                            "short_name": "US",
                            "types": ["country", "political"],
                        },
                    ],
                    "geometry": {
                        "location": {"lat": 37.422, "lng": -122.084}
                    },
                }
            ]
        )

        location = geo.normalize("1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA", client=fake)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        assert isinstance(location, Location)
        assert location.city == "Mountain View"
        assert location.postal_code == "94043"
        assert location.country == "US"
        assert location.address == "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA"
        assert location.geo is not None
        assert location.geo.latitude == 37.422
        assert location.geo.longitude == -122.084

        # cache hit: second call must not re-invoke the client
        location2 = geo.normalize("1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA", client=fake)
        assert fake.calls == 1
        assert location2.city == "Mountain View"
        assert capsys.readouterr().out == ""
    finally:
        rdap_request.reset(token)


def test_normalize_empty_components_is_quiet(capsys):
    token = _reset_state()
    try:
        fake = FakeClient(
            [
                {
                    "formatted_address": "Somewhere 1",
                    "address_components": [],
                    "geometry": {"location": {"lat": 1.0, "lng": 2.0}},
                }
            ]
        )

        location = geo.normalize("Somewhere 1", client=fake)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        assert location.address == "Somewhere 1"
        assert location.city is None
        assert location.country is None
        assert location.postal_code is None
        assert location.geo is not None
        assert location.geo.latitude == 1.0
        assert location.geo.longitude == 2.0
    finally:
        rdap_request.reset(token)


def test_normalize_no_key_falls_back_to_address_only(capsys, monkeypatch):
    token = _reset_state()
    try:
        def raise_no_key():
            raise geo.GoogleKeyNotSet("Google Maps API Key not set")

        monkeypatch.setattr(geo, "get_client", raise_no_key)

        location = geo.normalize("No Key Street 1")

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        assert isinstance(location, Location)
        assert location.address == "No Key Street 1"
        assert location.city is None
        assert location.country is None
        assert location.geo is None
    finally:
        rdap_request.reset(token)
