import json
import logging
from datetime import datetime
from time import sleep

import httpx

from act365.booking import Booking, BookingDoor, BookingSite
from act365.cardholder import CardHolder

logging.basicConfig(
    format="%(asctime)s %(levelname)-5s %(module)-10s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.ERROR,
)
LOG = logging.getLogger(__name__)


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

    def getCardholders(self, params={}):
        # ?customerid={customerid}
        # &siteid={siteid}
        # &maxlimit={maxlimit}
        # &skipover={skipover}
        # &enabled={enabled}
        # &externalId=externalid
        # &searchString={searchstring}'
        # params["siteid"] = self.siteid
        # lowercase all keys
        params = {k.lower(): v for k, v in params.items()}

        self._CardHolders = list()

        more_to_get = True
        while more_to_get:
            params["skipover"] = len(self._CardHolders)
            response = self.client.get(self.url + "/cardholder", params=params)

            if response.status_code == httpx.codes.OK:
                cardholders = json.loads(response.text)

                if len(cardholders) == 0:
                    more_to_get = False

                for ch in cardholders:
                    self._CardHolders.append(CardHolder(ch))

            else:
                more_to_get = False

        return self._CardHolders

    def getCardholderByEmail(self, email):
        self.getCardholders()
        for ch in self._CardHolders:
            if ch.Email.lower() == email.lower():
                return ch

    def getCardholderById(self, id):
        self.getCardholders()
        for ch in self._CardHolders:
            if ch.CardHolderID == id:
                return ch

    def getBookingSites(self, maxlimit=100, skipover=0):
        params = {"maxlimit": maxlimit, "skipover": skipover}

        sites = list()

        more_to_get = True
        while more_to_get:
            params["skipover"] = len(sites)
            response = self.client.get(
                self.url + "/Bookingsites", params=params
            )

            if response.status_code == httpx.codes.OK:
                _sites = json.loads(response.text)

                if len(_sites) == 0:
                    more_to_get = False

                for site in _sites:
                    sites.append(BookingSite(**site))

            else:
                more_to_get = False

        return sites

    def getBookingSiteDoors(self, siteid):
        response = self.client.get(
            self.url + "/Bookingdoors", params={"siteid": siteid}
        )

        if response.status_code == httpx.codes.OK:
            doors = [BookingDoor(**door) for door in json.loads(response.text)]

        return doors

    def createBooking(self, booking: Booking | dict):
        if isinstance(booking, dict):
            data = booking
        elif isinstance(booking, Booking):
            data = booking.dict()
        else:
            raise TypeError("booking must be a Booking object or a dictionary")

        response = self.client.post(self.url + "/Bookings", data=data)
        return response

    def getBookings(self, siteid, datefrom=None):
        if datefrom is None:
            datefrom = datetime.now().strftime("%d/%m/%Y")

        params = {"siteid": siteid, "date": datefrom}
        results = self._getAll("/getbookings", params=params)

        bookings = [Booking(**booking) for booking in results]

        return bookings

    def deleteBooking(self, bookingid):
        response = self.client.delete(
            self.url + "2/Bookings", params={"bookingID": f"{bookingid}"}
        )
        return response

    def _getAll(self, path, params={}, maxlimit=100):
        params["maxlimit"] = maxlimit

        results = list()

        more_to_get = True
        while more_to_get:
            params["skipover"] = len(results)
            response = self.client.get(self.url + path, params=params)

            if response.status_code == httpx.codes.OK:
                rs = json.loads(response.text)

                if len(rs) == 0:
                    more_to_get = False

                for r in rs:
                    results.append(r)

            else:
                more_to_get = False

        return results

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
