import json
import os
from datetime import datetime, timedelta
from random import randint

import pytest

from act365.booking import STRPTIME_FMT, Booking
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

sample = {
    # "BookingID": 74565,
    "SiteID": 8539,
    "Forename": "Simon",
    "Surname": "McCartney",
    "PIN": "0034",
    "Card": 0,
    "StartValidity": "15/03/2016 16:45",
    "EndValidity": "15/03/2016 18:00",
    "ToggleMode": False,
    "DoorIDs": [14247],
}


@pytest.fixture()
def act365_client():
    username = os.getenv("ACT365_USERNAME")
    password = os.getenv("ACT365_PASSWORD")
    return Act365Client(username=username, password=password, siteid=8539)


class _FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.text = json.dumps(payload)


def test_get_cardholders_preserves_true_siteid(monkeypatch):
    # ACT365's list endpoint returns SiteID 0 for all-sites/global cardholders.
    # getCardholders must return that 0 unchanged, not rewrite it to the
    # client's own site (8539) — doing so corrupts global cardholders and makes
    # a later update look like a rejected cross-site move.
    client = Act365Client(username="u", password="p", siteid=8539)
    pages = [
        [
            {"CardHolderID": 1, "CustomerID": 5622, "SiteID": 0, "Groups": [1]},
            {"CardHolderID": 2, "CustomerID": 5622, "SiteID": 9000, "Groups": [1]},
        ],
        [],
    ]
    calls = iter(pages)
    monkeypatch.setattr(
        client.client, "get", lambda *a, **k: _FakeResponse(next(calls))
    )

    holders = {ch.CardHolderID: ch for ch in client.getCardholders()}

    assert holders[1].SiteID == 0
    assert holders[2].SiteID == 9000


