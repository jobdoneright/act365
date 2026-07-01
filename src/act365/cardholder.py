import datetime

from act365.booking import STRPTIME_FMT

me = {
    "CardHolderID": 21274334,
    "CustomerID": 5622,
    "SiteID": 8539,
    "Forename": "Simon",
    "Surname": "McCartney",
    "Enabled": True,
    "StartValid": "03/11/2024 02: 00",
    "EndValid": "03/11/2024 03: 00",
    "Groups": [27470],
    "ToggleRelay": False,
    "ExtendRelay": False,
    "Op2": False,
    "Op3": False,
    "ArmDisarm": False,
    "Verify": False,
    "PIN": "",
    "Card1": 1003,
    "Card2": 0,
    "MobilePhone": "",
    "Email": "Simon@mccartney.ie",
    "UserFields": ["", "", "", "", "", "", "", "", "", ""],
    "Cards": [1003],
    "LastPhotoUpdate": 0,
    "HasPhoto": False,
    "ExternalID": 0,
}

empty = {
    "CardHolderID": None,
    "CustomerID": None,
    "SiteID": None,
    "Forename": None,
    "Surname": None,
    "Enabled": None,
    "StartValid": None,
    "EndValid": None,
    "Groups": [],
    "ToggleRelay": None,
    "ExtendRelay": None,
    "Op2": None,
    "Op3": None,
    "ArmDisarm": None,
    "Verify": None,
    "PIN": "",
    "Card1": None,
    "Card2": None,
    "MobilePhone": None,
    "Email": None,
    "UserFields": [],
    "Cards": [],
    "LastPhotoUpdate": 0,
    "HasPhoto": False,
    "ExternalID": 0,
}


class CardHolder(object):

    def __init__(self, dictionary) -> None:
        merged = dict(list(empty.items()) + list(dictionary.items()))
        for key in merged:
            setattr(self, key, merged[key])
        if not self.SiteID:
            raise ValueError("CardHolder SiteID is required")
        if not self.CustomerID:
            raise ValueError("CardHolder CustomerID is required")
        if not self.Groups:
            raise ValueError("CardHolder must belong to at least one Group")
        if len(self.Cards) > 4:
            raise ValueError("CardHolder can have at most 4 cards")

    def __repr__(self):
        return "<dict2obj: %s>" % self.__dict__

    @property
    def StartValid(self) -> str:
        if self._StartValid_dt is None:
            return ""
        else:
            return self._StartValid_dt.strftime(STRPTIME_FMT)

    @StartValid.setter
    def StartValid(self, value: str | None):
        if value is None or value == "":
            self._StartValid_dt = value
        else:
            self._StartValid_dt = datetime.datetime.strptime(value, STRPTIME_FMT)

    @property
    def EndValid(self) -> str:
        if self._EndValid_dt is None:
            return ""
        else:
            return self._EndValid_dt.strftime(STRPTIME_FMT)

    @EndValid.setter
    def EndValid(self, value: str | None):
        if value is None or value == "":
            self._EndValid_dt = value
        else:
            self._EndValid_dt = datetime.datetime.strptime(value, STRPTIME_FMT)

    def dict(self) -> dict:
        result = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        result["StartValid"] = self.StartValid
        result["EndValid"] = self.EndValid
        return result
