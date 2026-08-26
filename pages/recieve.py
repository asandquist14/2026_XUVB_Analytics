import streamlit as st

from utils.roster import passers
from database.database import delete_last_recieve, clear_serve_recieve_practice

from database.database import add_serve_receive
from database.queries import get_serve_receive_stats, get_serve_receive_player_rotation, get_serve_receive_stats_by_rotation

def pass_buttons(player, practice_date, drill):

    c1, c2, c3, c4 = st.columns([1,1,1,1])

    if c1.button("🟢 3", key=f"{player}_3"):
        add_serve_receive(
            practice_date,
            drill,
            player,
            3,
            st.session_state.rotation
        )

    if c2.button("🟡 2", key=f"{player}_2"):
        add_serve_receive(
            practice_date,
            drill,
            player,
            2,
            st.session_state.rotation
        )

    if c3.button("🟠 1", key=f"{player}_1"):
        add_serve_receive(
            practice_date,
            drill,
            player,
            1,
            st.session_state.rotation
        )

    if c4.button("🔴 0", key=f"{player}_0"):
        add_serve_receive(
            practice_date,
            drill,
            player,
            0,
            st.session_state.rotation
        )

def serve_receive_page():

    practice_date = st.session_state.practice_date
    drill = st.session_state.drill
    st.session_state.rotation


    st.header("🏐 Serve Receive")

    roster = passers()

    for _, player in roster.iterrows():

        with st.container(border=True):

            st.markdown(
                f"**#{player['Number']} {player['Player']}**"
            )

            pass_buttons(
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
        stats = get_serve_receive_stats(practice_date)

    elif view == "By Rotation":
        stats = get_serve_receive_stats_by_rotation(practice_date)

    else:
        stats = get_serve_receive_player_rotation(practice_date)

    if st.button("↩️ Undo Last Entry"):
        delete_last_recieve()
        st.rerun()

    if st.button("🗑️ Clear Current Practice"):
        clear_serve_recieve_practice(practice_date)
        st.rerun()


    st.header("Live Passing Stats")

    stats = get_serve_receive_stats(practice_date)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
    )