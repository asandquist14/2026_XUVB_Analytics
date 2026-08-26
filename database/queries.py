import pandas as pd
import numpy as np
from database.database import get_connection
from utils.roster import load_roster


def get_attack_stats(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        attacker,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks
    WHERE practice_date = ?
    GROUP BY attacker

    """, conn, params=(str(practice_date),))

    conn.close()

    if df.empty:
        return df


    df["TotalAttempts"] = (
        df["Kills"]
        + df["Errors"]
        + df["Attempt"]
    )

    df["Attacking %"] = np.where(
    df["TotalAttempts"] > 0,
    ((df["Kills"] - df["Errors"]) / df["TotalAttempts"]).round(3),
    0.000
)
    # Kill Percentage
    df["Kill %"] = np.where(
    df["TotalAttempts"] > 0,
    (df["Kills"] / df["TotalAttempts"]).round(3),
    0.000
)

    return df

def get_attack_stats_by_side(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        attacker,
        attack_side,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks

    WHERE practice_date = ?

    GROUP BY attacker, attack_side

    """, conn, params=(str(practice_date),))

    conn.close()

    if df.empty:
        return df

    df["TotalAttempts"] = (
        df["Kills"]
        + df["Errors"]
        + df["Attempt"]
    )

    df["Attack %"] = np.where(
        df["TotalAttempts"] > 0,
        ((df["Kills"] - df["Errors"]) / df["TotalAttempts"]).round(3),
        0.000
    )

    df["Kill %"] = np.where(
        df["TotalAttempts"] > 0,
        (df["Kills"] / df["TotalAttempts"]).round(3),
        0.000
    )

    return df

def get_attack_stats_by_setter(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        attacker,
        setter,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks

    WHERE practice_date = ?

    GROUP BY attacker, setter

    """, conn, params=(str(practice_date),))

    conn.close()

    if df.empty:
        return df

    df["TotalAttempts"] = (
        df["Kills"]
        + df["Errors"]
        + df["Attempt"]
    )

    df["Attack %"] = np.where(
        df["TotalAttempts"] > 0,
        ((df["Kills"] - df["Errors"]) / df["TotalAttempts"]).round(3),
        0.000
    )

    df["Kill %"] = np.where(
        df["TotalAttempts"] > 0,
        (df["Kills"] / df["TotalAttempts"]).round(3),
        0.000
    )

    return df

def get_attack_stats_by_setter_side(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        attacker,
        setter,
        attack_side,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks

    WHERE practice_date = ?

    GROUP BY attacker, setter, attack_side

    """, conn, params=(str(practice_date),))

    conn.close()

    if df.empty:
        return df

    df["TotalAttempts"] = (
        df["Kills"]
        + df["Errors"]
        + df["Attempt"]
    )

    df["Attack %"] = np.where(
        df["TotalAttempts"] > 0,
        ((df["Kills"] - df["Errors"]) / df["TotalAttempts"]).round(3),
        0.000
    )

    df["Kill %"] = np.where(
        df["TotalAttempts"] > 0,
        (df["Kills"] / df["TotalAttempts"]).round(3),
        0.000
    )

    return df

def get_serving_stats(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        server,

        COUNT(*) AS Serves,

        SUM(CASE WHEN result=4 THEN 1 ELSE 0 END) AS Aces,

        SUM(CASE WHEN result=0 THEN 1 ELSE 0 END) AS Errors,

        ROUND(AVG(result),2) AS Average

    FROM serves

    WHERE practice_date = ?

    GROUP BY server

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_serve_receive_stats(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        passer,

        COUNT(*) AS Passes,

        SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) AS Perfect,

        SUM(CASE WHEN rating=2 THEN 1 ELSE 0 END) AS Good,

        SUM(CASE WHEN rating=1 THEN 1 ELSE 0 END) AS Poor,

        SUM(CASE WHEN rating=0 THEN 1 ELSE 0 END) AS Errors,

        ROUND(AVG(rating),2) AS Average

    FROM serve_receive

    WHERE practice_date = ?

    GROUP BY passer

    """, conn, params=(str(practice_date),))

    conn.close()

    if df.empty:
        return df

    df["Perfect %"] = (
        df["Perfect"] / df["Passes"]
        ).round(3)

    return df

def get_attack_stats_by_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        rotation,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks

    WHERE practice_date = ?

    GROUP BY rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_attack_stats_player_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        attacker,

        rotation,

        SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

        SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

        SUM(CASE WHEN result='A' THEN 1 ELSE 0 END) AS Attempt

    FROM attacks

    WHERE practice_date = ?

    GROUP BY attacker, rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_serving_stats_by_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        rotation,

        COUNT(*) AS Serves,

        SUM(CASE WHEN result=4 THEN 1 ELSE 0 END) AS Aces,

        SUM(CASE WHEN result=0 THEN 1 ELSE 0 END) AS Errors,

        ROUND(AVG(result),2) AS Average

    FROM serves

    WHERE practice_date = ?

    GROUP BY rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_serving_stats_player_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        server,

        rotation,

        COUNT(*) AS Serves,

        SUM(CASE WHEN result=4 THEN 1 ELSE 0 END) AS Aces,

        SUM(CASE WHEN result=0 THEN 1 ELSE 0 END) AS Errors,

        ROUND(AVG(result),2) AS Average

    FROM serves

    WHERE practice_date = ?

    GROUP BY server, rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_serve_receive_stats_by_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        rotation,

        COUNT(*) AS Passes,

        SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) AS Perfect,

        SUM(CASE WHEN rating=0 THEN 1 ELSE 0 END) AS Aced,

        ROUND(AVG(rating),2) AS Average

    FROM serve_receive

    WHERE practice_date = ?

    GROUP BY rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_serve_receive_player_rotation(practice_date):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT

        passer,

        rotation,

        COUNT(*) AS Passes,

        SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) AS Perfect,

        SUM(CASE WHEN rating=0 THEN 1 ELSE 0 END) AS Aced,

        ROUND(AVG(rating),2) AS Average

    FROM serve_receive

    WHERE practice_date = ?

    GROUP BY passer, rotation

    """, conn, params=(str(practice_date),))

    conn.close()

    return df

