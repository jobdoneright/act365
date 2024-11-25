import os

import pytest

from act365.cardholder import CardHolder
from act365.client import Act365Client

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


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_client():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")

    client = Act365Client(username=username, password=password, siteid=8539)

    cardholder = client.getCardholderByEmail("simon@mccartney.ie")

    assert cardholder.Forename == "Simon"
    assert cardholder.Surname == "McCartney"
