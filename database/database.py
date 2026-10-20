from pathlib import Path
import sqlite3
import pandas as pd

DATABASE = Path(__file__).parent.parent / "data" / "volleyball.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    
    # Add missing columns to attacks
    cursor.execute("PRAGMA table_info(attacks)")
    columns = [row[1] for row in cursor.fetchall()]

    if "season_id" not in columns:
        cursor.execute("""
            ALTER TABLE attacks
            ADD COLUMN season_id INTEGER
        """)

    if "session_type" not in columns:
        cursor.execute("""
            ALTER TABLE attacks
            ADD COLUMN session_type TEXT DEFAULT 'Practice'
        """)

    # Add missing columns to serves
    cursor.execute("PRAGMA table_info(serves)")
    columns = [row[1] for row in cursor.fetchall()]

    if "season_id" not in columns:
        cursor.execute("""
            ALTER TABLE serves
            ADD COLUMN season_id INTEGER
        """)

    if "session_type" not in columns:
        cursor.execute("""
            ALTER TABLE serves
            ADD COLUMN session_type TEXT DEFAULT 'Practice'
        """)

    # Add missing columns to serve_receive
    cursor.execute("PRAGMA table_info(serve_receive)")
    columns = [row[1] for row in cursor.fetchall()]

    if "season_id" not in columns:
        cursor.execute("""
            ALTER TABLE serve_receive
            ADD COLUMN season_id INTEGER
        """)

    if "session_type" not in columns:
        cursor.execute("""
            ALTER TABLE serve_receive
            ADD COLUMN session_type TEXT DEFAULT 'Practice'
        """)

    # Add target_zone to existing attacks tables if needed
    cursor.execute("PRAGMA table_info(attacks)")
    attack_columns = [column[1] for column in cursor.fetchall()]

    if "target_zone" not in attack_columns:
        cursor.execute(
            "ALTER TABLE attacks ADD COLUMN target_zone INTEGER"
        )

    # ---------------- SEASONS ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_name TEXT NOT NULL UNIQUE,
            is_active INTEGER DEFAULT 0
        )
    """)

    # Create the initial season if it doesn't exist
    cursor.execute("""
        INSERT OR IGNORE INTO seasons (season_name, is_active)
        VALUES ('2026 Season', 1)
    """)

    # ---------------- ROSTER ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL,
            number INTEGER,
            player TEXT NOT NULL,
            position TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            UNIQUE (season_id, player)
        )
    """)

    # Import the existing CSV roster into the initial season
    roster_path = Path(__file__).parent.parent / "data" / "roster.csv"

    if roster_path.exists():
        roster_df = pd.read_csv(roster_path)
        roster_df.columns = roster_df.columns.str.strip().str.title()

        cursor.execute("""
            SELECT id FROM seasons
            WHERE season_name = '2026 Season'
        """)
        season_row = cursor.fetchone()

        if season_row:
            season_id = season_row[0]

            for _, row in roster_df.iterrows():
                active = 1

                if "Active" in roster_df.columns:
                    active = 1 if str(row["Active"]).strip().lower() == "yes" else 0

                cursor.execute("""
                    INSERT OR IGNORE INTO roster
                    (season_id, number, player, position, active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    season_id,
                    int(row["Number"]) if pd.notna(row.get("Number")) else None,
                    str(row["Player"]).strip(),
                    str(row["Position"]).strip(),
                    active
                ))

    # ---------------- ATTACK ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacks(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        practice_date TEXT,
        drill TEXT,

        setter TEXT,
        attacker TEXT,

        attack_side TEXT,

        result TEXT,
        
        rotation TEXT,

        session_type TEXT DEFAULT 'Practice'


)
    """)

    # ---------------- SERVES ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS serves(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            practice_date TEXT,
            drill TEXT,

            server TEXT,

            result INTEGER,
                    
            rotation TEXT


        )
    """)

    # ------------ SERVE RECEIVE ------------ #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS serve_receive(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            practice_date TEXT,
            drill TEXT,

            passer TEXT,

            rating INTEGER,
                
            rotation TEXT

        )
    """)

    # ------------ Match Information ------------ #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        opponent TEXT,
        match_date TEXT,

        location TEXT,

        set_number INTEGER,

        xavier_score INTEGER,
        opponent_score INTEGER,

        serving_team TEXT
    )
