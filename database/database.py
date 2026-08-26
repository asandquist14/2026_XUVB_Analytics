from pathlib import Path
import sqlite3

DATABASE = Path(__file__).parent.parent / "data" / "volleyball.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

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
        
        rotation TEXT


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

    conn.commit()
    conn.close()


if __name__ == "__main__":

    initialize_database()

    print("Database Initialized!")

def add_attack(practice_date, drill, setter, attacker, attack_side, result, rotation):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attacks
        (practice_date, drill, setter, attacker, attack_side, result, rotation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(practice_date),
        drill,
        setter,
        attacker,
        attack_side,
        result,
        rotation

    ))

    conn.commit()
    conn.close()

def delete_last_attack():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM attacks
        WHERE id = (
            SELECT MAX(id)
            FROM attacks
        )
    """)

    conn.commit()
    conn.close()

def delete_last_serve():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serves
        WHERE id = (
            SELECT MAX(id)
            FROM serves
        )
    """)

    conn.commit()
    conn.close()

def delete_last_recieve():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM serve_receive
        WHERE id = (
            SELECT MAX(id)
            FROM serve_receive
        )
    """)

    conn.commit()
    conn.close()

def clear_attack_practice(practice_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM attacks
        WHERE practice_date = ?
        """,
        (str(practice_date),)
    )

    conn.commit()
    conn.close()

def clear_serve_practice(practice_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM serves
        WHERE practice_date = ?
        """,
        (str(practice_date),)
    )

    conn.commit()
    conn.close()

def clear_serve_recieve_practice(practice_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM serve_receive
        WHERE practice_date = ?
        """,
        (str(practice_date),)
    )

    conn.commit()
    conn.close()


def add_serve(practice_date, drill, server, result, rotation):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO serves
        (practice_date, drill, server, result, rotation)
        VALUES (?, ?, ?, ?, ?)
    """,(
        str(practice_date),
        drill,
        server,
        result,
        rotation,
    ))

    conn.commit()
    conn.close()

def add_serve_receive(practice_date, drill, passer, rating, rotation):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO serve_receive
        (practice_date, drill, passer, rating, rotation)
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(practice_date),
        drill,
        passer,
        rating,
        rotation
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
    serving_team
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM matches")

    cursor.execute("""
        INSERT INTO matches
        (
            opponent,
            match_date,
            location,
            set_number,
            xavier_score,
            opponent_score,
            serving_team
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,(
        opponent,
        str(match_date),
        location,
        set_number,
        xavier_score,
        opponent_score,
        serving_team
    ))

    conn.commit()
    conn.close()

def load_match_state():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches LIMIT 1")

    row = cursor.fetchone()

    conn.close()

    return row