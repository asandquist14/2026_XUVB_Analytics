
import pandas as pd
from database.database import get_connection


def load_roster(season_id=None):
    """Load active players for the selected season."""
    conn = get_connection()

    if season_id is None:
        try:
            from streamlit import session_state
            season_id = session_state.get("active_season_id")
        except Exception:
            season_id = None

    if season_id is None:
        conn.close()
        return pd.DataFrame(
            columns=["Number", "Player", "Position", "Active"]
        )

    roster = pd.read_sql_query(
        """
        SELECT id,
               number AS Number,
               player AS Player,
               position AS Position,
               active AS Active
        FROM roster
        WHERE season_id = ?
          AND active = 1
        ORDER BY number, player
        """,
        conn,
        params=(season_id,)
    )

    conn.close()
    return roster


def attackers(season_id=None):
    roster = load_roster(season_id)
    return roster[roster["Position"].isin(["OH", "MB"])]


def setters(season_id=None):
    roster = load_roster(season_id)
    return roster[roster["Position"] == "S"]


def servers(season_id=None):
    return load_roster(season_id)


def passers(season_id=None):
    roster = load_roster(season_id)
    return roster[
        roster["Position"].isin(["OH", "L/DS", "DS", "MB"])
    ]