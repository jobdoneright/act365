import os

import pytest

from act365.cardholder import CardHolder
from act365.client import Act365Client

me = {
    "CardHolderID": 21274334,
    "CustomerID": 5622,
    "SiteID": 8539,
    "Forename": "Simon",
    "Surname": "McCartney",
    "Groups": [27470],
    "Card1": 1003,
}

rt = {
    "StartValid": "15/03/2016 16:45",
    "EndValid": "15/03/2016 18:00",
}


def test_cardholder():
    cardholder = CardHolder(
        {
            "CustomerID": 5622,
            "SiteID": 8539,
            "Groups": [27470],
            "Forename": "Simon",
            "Surname": "McCartney",
            "Email": "simon@mccartney.ie",
        }
    )
    assert cardholder.Forename == "Simon"
    assert cardholder.Surname == "McCartney"
    assert cardholder.Email == "simon@mccartney.ie"

    # setter & getter should always return an API friendly format
    assert cardholder.StartValid == ""
    assert cardholder.EndValid == ""

    cardholder.StartValid = rt["StartValid"]
    cardholder.EndValid = rt["EndValid"]
    assert cardholder.StartValid == rt["StartValid"]
    assert cardholder.EndValid == rt["EndValid"]


@pytest.fixture
def act365_client():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")
    return Act365Client(username=username, password=password, siteid=8539)


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_client_simon(act365_client):
    params = {"siteid": 8539, "maxlimit": 2, "searchstring": "Simon McCartney"}
    cardholders = act365_client.getCardholders(params=params)
    assert cardholders[0].CardHolderID == 21274334
    assert cardholders[0].Forename == "Simon"


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_client_morethan2(act365_client):
    cardholders = act365_client.getCardholders()
    print(f"CardHolders returned: {len(cardholders)}")
    assert len(cardholders) > 2


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_get_by_email(act365_client):
    cardholder = act365_client.getCardholderByEmail("simon@mccartney.ie")

    assert cardholder.Forename == "Simon"
    assert cardholder.Surname == "McCartney"


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_get_by_email_1410(act365_client):
    cardholder1410 = act365_client.getCardholderByEmail("araclay@hotmail.com")
    assert cardholder1410.Forename == "Aidan"
    assert cardholder1410.Surname == "McMurray "
    assert cardholder1410.Card1 == 1410


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_get_by_id(act365_client):
    cardholder1410 = act365_client.getCardholderById(32047402)
    assert cardholder1410.Forename == "Aidan"
    assert cardholder1410.Surname == "McMurray "
    assert cardholder1410.Card1 == 1410
