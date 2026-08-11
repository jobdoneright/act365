"""Unit tests for timeout configuration and the single timeout retry.

ACT365's backend has been observed taking 15s+ per request overnight, so the
client carries a generous default read timeout and retries idempotent requests
(GETs, the full-overwrite cardholder PUT) once on timeout. Non-idempotent
creation POSTs are never retried: a timed-out request may still have been
applied server-side.

pytest-httpx intercepts at HTTPTransport.handle_request, above the transport's
connect-retry layer, so a mocked timeout exercises exactly one application-level
retry.
"""

import httpx
import pytest

from act365.client import DEFAULT_TIMEOUT, Act365Auth, Act365AuthError, Act365Client

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


@pytest.fixture
def no_retry_sleep(monkeypatch):
    monkeypatch.setattr("act365.client.sleep", lambda seconds: None)


def _client(**kwargs):
    return Act365Client(username="u", password="p", siteid=8539, **kwargs)


def _cardholder():
    return {
        "CardHolderID": 123,
        "CustomerID": 5622,
        "SiteID": 8539,
        "Forename": "Test",
        "Surname": "Holder",
        "Email": "test@example.com",
        "Groups": [27470],
        "Cards": [1003],
    }


def test_default_timeout_is_generous():
    client = _client()
    assert client.client.timeout == DEFAULT_TIMEOUT
    assert DEFAULT_TIMEOUT.read == 30.0
    assert DEFAULT_TIMEOUT.connect == 10.0


def test_timeout_kwarg_overrides_default():
    custom = httpx.Timeout(3.0)
    client = _client(timeout=custom)
    assert client.client.timeout == custom


def test_get_cardholder_retries_once_on_timeout(login, httpx_mock, no_retry_sleep):
    httpx_mock.add_exception(
        httpx.ReadTimeout("timed out"), method="GET", url=f"{BASE}/cardholder/123"
    )
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/cardholder/123", json=_cardholder()
    )

    ch = _client().getCardholder(123)

    assert ch is not None
    assert ch.CardHolderID == 123


def test_get_cardholder_raises_after_second_timeout(login, httpx_mock, no_retry_sleep):
    httpx_mock.add_exception(
        httpx.ReadTimeout("timed out"), method="GET", url=f"{BASE}/cardholder/123"
    )
    httpx_mock.add_exception(
        httpx.ReadTimeout("timed out again"), method="GET", url=f"{BASE}/cardholder/123"
    )

    with pytest.raises(httpx.ReadTimeout):
        _client().getCardholder(123)


def test_connect_timeout_is_not_retried_by_the_helper(
    login, httpx_mock, no_retry_sleep
):
    # Connect timeouts are the transport's job (HTTPTransport(retries=2)) and
    # must otherwise fail fast — the helper retries only read timeouts.
    httpx_mock.add_exception(
        httpx.ConnectTimeout("connect timed out"),
        method="GET",
        url=f"{BASE}/cardholder/123",
    )

    with pytest.raises(httpx.ConnectTimeout):
        _client().getCardholder(123)

    gets = [r for r in httpx_mock.get_requests() if r.method == "GET"]
    assert len(gets) == 1


def test_update_cardholder_retries_once_on_timeout(login, httpx_mock, no_retry_sleep):
    httpx_mock.add_exception(
        httpx.ReadTimeout("timed out"), method="PUT", url=f"{BASE}/cardholder"
    )
    httpx_mock.add_response(
        method="PUT", url=f"{BASE}/cardholder", json={"Success": True}
    )

    assert _client().updateCardholder(_cardholder()) is True


def test_create_cardholder_is_not_retried_on_timeout(login, httpx_mock, no_retry_sleep):
    httpx_mock.add_exception(
        httpx.ReadTimeout("timed out"), method="POST", url=f"{BASE}/cardholder"
    )

    with pytest.raises(httpx.ReadTimeout):
        _client().createCardholder(_cardholder())

    creates = [
        r for r in httpx_mock.get_requests() if r.url.path.endswith("/cardholder")
    ]
    assert len(creates) == 1


def test_login_failure_raises_typed_error(httpx_mock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/account/login", status_code=400, text="bad creds"
    )

    auth = Act365Auth(username="bad", password="credentials")
    with pytest.raises(Act365AuthError, match="login failed: 400"):
        auth.get_token()