""")

    # ---------------- SEASON MIGRATION ---------------- #

    # Get the ID of the initial season
    cursor.execute("""
        SELECT id
        FROM seasons
        WHERE season_name = '2026 Season'
    """)

    season_id = cursor.fetchone()[0]

    # Add season_id to existing tables if needed
    tables = [
        "attacks",
        "serves",
        "serve_receive",
        "matches"
    ]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [column[1] for column in cursor.fetchall()]

        if "season_id" not in columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN season_id INTEGER"
            )

        # Assign existing records to the 2026 season
        cursor.execute(
            f"UPDATE {table} SET season_id = ? WHERE season_id IS NULL",
            (season_id,)
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    initialize_database()

    print("Database Initialized!")



def add_attack(practice_date, drill, setter, attacker, attack_side,
               result, rotation, season_id, session_type="Practice", target_zone=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attacks
        (practice_date, drill, setter, attacker, attack_side,
         result, rotation, season_id, session_type, target_zone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(practice_date),
        drill,
        setter,
        attacker,
        attack_side,
        result,
        rotation,
        season_id,
        session_type,
        target_zone
    ))

    conn.commit()
    conn.close()



def delete_last_attack(season_id, session_type=None):

    conn = get_connection()
    cursor = conn.cursor()

    if session_type is None:
        cursor.execute("""
            DELETE FROM attacks
            WHERE id = (
                SELECT MAX(id)
                FROM attacks
                WHERE season_id = ?
            )
        """, (season_id,))
    else:
        cursor.execute("""
            DELETE FROM attacks
            WHERE id = (
                SELECT MAX(id)
                FROM attacks
                WHERE season_id = ?
                AND session_type = ?
            )
        """, (season_id, session_type))

    conn.commit()
    conn.close()


def delete_last_serve(season_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serves
        WHERE id = (
            SELECT MAX(id)
            FROM serves
            WHERE season_id = ?
        )
    """, (season_id,))

    conn.commit()
    conn.close()


def delete_last_recieve(season_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serve_receive
        WHERE id = (
            SELECT MAX(id)
            FROM serve_receive
            WHERE season_id = ?
        )
    """, (season_id,))

    conn.commit()
    conn.close()



def clear_attack_practice(practice_date, season_id, session_type="Practice"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM attacks
        WHERE practice_date = ?
        AND season_id = ?
        AND session_type = ?
    """, (str(practice_date), season_id, session_type))

    conn.commit()
    conn.close()


def clear_serve_practice(practice_date, season_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serves
        WHERE practice_date = ?
        AND season_id = ?
    """, (str(practice_date), season_id))

    conn.commit()
    conn.close()


def clear_serve_recieve_practice(practice_date, season_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serve_receive
        WHERE practice_date = ?
        AND season_id = ?
    """, (str(practice_date), season_id))

    conn.commit()
    conn.close()


def add_serve(
    practice_date, drill, server, result, rotation,
    season_id, session_type="Practice"
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO serves
        (practice_date, drill, server, result, rotation,
         season_id, session_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(practice_date),
        drill,
        server,
        result,
        rotation,
        season_id,
        session_type
    ))

    conn.commit()
    conn.close()


def add_serve_receive(
    practice_date, drill, passer, rating, rotation,
    season_id, session_type="Practice"
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO serve_receive
        (practice_date, drill, passer, rating, rotation,
         season_id, session_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(practice_date),
        drill,
        passer,
        rating,
        rotation,
        season_id,
        session_type
    ))

    conn.commit()
    conn.close()


def save_match_state(
    opponent,
    match_date,
    location,
    set_number,
    xavier_score,
    opponent_score,
    serving_team,
    season_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM matches WHERE season_id = ?",
        (season_id,)
    )

    cursor.execute("""
        INSERT INTO matches
        (
            opponent,
            match_date,
            location,
            set_number,
            xavier_score,
            opponent_score,
            serving_team,
            season_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opponent,
        str(match_date),
        location,
        set_number,
        xavier_score,
        opponent_score,
        serving_team,
        season_id
    ))

    conn.commit()
    conn.close()


def load_match_state(season_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM matches WHERE season_id = ? LIMIT 1",
        (season_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_seasons():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, season_name
        FROM seasons
        ORDER BY season_name DESC
    """)

    seasons = cursor.fetchall()

    conn.close()

    return seasons


def add_season(season_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO seasons (season_name, is_active)
        VALUES (?, 0)
    """, (season_name,))

    conn.commit()
    conn.close()


def delete_season(season_name):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        # Find the season
        cursor.execute(
            "SELECT id FROM seasons WHERE season_name = ?",
            (season_name,)
        )
        season = cursor.fetchone()

        if season is None:
            conn.rollback()
            return False

        season_id = season[0]

        # Delete all statistics belonging to this season
        cursor.execute(
            "DELETE FROM attacks WHERE season_id = ?",
            (season_id,)
        )

        cursor.execute(
            "DELETE FROM serves WHERE season_id = ?",
            (season_id,)
        )

        cursor.execute(
            "DELETE FROM serve_receive WHERE season_id = ?",
            (season_id,)
        )

        # Delete the season's roster
        cursor.execute(
            "DELETE FROM roster WHERE season_id = ?",
            (season_id,)
        )

        # Delete the season record last
        cursor.execute(
            "DELETE FROM seasons WHERE id = ?",
            (season_id,)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def add_roster_player(season_id, number, player, position):
    """Add a player to a specific season's roster."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO roster (season_id, number, player, position, active)
        VALUES (?, ?, ?, ?, 1)
    """, (season_id, number, player.strip(), position))

    conn.commit()
    conn.close()


def update_roster_player(player_id, number, player, position):
    """Update a player's roster information."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE roster
        SET number = ?, player = ?, position = ?
        WHERE id = ?
    """, (number, player.strip(), position, player_id))

    conn.commit()
    conn.close()


def deactivate_roster_player(player_id):
    """Remove a player from the active roster without deleting their history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE roster
        SET active = 0
        WHERE id = ?
    """, (player_id,))

    conn.commit()
    conn.close()