@pytest.mark.skipif(
    os.getenv("ACT365_USERNAME") is None
    or os.getenv("ACT365_PASSWORD") is None,  # noqa: W503
    reason="skip this test as ACT365_USERNAME is not set",
)
class TestBookingClient:
    def test_booking_sites(self, act365_client):
        sites = act365_client.getBookingSites()
        assert len(sites) > 0
        assert sites[0].ID == 8539
        site = sites[0]
        assert site.ID == 8539

    def test_booking_doors(self, act365_client):
        doors = act365_client.getBookingSiteDoors(me.get("SiteID"))
        assert len(doors) > 0
        door = doors[0]
        assert door.ID == 14247

    def test_get_bookings(self, act365_client):
        # create a booking
        self.test_create_booking(act365_client)

        bookings = act365_client.getBookings(me.get("SiteID"), datefrom="01/01/2000")
        assert len(bookings) > 0
        assert bookings[0].BookingID > 0

    def test_create_booking(self, act365_client):
        sample["PIN"] = f"{randint(0, 9999):04d}"
        booking = Booking(**sample)
        response = act365_client.createBooking(booking)
        assert response.json().get("Success") is True
        assert response.json().get("BookingID") > 0
        assert response.json().get("Message") is None

    def test_get_booking(self, act365_client):
        bookings = act365_client.getBookings(me.get("SiteID"), datefrom="01/01/2000")
        booking = act365_client.getBooking(me.get("SiteID"), bookings[0].BookingID)
        assert booking.BookingID == bookings[0].BookingID

    def test_get_booking_missing(self, act365_client):
        b = act365_client.getBooking(me.get("SiteID"), 999999)
        assert b is None

    def test_create_bookingRAW(self, act365_client):
        booking = {
            "SiteID": 8539,
            "Forename": "Simon",
            "Surname": "McCartney",
            "PIN": "0034",
            "Card": 0,
            "StartValidity": "15/03/2016 16:45",
            "EndValidity": "15/03/2016 18:00",
            "ToggleMode": False,
            "DoorIDs": 14247,
        }
        booking["PIN"] = f"{randint(0, 9999):04d}"
        response = act365_client.createBooking(booking)
        assert response.json().get("Success") is True
        assert response.json().get("BookingID") > 0
        assert response.json().get("Message") is None

    def test_booking_deleteall(self, act365_client):
        # bookings = act365_client.getBookings(me.get("SiteID"))
        bookings = act365_client.getBookings(me.get("SiteID"), datefrom="01/01/2021")

        for booking in bookings:
            response = act365_client.deleteBooking(booking.BookingID)
            assert response.json().get("Success") is True

    def test_booking_workflow(self, act365_client):
        now = datetime.now()
        startvalid = now.strftime(STRPTIME_FMT)
        endvalid = (now + timedelta(hours=1)).strftime(STRPTIME_FMT)

        PIN = f"{randint(0, 9999):04d}"

        booking_dict = {
            "SiteID": me.get("SiteID"),
            "Forename": "Simon",
            "Surname": "McCartney",
            "PIN": PIN,
            "Card": 0,
            "StartValidity": startvalid,
            "EndValidity": endvalid,
            "ToggleMode": False,
            "DoorIDs": [14247],
        }

        booking = Booking(**booking_dict)
        response = act365_client.createBooking(booking)
        assert response.json().get("Success") is True
        assert response.json().get("BookingID") > 0

        r = act365_client.getBooking(me.get("SiteID"), response.json().get("BookingID"))
        assert r.BookingID == response.json().get("BookingID")
        assert r.Forename == booking_dict.get("Forename")
        # ACT365 appents a unique number to the surname
        assert r.Surname.startswith(booking_dict.get("Surname"))
        assert r.PIN == booking_dict.get("PIN")
        assert r.StartValidity == booking_dict.get("StartValidity")
        assert r.EndValidity == booking_dict.get("EndValidity")
        assert r.DoorIDs == booking_dict.get("DoorIDs")

        response = act365_client.deleteBooking(r.BookingID)
        assert response.json().get("Success") is True

    def _create_test_cardholder(self, act365_client) -> int:
        now = datetime.now()
        cardholder = CardHolder(
            {
                "CustomerID": me.get("CustomerID"),
                "SiteID": me.get("SiteID"),
                "Forename": "Test",
                "Surname": "Cardholder",
                "Email": f"test+{now.strftime('%Y%m%d%H%M%S')}@example.com",
                "PIN": f"{randint(0, 9999):04d}",
                "Groups": me.get("Groups"),
                "Card1": 0,
                "Card2": 0,
                "Enabled": True,
                "StartValid": now.strftime(STRPTIME_FMT),
                "EndValid": (now + timedelta(hours=1)).strftime(STRPTIME_FMT),
            }
        )
        new_id = act365_client.createCardholder(cardholder)
        assert new_id is not None
        assert isinstance(new_id, int)
        assert new_id > 0
        return new_id

    def test_create_cardholder(self, act365_client):
        self._create_test_cardholder(act365_client)

    def test_update_cardholder(self, act365_client):
        new_id = self._create_test_cardholder(act365_client)
        now = datetime.now()
        cardholder = CardHolder(
            {
                "CardHolderID": new_id,
                "CustomerID": me.get("CustomerID"),
                "SiteID": me.get("SiteID"),
                "Forename": "Test",
                "Surname": "Cardholder",
                "Groups": me.get("Groups"),
                "StartValid": (now + timedelta(hours=2)).strftime(STRPTIME_FMT),
                "EndValid": (now + timedelta(hours=3)).strftime(STRPTIME_FMT),
            }
        )
        result = act365_client.updateCardholder(cardholder)
        assert result is True

    def test_client_simon(self, act365_client):
        params = {
            "siteid": 8539,
            "maxlimit": 2,
            "searchstring": "Simon McCartney",
        }
        cardholders = act365_client.getCardholders(params=params)
        assert cardholders[0].CardHolderID == 21274334
        assert cardholders[0].Forename == "Simon"

    def test_client_morethan2(self, act365_client):
        cardholders = act365_client.getCardholders()
        print(f"CardHolders returned: {len(cardholders)}")
        assert len(cardholders) > 2

    def test_get_by_email(self, act365_client):
        import time

        start = time.monotonic()
        cardholder = act365_client.getCardholderByEmail("simon@mccartney.ie")
        elapsed = time.monotonic() - start

        total = len(act365_client._CardHolders)
        print(f"\nLoaded {total} cardholders in {elapsed:.2f}s to find by email")

        assert cardholder.Forename == "Simon"
        assert cardholder.Surname == "McCartney"

    # def test_get_by_email_1410(act365_client):
    #     cardholder1410 = act365_client.getCardholderByEmail("araclay@hotmail.com")
    #     assert cardholder1410.Forename == "Aidan"
    #     assert cardholder1410.Surname == "McMurray "
    #     assert cardholder1410.Card1 == 1410

    # def test_get_by_id(act365_client):
    #     cardholder1410 = act365_client.getCardholderById(32047402)
    #     assert cardholder1410.Forename == "Aidan"
    #     assert cardholder1410.Surname == "McMurray "
    #     assert cardholder1410.Card1 == 1410
