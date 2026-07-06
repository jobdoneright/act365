import pytest

from act365.cardholder import CardHolder

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


def test_cardholder():
    cardholder = CardHolder(
        {
            "CustomerID": 5622,
            "SiteID": 8539,
            "Groups": [27470],
            "Forename": "Simon",
            "Surname": "McCartney",
            "Email": "simon@mccartney.ie",
        }
    )
    assert cardholder.Forename == "Simon"
    assert cardholder.Surname == "McCartney"
    assert cardholder.Email == "simon@mccartney.ie"

    # setter & getter should always return an API friendly format
    assert cardholder.StartValid == ""
    assert cardholder.EndValid == ""

    cardholder.StartValid = rt["StartValid"]
    cardholder.EndValid = rt["EndValid"]
    assert cardholder.StartValid == rt["StartValid"]
    assert cardholder.EndValid == rt["EndValid"]


def test_cardholder_dict():
    cardholder = CardHolder(
        {
            "CardHolderID": 21274334,
            "CustomerID": 5622,
            "SiteID": 8539,
            "Groups": [27470],
            "Forename": "Simon",
            "Surname": "McCartney",
            "Email": "simon@mccartney.ie",
            "PIN": "1234",
        }
    )
    cardholder.StartValid = rt["StartValid"]
    cardholder.EndValid = rt["EndValid"]

    d = cardholder.dict()

    assert d["Forename"] == "Simon"
    assert d["Surname"] == "McCartney"
    assert d["Email"] == "simon@mccartney.ie"
    assert d["PIN"] == "1234"
    assert d["Groups"] == [27470]
    assert d["StartValid"] == rt["StartValid"]
    assert d["EndValid"] == rt["EndValid"]
    assert d["CardHolderID"] == 21274334
    # private datetime attributes should not be in the dict
    assert "_StartValid_dt" not in d
    assert "_EndValid_dt" not in d


def test_cardholder_empty_validity_dates():
    # the API returns "" for cardholders with no validity dates; the
    # getters must not blow up on them (regression: str has no strftime)
    cardholder = CardHolder(
        {
            "CustomerID": 5622,
            "SiteID": 8539,
            "Groups": [27470],
            "StartValid": "",
            "EndValid": "",
        }
    )
    assert cardholder.StartValid == ""
    assert cardholder.EndValid == ""

    d = cardholder.dict()
    assert d["StartValid"] == ""
    assert d["EndValid"] == ""


def test_cardholder_requires_siteid():
    with pytest.raises(ValueError, match="SiteID"):
        CardHolder({"CustomerID": 5622, "Groups": [27470]})


def test_cardholder_requires_customerid():
    with pytest.raises(ValueError, match="CustomerID"):
        CardHolder({"SiteID": 8539, "Groups": [27470]})


def test_cardholder_requires_group():
    with pytest.raises(ValueError, match="Group"):
        CardHolder({"SiteID": 8539, "CustomerID": 5622})


def test_cardholder_max_4_cards():
    with pytest.raises(ValueError, match="4 cards"):
        CardHolder(
            {
                "SiteID": 8539,
                "CustomerID": 5622,
                "Groups": [27470],
                "Cards": [1, 2, 3, 4, 5],
            }
        )
