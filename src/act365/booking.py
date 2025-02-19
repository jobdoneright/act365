from dataclasses import InitVar, asdict, dataclass, field
from datetime import datetime
from typing import List


@dataclass
class BookingDoor:
    ID: int
    Name: str
    CustomerID: int
    SiteID: int
    ControllerID: int
    LocalDoorNumber: int
    IsConnected: bool
    IsEnabled: bool
    Status: List[str] = field(default_factory=lambda: [])
    State: int = 0
    Cameras: List[str] = field(default_factory=lambda: [])


@dataclass
class BookingAddress:
    AddressLine1: str
    AddressLine2: str
    City: str
    Country: str
    Longitude: str
    Latitude: str
    LocationAccurate: bool


@dataclass
class BookingContact:
    Name: str
    Phone: str
    Email: str


@dataclass
class BookingSite:
    ID: int
    Name: str
    CustomerID: int
    Address: BookingAddress
    Contact: BookingContact


@dataclass
class Booking:
    SiteID: int
    Forename: str
    Surname: str
    PIN: str
    StartValidity: str | datetime
    EndValidity: str | datetime
    Card: int = 0
    ToggleMode: bool = False
    DoorIDs: List[int] = field(default_factory=list)
    BookingID: int = 0
    BookingCreatedTime: str | None = None
    # ACT365 will return objects with a single door as DoorID, not DoorIDs, when there is only 1 door
    # to prevent dataclass returning this, we use InitVar & store the passed DoorID in DoorIDs
    DoorID: InitVar[int | None] = None

    def __post_init__(self, DoorID):
        if len(self.DoorIDs) == 0 and DoorID is not None:
            self.DoorIDs.append(DoorID)

    @property
    def StartValidity(self):
        if isinstance(self._StartValidity, datetime):
            return self._StartValidity.strftime("%d/%m/%Y %H:%M")
        else:
            return self._StartValidity

    @StartValidity.setter
    def StartValidity(self, value):
        if isinstance(value, datetime):
            self._StartValidity = value
        else:
            self._StartValidity = datetime.strptime(value, "%d/%m/%Y %H:%M")

    @property
    def EndValidity(self):
        if isinstance(self._EndValidity, datetime):
            return self._EndValidity.strftime("%d/%m/%Y %H:%M")
        else:
            return self._EndValidity

    @EndValidity.setter
    def EndValidity(self, value):
        if isinstance(value, datetime):
            self._EndValidity = value
        else:
            self._EndValidity = datetime.strptime(value, "%d/%m/%Y %H:%M")

    # @property
    # def DoorID(self):
    #     return self.DoorIDs[0] if self.DoorIDs else None

    # @DoorID.setter
    # def DoorID(self, value):
    #     self.DoorIDs = [value]

    def dict(self):
        d = {k: str(v) for k, v in asdict(self).items()}
        # the ACT365 API expects a single door ID, not a list, when there is only 1 door
        if len(self.DoorIDs) == 1:
            d["DoorIDs"] = self.DoorIDs[0]

        # remove some of the fields that are not needed when creating a booking
        if self.BookingID == 0:
            del d["BookingID"]

        if self.BookingCreatedTime is None:
            del d["BookingCreatedTime"]

        return d
