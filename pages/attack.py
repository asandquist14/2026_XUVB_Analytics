import streamlit as st

from utils.roster import attackers
from database.database import add_attack, delete_last_attack, clear_attack_practice, save_match_state
from database.queries import (
    get_attack_stats,
    get_attack_stats_by_side,
    get_attack_stats_by_setter,
    get_attack_stats_by_setter_side,
    get_attack_stats_by_rotation,
    get_attack_stats_player_rotation
)
from config import ATTACK_RESULTS

mode = st.session_state.mode

def get_setter(court):

    if st.session_state.mode == "Match":
        return st.session_state.left_setter

    if court == "Left":
        return st.session_state.left_setter

    return st.session_state.right_setter

def attack_buttons(player, side, court,  practice_date, drill):

    c1, c2, c3 = st.columns([1,1,1], gap="small")

    if c1.button("🟢 Kill", key=f"{court}_{player['Player']}_{side}_K"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "K",
            st.session_state.rotation
        )

    if c2.button("🔴 Error", key=f"{court}_{player['Player']}_{side}_E"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "E",
            st.session_state.rotation
        )

    if c3.button("🟡 Attempt", key=f"{court}_{player['Player']}_{side}_A"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "A",
            st.session_state.rotation
        )

def practice_attack_page():

    practice_date = st.session_state.practice_date
    drill = st.session_state.drill
    st.session_state.rotation
    

    st.header("🏐 Attack Entry")

    roster = attackers()

    left_court, right_court = st.columns(2)

    with left_court:

        st.subheader("🏐 Left Court")

        for _, player in roster.iterrows():

            st.markdown(f"**#{player['Number']} {player['Player']}**")

            if player["Position"] == "OH":

                st.caption("Outside")

                attack_buttons(
                    player,
                    "Outside",
                    "Left",
                    practice_date,
                    drill
                )   

                st.caption("Right Side")

                attack_buttons(
                    player,
                    "Right Side",
                    "Left",
                    practice_date,
                    drill
            )

            elif player["Position"] == "MB":

                st.caption("Middle")

                attack_buttons(
                    player,
                    "Middle",
                    "Left",
                    practice_date,
                    drill
                )
            
            if (_ + 1) % 2 == 0:
                st.divider()

    with right_court:

        st.subheader("🏐 Right Court")

        for _, player in roster.iterrows():

            st.markdown(f"**#{player['Number']} {player['Player']}**")

            if player["Position"] == "OH":

                st.caption("Outside")

                attack_buttons(
                    player,
                    "Outside",
                    "Right",
                    practice_date,
                    drill
                )

                st.caption("Right Side")

                attack_buttons(
                    player,
                    "Right Side",
                    "Right",
                    practice_date,
                drill
                )

            elif player["Position"] == "MB":

                st.caption("Middle")

                attack_buttons(
                    player,
                    "Middle",
                    "Right",
                    practice_date,
                    drill
                )
            if (_ + 1) % 2 == 0:
                st.divider()

    if st.button("↩️ Undo Last Entry"):
        delete_last_attack()
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_attack_practice(practice_date)
        st.rerun()

    st.header("Live Practice Stats")

    roster = attackers()
    st.write("Number of attackers:", len(roster))

    view = st.selectbox(
    "Statistics View",
    [
        "Overall",
        "By Rotation",
        "By Player & Rotation",
        "By Attack Side",
        "By Setter",
        "By Setter & Attack Side"
    ]
)

    if view == "Overall":
        stats = get_attack_stats(practice_date)

    elif view == "By Rotation":
        stats = get_attack_stats_by_rotation(practice_date)

    elif view == "By Player & Rotation":
        stats = get_attack_stats_player_rotation(practice_date)

    elif view == "By Attack Side":
        stats = get_attack_stats_by_side(practice_date)

    elif view == "By Setter":
        stats = get_attack_stats_by_setter(practice_date)

    else:
        stats = get_attack_stats_by_setter_side(practice_date)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
        )

def match_attack_page():

    practice_date = st.session_state.practice_date
    drill = st.session_state.drill

    # ============================================
    # Match Information
    # ============================================

    st.header("🏆 Match Information")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Opponent",
            key="opponent"
        )

        st.selectbox(
            "Location",
            ["Home", "Away", "Neutral"],
            key="location"
        )

    with col2:

        st.date_input(
            "Match Date",
            key="match_date"
        )

        st.selectbox(
            "Set",
            [1,2,3,4,5],
            key="set_number"
        )

    st.divider()

    # ============================================
    # Live Score
    # ============================================

    st.header("📊 Live Score")

    score1, score2 = st.columns(2)

    with score1:

        st.number_input(
            "Xavier",
            min_value=0,
            key="xavier_score"
        )

    with score2:

        st.number_input(
            "Opponent",
            min_value=0,
            key="opponent_score"
        )

    st.radio(
        "Serving",
        ["Xavier", "Opponent"],
        horizontal=True,
        key="serving_team"
    )

    st.radio(
        "Rotation",
        ["R1","R2","R3","R4","R5","R6"],
        horizontal=True,
        key="rotation"
    )

    st.divider()

    # ============================================
    # Attack Entry
    # ============================================

    st.header("🏐 Attack Entry")

    roster = attackers()

    for _, player in roster.iterrows():

        st.markdown(f"**#{player['Number']} {player['Player']}**")

        if player["Position"] == "OH":

            st.caption("Outside")

            attack_buttons(
                player,
                "Outside",
                "Left",
                practice_date,
                drill
            )

            st.caption("Right Side")

            attack_buttons(
                player,
                "Right Side",
                "Left",
                practice_date,
                drill
            )

        elif player["Position"] == "MB":

            st.caption("Middle")

            attack_buttons(
                player,
                "Middle",
                "Left",
                practice_date,
                drill
            )

        st.divider()

    # ============================================
    # Live Match Stats
    # ============================================

    st.header("📈 Live Match Stats")

    view = st.selectbox(
    "Statistics View",
    [
        "Overall",
        "By Rotation",
        "By Player & Rotation",
        "By Attack Side",
        "By Setter",
        "By Setter & Attack Side"
    ]
)

    if view == "Overall":
        stats = get_attack_stats(practice_date)

    elif view == "By Rotation":
        stats = get_attack_stats_by_rotation(practice_date)

    elif view == "By Player & Rotation":
        stats = get_attack_stats_player_rotation(practice_date)

    elif view == "By Attack Side":
        stats = get_attack_stats_by_side(practice_date)

    elif view == "By Setter":
        stats = get_attack_stats_by_setter(practice_date)

    else:
        stats = get_attack_stats_by_setter_side(practice_date)

    if st.button("↩️ Undo Last Entry"):
        delete_last_attack()
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_attack_practice(practice_date)
        st.rerun()

    if st.button("💾 Save Match"):

        save_match_state(

            st.session_state.opponent,

            st.session_state.match_date,

            st.session_state.location,

            st.session_state.set_number,

            st.session_state.xavier_score,

            st.session_state.opponent_score,

            st.session_state.serving_team
        )

    st.success("Match saved!")

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
    )