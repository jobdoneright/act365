from datetime import datetime

from act365.booking import STRPTIME_FMT, Booking, BookingDoor

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

sample_out = {
    "SiteID": "8539",
    "Forename": "Simon",
    "Surname": "McCartney",
    "PIN": "0034",
    "Card": "0",
    "StartValidity": "15/03/2016 16:45",
    "EndValidity": "15/03/2016 18:00",
    "ToggleMode": "False",
    "DoorIDs": 14247,
}


def test_booking_door_object():
    door = BookingDoor(
        **{
            "ID": 1046,
            "Name": "Front door",
            "CustomerID": 12,
            "SiteID": 23,
            "ControllerID": 17,
            "LocalDoorNumber": 1,
            "IsConnected": True,
            "IsEnabled": True,
            "Status": ["Locked", "Tamper"],
            "State": 122,
            "Cameras": [],
        }
    )
    assert door.ID == 1046
    assert door.Name == "Front door"

    door2 = BookingDoor(
        **{
            "ID": 1046,
            "Name": "Front door",
            "CustomerID": 12,
            "SiteID": 23,
            "ControllerID": 17,
            "LocalDoorNumber": 1,
            "IsConnected": True,
            "IsEnabled": True,
        }
    )
    assert door2.ID == 1046
    assert door2.Name == "Front door"
    assert door2.Status == []
    assert door2.State == 0
    assert door2.Cameras == []


def test_booking_doors_from_json():
    doors = [
        {
            "ID": 1046,
            "Name": "Front door",
            "CustomerID": 12,
            "SiteID": 23,
            "ControllerID": 17,
            "LocalDoorNumber": 1,
            "IsConnected": True,
            "IsEnabled": True,
            "Status": ["Locked", "Tamper"],
            "State": 122,
            "Cameras": [],
        },
        {
            "ID": 1047,
            "Name": "Back door",
            "CustomerID": 12,
            "SiteID": 23,
            "ControllerID": 17,
            "LocalDoorNumber": 2,
            "IsConnected": True,
            "IsEnabled": True,
            "Status": ["Locked", "Tamper"],
            "State": 122,
            "Cameras": [],
        },
    ]
    doors = [BookingDoor(**door) for door in doors]
    assert doors[0].ID == 1046
    assert doors[1].ID == 1047


def test_booking_object_to_json():
    """
    Test that the Booking object can be converted to a JSON friendly format, the ACT365 API expects
    the DoorIDs field to be a single int when there is only one door.
    """
    booking = Booking(**sample)
    assert booking.dict() == sample_out
    assert type(booking) is Booking


def test_booking_object():
    booking = Booking(**sample)
    assert booking.Forename == "Simon"
    assert booking.Surname == "McCartney"
    assert booking.PIN == "0034"

    # setter & getter should always return an API friendly format
    assert booking.StartValidity == sample["StartValidity"]
    assert booking.EndValidity == sample["EndValidity"]

    booking.StartValidity = rt["StartValid"]
    booking.EndValidity = rt["EndValid"]
    assert booking.StartValidity == rt["StartValid"]
    assert booking.EndValidity == rt["EndValid"]

    booking.DoorIDs = [14247, 14248]
    assert booking.DoorIDs == [14247, 14248]

    # validate that DoorIDs is an int when there is only one door
    booking.DoorIDs = [14247]
    assert booking.dict().get("DoorIDs") == 14247
    assert type(booking.dict().get("DoorIDs")) == int
    assert type(booking.dict()["DoorIDs"]) == int


def test_booking_object_datetime():
    d = sample.copy()
    d["StartValidity"] = datetime.strptime(d["StartValidity"], STRPTIME_FMT)
    d["EndValidity"] = datetime.strptime(d["EndValidity"], STRPTIME_FMT)
    booking = Booking(**d)
    assert booking.Forename == "Simon"
    assert booking.Surname == "McCartney"
    assert booking.PIN == "0034"

    # setter & getter should always return an API friendly format
    assert booking.StartValidity == sample["StartValidity"]
    assert booking.EndValidity == sample["EndValidity"]

    booking.StartValidity = rt["StartValid"]
    booking.EndValidity = rt["EndValid"]
    assert booking.StartValidity == rt["StartValid"]
    assert booking.EndValidity == rt["EndValid"]

    booking.DoorIDs = [14247, 14248]
    assert booking.DoorIDs == [14247, 14248]

    # validate that DoorIDs is an int when there is only one door
    booking.DoorIDs = [14247]
    assert booking.dict().get("DoorIDs") == 14247
    assert type(booking.dict().get("DoorIDs")) == int
    assert type(booking.dict()["DoorIDs"]) == int


def test_booking_object_baddate():
    bad_dates = {
        "SiteID": 8539,
        "Forename": "Simon",
        "Surname": "McCartney",
        "PIN": "0034",
        "Card": 0,
        "StartValidity": "99/03/2016 16:45",
        "EndValidity": "2016/01/01 18:00",
        "ToggleMode": False,
        "DoorIDs": [14247],
    }
    # the StartValidity date is invalid, and should throw a ValueError
    try:
        _ = Booking(**bad_dates)
    except Exception as e:
        assert type(e) is ValueError


def test_booking_object_with_doorid():

    s2 = {
        "SiteID": 8539,
        "Forename": "Simon",
        "Surname": "McCartney",
        "PIN": "0034",
        "StartValidity": "15/03/2016 16:45",
        "EndValidity": "15/03/2016 18:00",
        "ToggleMode": False,
        "DoorID": 14247,
    }

    booking = Booking(**s2)
    # DoorID was set, so DoorIDs should be an int
    assert booking.dict()["DoorIDs"] == 14247


def test_booking_empty_object():
    try:
        _ = Booking()
    except Exception as e:
        assert type(e) is TypeError

    try:
        _ = Booking(BookingID=1)
    except Exception as e:
        assert type(e) is TypeError
