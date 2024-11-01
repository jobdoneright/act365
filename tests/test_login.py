import httpx
import os
import pytest
import json5
from pprint import pprint as pp

from act365.client import Act365Auth

def test_act65_auth_failures():
    try:
        auth = Act365Auth(username=None, password=None)
    except Exception as e:
        assert type(e) == Exception

    try:
        auth = Act365Auth(username="bad", password="credenrials")
    except Exception as e:
        assert type(e) == Exception

@pytest.mark.skipif(os.getenv('ACT365_USERNAME') == None, reason="skip this test as ACT365_USERNAME is not set")
def test_act65_auth():
    username = os.getenv('ACT365_USERNAME')
    password = os.getenv('ACT365_PASSWORD')

    url = "https://userapi.act365.eu/api"

    auth = Act365Auth(username=username, password=password)
    with httpx.Client(auth=auth) as client:
        print("Summary:")
        response = client.get(url+"/summary")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Sites:")
        response = client.get(url+"/sites")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Card Holders:")
        response = client.get(url+"/cardholder")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))

        print("Bookingsites:")
        response = client.get(url+"/cardholder/22042028")
        assert response.status_code == httpx.codes.OK
        print(pp(response.json()))


def test_act65_auth_apiary():
    # you can use this with https://act365api.docs.apiary.io/traffic
    # to view the apiary traffic
    url = "https://private-3061cd-act365api.apiary-mock.com/api"
    username = "jeffrey.behan@act.eu"
    password = "thisismypassword"

    auth = Act365Auth(username=username, password=password, url=url)
    with httpx.Client(auth=auth) as client:
        print("Summary:")
        response = client.get(url+"/summary")
        assert response.status_code == httpx.codes.OK
        # use the json5 library to parse the response.text, as apiary has trailing commas
        summary = json5.loads(response.text)
        assert summary.get("ServiceUserType") == "Installer"
        assert isinstance(summary.get("MusteredCardHolders"), list)