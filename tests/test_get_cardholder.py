"""Unit tests for the server-side single-cardholder fetch (GET /cardholder/{id}).

Uses pytest-httpx to mock both the auth login and the cardholder endpoint, so no
live ACT365 account is needed. The point of getCardholder is that a caller who
knows the CardHolderID pays one request instead of walking the whole directory.
"""

import pytest

from act365.client import Act365Client

BASE = "https://userapi.act365.eu/api"


@pytest.fixture
def login(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/account/login",
        json={
            "access_token": "test-token",
            "token_type": "bearer",
            "expires_in": 86399,
        },
    )


def _cardholder(**overrides):
    ch = {
        "CardHolderID": 123,
        "CustomerID": 5622,
        "SiteID": 8539,
        "Forename": "Test",
        "Surname": "Holder",
        "Email": "test@example.com",
        "Groups": [27470],
        "Cards": [1003],
    }
    ch.update(overrides)
    return ch


def _client():
    return Act365Client(username="u", password="p", siteid=8539)


def test_get_cardholder_found(login, httpx_mock):
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/cardholder/123", json=_cardholder()
    )

    ch = _client().getCardholder(123)

    assert ch is not None
    assert ch.CardHolderID == 123
    assert ch.Email == "test@example.com"


def test_get_cardholder_by_id_uses_single_endpoint_not_a_walk(login, httpx_mock):
    # Only the single-cardholder endpoint is registered; a full-directory walk
    # (GET /cardholder?skipover=...) would raise an unmatched-request error.
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/cardholder/123", json=_cardholder()
    )

    ch = _client().getCardholderById(123)

    assert ch is not None and ch.CardHolderID == 123


def test_get_cardholder_not_found_returns_none(login, httpx_mock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/cardholder/999", status_code=404)

    assert _client().getCardholder(999) is None


def test_get_cardholder_preserves_allsites_siteid(login, httpx_mock):
    # An all-sites (SiteID 0) cardholder must keep SiteID 0, mirroring
    # getCardholders. Rewriting it to the querying site makes a later
    # updateCardholder look like a cross-site move, which ACT365 rejects.
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/cardholder/123", json=_cardholder(SiteID=0)
    )

    ch = _client().getCardholder(123)

    assert ch is not None
    assert ch.SiteID == 0


def test_get_cardholder_round_trips_pin(login, httpx_mock):
    # ACT365 returns the stored PIN on GET, and a PUT with an empty/absent PIN
    # clears it — so the fetched object must carry the PIN through to dict()
    # for a safe fetch-modify-write update.
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/cardholder/123", json=_cardholder(PIN="4321")
    )

    ch = _client().getCardholder(123)

    assert ch is not None
    assert ch.PIN == "4321"
    assert ch.dict()["PIN"] == "4321"


def test_get_cardholder_empty_body_returns_none(login, httpx_mock):
    # An unknown id can answer 200 with an empty object rather than 404.
    httpx_mock.add_response(method="GET", url=f"{BASE}/cardholder/123", json={})

    assert _client().getCardholder(123) is None
