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
