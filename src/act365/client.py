import logging
from time import sleep

import httpx
import json5

from act365.cardholder import CardHolder

# logging.basicConfig(filename="act365.log", filemode="w", level=logging.INFO)

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
LOG = logging.getLogger("act635")


class Act365Client:
    def __init__(
        self, username, password, siteid, url="https://userapi.act365.eu/api"
    ):
        self.username = username
        self.password = password
        self.siteid = siteid
        self.url = url

        self.auth = Act365Auth(username, password, url=url)
        self.client = httpx.Client(auth=self.auth)

        self._CardHolders = list()

    def getCardholders(self):
        response = self.client.get(self.url + "/cardholder")
        if response.status_code == httpx.codes.OK:
            cardholders = json5.loads(response.text)
            for ch in cardholders:
                self._CardHolders.append(CardHolder(ch))

    def getCardholderByEmail(self, email):
        self.getCardholders()
        for ch in self._CardHolders:
            if ch.Email.lower() == email.lower():
                return ch

    def post(self, url, data):
        return self.client.post(url, data=data)

    def put(self, url, data):
        return self.client.put(url, data=data)

    def delete(self, url):
        return self.client.delete(url)


class Act365Auth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        username,
        password,
        grant_type="password",
        url="https://userapi.act365.eu/api",
    ):

        if username is None or password is None:
            raise Exception
        self.username = username
        self.password = password
        self.grant_type = grant_type
        self.url = url

        self.access_token = None

    def get_token(self):
        data = {
            "grant_type": self.grant_type,
            "username": self.username,
            "password": self.password,
        }

        while self.access_token is None:
            # Set Content-Type: application/x-www-form-urlencoded via headers
            # as apiary complains about case mismatch
            response = httpx.post(
                self.url + "/account/login",
                data=data,
                timeout=90,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            LOG.debug(f"Response: {response.status_code} {response.text}")
            LOG.info(f"Response Headers: {response.headers}")

            if response.status_code == httpx.codes.OK:
                # "token_type":"bearer","expires_in":86399,
                # ".issued":"Wed, 24 Jul 2024 11:37:56 GMT",
                # ".expires":"Thu, 25 Jul 2024 11:37:56 GMT"}'
                self.access_token = response.json().get("access_token", None)
                self.token_type = response.json().get("token_type", None)
                self.expires_in = response.json().get("expires_in", None)
                self.issued = response.json().get(".issued", None)
                self.expires = response.json().get(".expires", None)
            elif response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                sleep(65)
            else:
                raise Exception

    def auth_flow(self, request):
        if self.access_token is None:
            self.get_token()

        request.headers["Authorization"] = "Bearer " + self.access_token
        response = yield request

        if response.status_code == 401:
            self.get_token()
            request.headers["Authorization"] = "Bearer " + self.access_token

            yield request
