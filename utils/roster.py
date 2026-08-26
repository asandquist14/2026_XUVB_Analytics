import pandas as pd
from pathlib import Path

ROSTER = Path(__file__).parent.parent / "data" / "roster.csv"


def load_roster():
    roster = pd.read_csv(ROSTER)

    roster.columns = roster.columns.str.strip().str.title()

    if "Active" in roster.columns:
        roster = roster[roster["Active"] == "Yes"]

    return roster


def attackers():

    roster = load_roster()
    
    return roster[
        roster["Position"].isin(["OH", "MB"])
    ]


def setters():

    roster = load_roster()

    return roster[
        roster["Position"] == "S"
    ]


def servers():

    return load_roster()


def passers():

    roster = load_roster()

    return roster[
        roster["Position"].isin(
            ["OH", "L/DS", "DS", "MB"]
        )
    ]