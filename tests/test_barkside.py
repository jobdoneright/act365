import os

import httpx
import json5
import pytest

from act365.client import Act365Auth


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_act65_barkside():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")

    url = "https://userapi.act365.eu/api"

    auth = Act365Auth(username=username, password=password)
    with httpx.Client(auth=auth) as client:

        # Site ID: 8539 (Barkside Park)

        # Cardholder Groups: Full Access to Barkside Park (27470) (369 Cardholders assigned to this group)
        # Cardholder Groups: Full Access (27471) (3 Cardholders assigned to this group)

        # Cardholder: 21274334 (Simon McCartney), Email: simon@mccartney.ie, Card Number: 1003
        # Cardholder Validity Details:
        #    Enabled: True
        #    Valid From: 2024-01-06 11:00AM
        #    Valid To: 2024-01-06 12:00PM
        #

        # use the json5 library to parse the response.text, as apiary
        # responses have trailing commas
        params = {"siteid": "8539", "searchString": "Simon McCartney"}
        response = client.get(url + "/cardholder", params=params)

        assert response.status_code == httpx.codes.OK
        cardholders = json5.loads(response.text)
        assert isinstance(cardholders, list)
        assert len(cardholders) == 1
        cardholder = cardholders[0]
        assert cardholder.get("CardHolderID") == 21274334
        assert cardholder.get("StartValid") == "01/06/2024 11:00"
        assert cardholder.get("EndValid") == "01/06/2024 12:00"

        # Update the cardholder
        new_startvalid = "02/11/2024 21:00"
        new_endvalid = "02/11/2024 22:00"
        update_cardholder = dict()
        update_cardholder["CardHolderID"] = 21274334
        update_cardholder["StartValid"] = new_startvalid
        update_cardholder["EndValid"] = new_endvalid
        response = client.post(url=url + "/cardholder", data=update_cardholder)
        assert response.status_code == httpx.codes.OK

        # Get the cardholder again
        check_url = f"{url}/cardholder/{cardholder.get('CardHolderID')}"
        response = client.get(check_url)
        assert response.status_code == httpx.codes.OK
        cardholder = json5.loads(response.text)
        assert cardholder.get("CardHolderID") == 21274334
        assert cardholder.get("StartValid") == new_startvalid
        assert cardholder.get("EndValid") == new_endvalid


# TODO: Try using Event Booking API & generate a simple QR code?
