import os
from datetime import datetime, timedelta  # Add this import

import httpx
import json5
import pytest

from act365.client import Act365Auth


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_act365_barkside():
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
        assert cardholder.get("Email").lower() == "simon@mccartney.ie".lower()

        # Add an hour to the StartValid and EndValid times
        current_start_valid_dt = datetime.strptime(
            cardholder.get("StartValid"), "%d/%m/%Y %H:%M"
        )
        current_end_valid_dt = datetime.strptime(
            cardholder.get("EndValid"), "%d/%m/%Y %H:%M"
        )
        new_start_valid = (
            current_start_valid_dt + timedelta(hours=1)
        ).strftime("%d/%m/%Y %H:%M")
        new_end_valid = (current_end_valid_dt + timedelta(hours=1)).strftime(
            "%d/%m/%Y %H:%M"
        )

        # Update the cardholder
        update_cardholder = cardholder.copy()
        update_cardholder["StartValid"] = new_start_valid
        update_cardholder["EndValid"] = new_end_valid
        response = client.put(url=url + "/cardholder", data=update_cardholder)
        assert response.status_code == httpx.codes.OK
        api_response = json5.loads(response.text)
        assert api_response.get("Success") is True, api_response.get(
            "ErrorMsg"
        )
        assert (
            api_response.get("ErrorCode") == 0
        ), f"ErrorCode: {api_response.get('ErrorCode')}, ErrorMsg: {api_response.get('ErrorMsg')}"

        # Get the cardholder again
        check_url = f"{url}/cardholder/{cardholder.get('CardHolderID')}"
        response = client.get(check_url)
        assert response.status_code == httpx.codes.OK
        cardholder = json5.loads(response.text)
        assert cardholder.get("CardHolderID") == 21274334
        assert cardholder.get("StartValid") == new_start_valid
        assert cardholder.get("EndValid") == new_end_valid


# TODO: Try using Event Booking API & generate a simple QR code?


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_act365_create():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")

    url = "https://userapi.act365.eu/api"

    auth = Act365Auth(username=username, password=password)
    with httpx.Client(auth=auth) as client:
        # Site ID: 8539 (Barkside Park)
        cardholder = {
            "CustomerID": 5622,
            "SiteID": 8539,
            "Groups": [27470],
            "Forename": "Simon",
            "Surname": "McTest",
            "Enabled": True,
            "StartValid": "",
            "EndValid": "",
            "Email": "peter@mccartney.ie",
            "Cards": [],
        }

        response = client.post(url=url + "/cardholder", data=cardholder)
        assert response.status_code == httpx.codes.OK
        api_response = json5.loads(response.text)
        assert api_response.get("Success") is True, api_response.get(
            "ErrorMsg"
        )
        assert api_response.get("NewID") != 0, api_response.get("ErrorMsg")
        cardholder_id = api_response.get("NewID")

        assert (
            api_response.get("ErrorCode") == 0
        ), f"ErrorCode: {api_response.get('ErrorCode')}, ErrorMsg: {api_response.get('ErrorMsg')}"

        # Get the cardholder again
        check_url = f"{url}/cardholder/{cardholder_id}"
        response = client.get(check_url)
        assert response.status_code == httpx.codes.OK
        cardholder = json5.loads(response.text)
