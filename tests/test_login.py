import os
from pprint import pprint as pp

import httpx
import json5
import pytest

from act365.client import Act365Auth


def test_act65_auth_failures():
    try:
        _ = Act365Auth(username=None, password=None)
    except Exception as e:
        assert type(e) is Exception

    try:
        _ = Act365Auth(username="bad", password="credenrials")
    except Exception as e:
        assert type(e) is Exception


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None,
    reason="skip this test as ACT365_USERNAME is not set",
)
def test_act365_auth():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")

    url = "https://userapi.act365.eu/api"

    auth = Act365Auth(username=username, password=password)
    with httpx.Client(auth=auth) as client:
        print("Summary:")
        response = client.get(url + "/summary")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Sites:")
        response = client.get(url + "/sites")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Card Holders:")
        response = client.get(url + "/cardholder")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Bookingsites:")
        response = client.get(url + "/cardholder/22042028")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))


def test_act365_apiary():
    # you can use this with https://act365api.docs.apiary.io/traffic
    # to view the apiary traffic
    url = "https://private-3061cd-act365api.apiary-mock.com/api"
    username = "jeffrey.behan@act.eu"
    password = "thisismypassword"

    auth = Act365Auth(username=username, password=password, url=url)
    with httpx.Client(auth=auth) as client:
        print("Summary:")
        response = client.get(url + "/summary")
        assert response.status_code == httpx.codes.OK
        # use the json5 library to parse the response.text, as apiary
        # responses have trailing commas
        summary = json5.loads(response.text)
        assert summary.get("ServiceUserType") == "Installer"
        assert isinstance(summary.get("MusteredCardHolders"), list)

        params = {"siteid": "8539", "searchString": "Simon McCartney"}
        response = client.get(url + "/cardholder", params=params)

        assert response.status_code == httpx.codes.OK
        cardholders = json5.loads(response.text)
        assert isinstance(cardholders, list)
        assert len(cardholders) == 1
        cardholder = cardholders[0]

        # Update the cardholder
        new_startvalid = "02/11/2024 21:00"
        new_endvalid = "02/11/2024 22:00"
        update_cardholder = cardholder.copy()
        update_cardholder["StartValid"] = new_startvalid
        update_cardholder["EndValid"] = new_endvalid
        response = client.put(url=url + "/cardholder", data=update_cardholder)
        assert response.status_code == httpx.codes.OK
        api_response = json5.loads(response.text)
        assert api_response.get("Success") is True, api_response.get(
            "ErrorMsg"
        )
        # f"ErrorCode: {api_response.get("ErrorCode")}, ErrorMsg: {api_response.get('ErrorMsg')}"
        assert api_response.get("ErrorCode", -1) == 0
