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

if "selected_target_zone" not in st.session_state:
    st.session_state.selected_target_zone = None

def get_setter(court):

    if st.session_state.mode == "Match":
        return st.session_state.left_setter

    if court == "Left":
        return st.session_state.left_setter

    return st.session_state.right_setter




def target_zone_selector():
    st.markdown("**Where did the attack land?**")

    if "selected_target_zone" not in st.session_state:
        st.session_state.selected_target_zone = None

    # Front row: zones 4, 3, 2
    front = st.columns(3, gap="small")
    for col, zone in zip(front, [4, 3, 2]):
        with col:
            if st.button(
                f"Zone {zone}",
                key=f"target_zone_{zone}",
                use_container_width=True
            ):
                st.session_state.selected_target_zone = zone

    # Back row: zones 5, 6, 1
    back = st.columns(3, gap="small")
    for col, zone in zip(back, [5, 6, 1]):
        with col:
            if st.button(
                f"Zone {zone}",
                key=f"target_zone_{zone}",
                use_container_width=True
            ):
                st.session_state.selected_target_zone = zone

    zone = st.session_state.selected_target_zone

    if zone is not None:
        st.info(f"Selected target zone: {zone}")
    else:
        st.caption("Select a zone before recording the attack.")

def attack_buttons(player, side, court,  practice_date, drill):
    target_zone = st.session_state.selected_target_zone

    c1, c2, c3 = st.columns([1,1,1], gap="small")

    if c1.button("🟢 Kill", key=f"{court}_{player['Player']}_{side}_K"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "K",
            st.session_state.rotation,
            st.session_state.active_season_id,
            session_type=st.session_state.mode,
            target_zone=target_zone
        )
        st.session_state.selected_target_zone = None
        st.rerun()

    if c2.button("🔴 Error", key=f"{court}_{player['Player']}_{side}_E"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "E",
            st.session_state.rotation,
            st.session_state.active_season_id,
            session_type=st.session_state.mode,
            target_zone=target_zone
        )
        st.session_state.selected_target_zone = None
        st.rerun()

    if c3.button("🟡 Attempt", key=f"{court}_{player['Player']}_{side}_A"):
        add_attack(
            practice_date,
            drill,
            get_setter(court),
            player["Player"],
            side,
            "A",
            st.session_state.rotation,
            st.session_state.active_season_id,
            session_type=st.session_state.mode,
            target_zone=target_zone
        )
        st.session_state.selected_target_zone = None
        st.rerun()

def practice_attack_page():

    practice_date = st.session_state.practice_date
    drill = st.session_state.drill
    st.session_state.rotation
    

    st.header("🏐 Attack Entry")

    target_zone_selector()

    st.divider()

    roster = attackers(st.session_state.active_season_id)

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
        delete_last_attack(st.session_state.active_season_id, session_type="Practice")
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_attack_practice(practice_date, st.session_state.active_season_id, session_type="Practice")
        st.rerun()

    st.header("Live Practice Stats")

    roster = attackers(st.session_state.active_season_id)
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

    
    session_type = "Practice"
    season_id = st.session_state.active_season_id

    if view == "Overall":
        stats = get_attack_stats(practice_date, season_id, session_type)

    elif view == "By Rotation":
        stats = get_attack_stats_by_rotation(practice_date, season_id, session_type)

    elif view == "By Player & Rotation":
        stats = get_attack_stats_player_rotation(practice_date, season_id, session_type)

    elif view == "By Attack Side":
        stats = get_attack_stats_by_side(practice_date, season_id, session_type)

    elif view == "By Setter":
        stats = get_attack_stats_by_setter(practice_date, season_id, session_type)

    else:
        stats = get_attack_stats_by_setter_side(practice_date, season_id, session_type)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
        )

def match_attack_page():

    practice_date = st.session_state.practice_date
    drill = st.session_state.drill

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
        ["No Rotation", "R1","R2","R3","R4","R5","R6"],
        horizontal=True,
        key="rotation"
    )

    st.divider()

    # ============================================
    # Attack Entry
    # ============================================

    st.header("🏐 Attack Entry")

    target_zone_selector()

    st.divider()

    roster = attackers(st.session_state.active_season_id)

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

    session_type = "Match"
    season_id = st.session_state.active_season_id

    if view == "Overall":
        stats = get_attack_stats(practice_date, season_id, session_type)

    elif view == "By Rotation":
        stats = get_attack_stats_by_rotation(practice_date, season_id, session_type)

    elif view == "By Player & Rotation":
        stats = get_attack_stats_player_rotation(practice_date, season_id, session_type)

    elif view == "By Attack Side":
        stats = get_attack_stats_by_side(practice_date, season_id, session_type)

    elif view == "By Setter":
        stats = get_attack_stats_by_setter(practice_date, season_id, session_type)

    else:
        stats = get_attack_stats_by_setter_side(practice_date, season_id, session_type)

    if st.button("↩️ Undo Last Entry"):
        delete_last_attack(st.session_state.active_season_id, session_type="Match")
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_attack_practice(practice_date, st.session_state.active_season_id, session_type="Match")
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