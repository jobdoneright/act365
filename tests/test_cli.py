from click.testing import CliRunner

from act365.cardholder import CardHolder
from act365.cli import _cardholder_sort_key, cli


def make_cardholder(**overrides):
    base = {
        "CustomerID": 5622,
        "SiteID": 8539,
        "Groups": [27470],
    }
    base.update(overrides)
    return CardHolder(base)


def test_sort_key_cards_ascending_by_lowest_card():
    holders = [
        make_cardholder(CardHolderID=1, Cards=[200]),
        make_cardholder(CardHolderID=2, Cards=[]),
        make_cardholder(CardHolderID=3, Cards=[100, 50]),
    ]

    ordered = sorted(holders, key=_cardholder_sort_key("Cards"))

    # lowest card number first, cardholders without cards last
    assert [ch.CardHolderID for ch in ordered] == [3, 1, 2]


def test_sort_key_surname_case_insensitive_none_last():
    holders = [
        make_cardholder(CardHolderID=1, Surname="mccartney"),
        make_cardholder(CardHolderID=2, Surname=None),
        make_cardholder(CardHolderID=3, Surname="Abbott"),
    ]

    ordered = sorted(holders, key=_cardholder_sort_key("Surname"))

    assert [ch.CardHolderID for ch in ordered] == [3, 1, 2]


def test_sort_key_startvalid_chronological():
    holders = [
        make_cardholder(CardHolderID=1, StartValid="02/01/2025 00:00"),
        make_cardholder(CardHolderID=2, StartValid=""),
        # string-sorts after 02/01/2025 but is chronologically earlier
        make_cardholder(CardHolderID=3, StartValid="31/12/2024 23:59"),
    ]

    ordered = sorted(holders, key=_cardholder_sort_key("StartValid"))

    assert [ch.CardHolderID for ch in ordered] == [3, 1, 2]


def test_cardholders_list_sort_by_cards(monkeypatch):
    holders = [
        make_cardholder(CardHolderID=1, Surname="High", Cards=[3000]),
        make_cardholder(CardHolderID=2, Surname="None", Cards=[]),
        make_cardholder(CardHolderID=3, Surname="Low", Cards=[1003]),
    ]

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def getCardholders(self, params=None):
            return holders

    monkeypatch.setattr("act365.cli.Act365Client", FakeClient)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--username",
            "user",
            "--password",
            "pass",
            "--siteid",
            "8539",
            "cardholders",
            "list",
            "--sort-by",
            "Cards",
        ],
        obj={},
    )

    assert result.exit_code == 0, result.output
    lines = [
        line for line in result.output.splitlines() if line.startswith(("1", "2", "3"))
    ]
    assert [line.split()[0] for line in lines] == ["3", "1", "2"]


def test_cardholders_list_rejects_unknown_sort_field(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--username",
            "user",
            "--password",
            "pass",
            "--siteid",
            "8539",
            "cardholders",
            "list",
            "--sort-by",
            "NotAField",
        ],
        obj={},
    )

    assert result.exit_code != 0
    assert "Invalid value for '--sort-by'" in result.output
