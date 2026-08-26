import streamlit as st

from utils.roster import load_roster
from database.queries import get_serving_stats, get_serving_stats_by_rotation, get_serving_stats_player_rotation
from database.database import delete_last_serve, clear_serve_practice
from database.database import add_serve
from config import SERVE_RESULTS

def serve_buttons(player, practice_date, drill):

    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])

    if c1.button("🟢 4", key=f"{player}_4"):
        add_serve(practice_date, drill, player, 4, st.session_state.rotation)

    if c2.button("🟩 3", key=f"{player}_3"):
        add_serve(practice_date, drill, player, 3, st.session_state.rotation)

    if c3.button("🟨 2", key=f"{player}_2"):
        add_serve(practice_date, drill, player, 2, st.session_state.rotation)

    if c4.button("🟧 1", key=f"{player}_1"):
        add_serve(practice_date, drill, player, 1, st.session_state.rotation)

    if c5.button("🔴 0", key=f"{player}_0"):
        add_serve(practice_date, drill, player, 0, st.session_state.rotation)

def serving_page():

    practice_date = st.session_state.practice_date

    if st.session_state.mode == "Practice":
        drill = st.session_state.drill
    else:
        drill = f"{st.session_state.opponent} - Set {st.session_state.match_set}"
    
    st.session_state.rotation

    st.header("🏐 Serving")

    roster = load_roster()

    for _, player in roster.iterrows():

        with st.container(border=True):

            st.markdown(
                f"**#{player['Number']} {player['Player']}**"
            )

            serve_buttons(
                player["Player"],
                practice_date,
                drill
            )
    st.divider()

    view = st.selectbox(
        "Statistics View",
        [
            "Overall",
            "By Rotation",
            "By Player & Rotation"
        ]
    )

    if view == "Overall":
        stats = get_serving_stats(practice_date)

    elif view == "By Rotation":
        stats = get_serving_stats_by_rotation(practice_date)

    else:
        stats = get_serving_stats_player_rotation(practice_date)

    if st.button("↩️ Undo Last Entry"):
        delete_last_serve()
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_serve_practice(practice_date)
        st.rerun()

    st.header("Live Serving Stats")

    stats = get_serving_stats(practice_date)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
    )