def get_player_attack_stats(practice_date, player):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT *

    FROM attacks

    WHERE practice_date = ?
    AND attacker = ?

    """, conn, params=(str(practice_date), player))

    conn.close()

    return df

def get_player_serving_stats(practice_date, player):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT *

    FROM serves

    WHERE practice_date = ?
    AND server = ?

    """, conn, params=(str(practice_date), player))

    conn.close()

    return df

def get_player_receive_stats(practice_date, player):

    conn = get_connection()

    df = pd.read_sql_query("""

    SELECT *

    FROM serve_receive

    WHERE practice_date = ?
    AND passer = ?

    """, conn, params=(str(practice_date), player))

    conn.close()

    return df

def get_master_report(practice_date):

    roster = load_roster()

    attack = get_attack_stats(practice_date)
    serving = get_serving_stats(practice_date)
    passing = get_serve_receive_stats(practice_date)

    master = roster.copy()

    master = master.merge(
        attack,
        how="left",
        left_on="Player",
        right_on="attacker"
    )

    master = master.merge(
        serving,
        how="left",
        left_on="Player",
        right_on="server"
    )

    master = master.merge(
        passing,
        how="left",
        left_on="Player",
        right_on="passer"
    )

    return master.fillna(0)

def get_attack_trend(player=None):

    conn = get_connection()

    query = """

        SELECT

            practice_date,

            SUM(CASE WHEN result='K' THEN 1 ELSE 0 END) AS Kills,

            SUM(CASE WHEN result='E' THEN 1 ELSE 0 END) AS Errors,

            COUNT(*) AS Attempts

        FROM attacks

    """

    params = []

    if player is not None:

        query += " WHERE attacker = ? "

        params.append(player)

    query += """

        GROUP BY practice_date

        ORDER BY practice_date

    """

    df = pd.read_sql_query(
        query,
        conn,
        params=params
    )

    conn.close()

    if df.empty:

        return df

    df["Attack %"] = (
        (df["Kills"] - df["Errors"])
        / df["Attempts"]
    ).round(3)

    df["Kill %"] = (
        df["Kills"]
        / df["Attempts"]
    ).round(3)

    return df

def get_serving_trend(player=None):

    conn = get_connection()

    query = """

        SELECT

            practice_date,

            ROUND(AVG(result),2) AS ServeAverage

        FROM serves

    """

    params = []

    if player is not None:

        query += " WHERE server = ? "

        params.append(player)

    query += """

        GROUP BY practice_date

        ORDER BY practice_date

    """

    df = pd.read_sql_query(
        query,
        conn,
        params=params
    )

    conn.close()

    return df

def get_passing_trend(player=None):

    conn = get_connection()

    query = """

        SELECT

            practice_date,

            ROUND(AVG(rating),2) AS PassAverage,

            COUNT(*) AS Passes,

            SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) AS Perfect

        FROM serve_receive

    """

    params = []

    if player is not None:

        query += " WHERE passer = ? "

        params.append(player)

    query += """

        GROUP BY practice_date

        ORDER BY practice_date

    """

    df = pd.read_sql_query(
        query,
        conn,
        params=params
    )

    conn.close()

    if df.empty:

        return df

    df["Perfect %"] = (
        df["Perfect"]
        / df["Passes"]
    ).round(3)

    return df