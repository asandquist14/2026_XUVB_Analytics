import streamlit as st
from utils.session import initialize_session
initialize_session()
from pages.attack import practice_attack_page, match_attack_page
from utils.roster import setters
from pages.serving import serving_page
from pages.recieve import serve_receive_page
from pages.reports import reports_page

st.set_page_config(
    page_title="Xavier Volleyball Analytics",
    page_icon="🏐",
    layout="wide"
)

st.header("Session")

st.session_state.mode = st.radio(
    "Select Session Type",
    ["Practice", "Match"],
    horizontal=True
)

# ---------- Sidebar ----------

st.sidebar.title("🏐 Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "🏠 Home",
        "🏐 Attack",
        "🎯 Serving",
        "📥 Serve Receive",
        "📊 Reports",
        "⚙ Settings"
    ]
)

# ---------- Header ----------

st.title("🏐 Xavier Women's Volleyball Analytics")

st.divider()

# ---------- Practice Information ----------

st.subheader("Session Setup")

st.session_state.practice_date = st.date_input(
    "Date"
)

if st.session_state.mode == "Practice":

    st.session_state.drill = st.text_input(
        "Current Drill"
    )

else:

    st.session_state.opponent = st.text_input(
        "Opponent"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.location = st.selectbox(
            "Location",
            ["Home", "Away", "Neutral"]
        )

        st.session_state.match_set = st.selectbox(
            "Current Set",
            [1, 2, 3, 4, 5]
        )

    with col2:

        st.session_state.xavier_score = st.number_input(
            "Xavier Score",
            min_value=0,
            value=0
        )

        st.session_state.opponent_score = st.number_input(
            "Opponent Score",
            min_value=0,
            value=0
        )

    st.session_state.serving_team = st.radio(
        "Serving Team",
        ["Xavier", "Opponent"],
        horizontal=True
    )


# ---------- Rotation ----------

st.session_state.rotation = st.radio(
    "Rotation",
    [
        "No Rotation",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6"
    ],
    horizontal=True,
)


# ---------- Setter ----------

setter_options = setters()["Player"].tolist()
setter_options.append("OOS")

if st.session_state.mode == "Practice":

    left_col, right_col = st.columns(2)

    with left_col:

        st.selectbox(
            "Left Court Setter",
            setter_options,
            key="left_setter"
        )

    with right_col:

        st.selectbox(
            "Right Court Setter",
            setter_options,
            key="right_setter"
        )

else:

    st.selectbox(
        "Current Setter",
        setter_options,
        key="left_setter"
    )


st.divider()

# ---------- Pages ----------

if page == "🏠 Home":

    st.header("Welcome")

    st.write("Select a page from the left.")

elif page == "🏐 Attack":

    if st.session_state.mode == "Practice":

        practice_attack_page()

    else:

        match_attack_page()

elif page == "🎯 Serving":

    serving_page()

elif page == "📥 Serve Receive":

    serve_receive_page()

elif page == "📊 Reports":

    reports_page()

elif page == "⚙ Settings":

    st.header("Settings")