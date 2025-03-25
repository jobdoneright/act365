import os
from datetime import datetime, timedelta
from random import randint

import pytest

from act365.booking import STRPTIME_FMT, Booking
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

        bookings = act365_client.getBookings(me.get("SiteID"))
        assert len(bookings) > 0
        assert bookings[0].BookingID > 0

        response = act365_client.deleteBooking(bookings[0].BookingID)
        assert response.json().get("Success") is True

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
        cardholder = act365_client.getCardholderByEmail("simon@mccartney.ie")

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
