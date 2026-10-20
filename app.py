import streamlit as st
import pandas as pd
from utils.session import initialize_session
initialize_session()
from pages.attack import practice_attack_page, match_attack_page
from utils.roster import setters, load_roster
from pages.serving import serving_page
from pages.recieve import serve_receive_page
from pages.reports import reports_page
from database.database import get_seasons, add_roster_player, update_roster_player, deactivate_roster_player, add_season, delete_season, get_connection

st.set_page_config(
    page_title="Xavier Volleyball Analytics",
    page_icon="🏐",
    layout="wide"
)

# ---------------- SEASON SELECTOR ---------------- #

seasons = get_seasons()

if seasons:
    season_options = {
        season_name: season_id
        for season_id, season_name in seasons
    }

    selected_season = st.sidebar.selectbox(
        "Season",
        options=list(season_options.keys()),
        key="selected_season"
    )

    st.session_state.active_season_id = season_options[selected_season]
    st.session_state.active_season_name = selected_season

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
        "👥 Roster",
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

    drill_options = [
        "6v6",
        "Whistle 6v6",
        "5v5",
        "3 Ball Wash",
        "Tip Transition",
        "OOS v 6",
        "3 Ball Transition v 6",
        "Hitting Lines",
        "2 Min Hitting",
        "Pass to Attack",
        "Baseball",
        "Other / New Drill"
    ]

    selected_drill = st.selectbox(
        "Current Drill",
        drill_options,
        key="practice_drill_selection"
    )

    if selected_drill == "Other / New Drill":
        st.session_state.drill = st.text_input(
            "Enter New Drill Name",
            key="custom_drill_name"
        ).strip()
    else:
        st.session_state.drill = selected_drill

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

setter_options = setters(st.session_state.active_season_id)["Player"].tolist()
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


elif page == "👥 Roster":

    st.header("👥 Season Roster")

    season_id = st.session_state.active_season_id
    season_name = st.session_state.active_season_name

    st.write(f"Managing players for **{season_name}**.")

    roster = load_roster(season_id)

    # Add a player
    st.subheader("Add Player")

    with st.form("add_roster_player_form"):
        number = st.number_input(
            "Jersey Number",
            min_value=0,
            max_value=99,
            value=0,
            step=1
        )

        player = st.text_input("Player Name").strip()

        position = st.selectbox(
            "Position",
            ["OH", "MB", "S", "L/DS", "DS"]
        )

        add_submitted = st.form_submit_button("Add Player")

        if add_submitted:
            if not player:
                st.error("Please enter a player name.")
            else:
                try:
                    add_roster_player(
                        season_id,
                        int(number),
                        player,
                        position
                    )
                    st.success(f"Added {player} to {season_name}.")
                    st.rerun()
                except Exception as e:
                    st.error(
                        "Could not add the player. "
                        "They may already exist in this season."
                    )

    st.divider()

    # Display active players
    st.subheader("Current Roster")

    if roster.empty:
        st.info("No active players have been added to this season yet.")
    else:
        st.dataframe(
            roster[["Number", "Player", "Position"]],
            use_container_width=True,
            hide_index=True
        )

        # Edit an existing player
        st.subheader("Edit Player")

        player_options = roster["Player"].tolist()

        selected_player = st.selectbox(
            "Choose a player to edit",
            player_options,
            key="edit_roster_player"
        )

        selected_row = roster[
            roster["Player"] == selected_player
        ].iloc[0]

        with st.form("edit_roster_player_form"):
            new_number = st.number_input(
                "Jersey Number",
                min_value=0,
                max_value=99,
                value=int(selected_row["Number"])
                if pd.notna(selected_row["Number"]) else 0,
                step=1,
                key="edit_roster_number"
            )

            new_name = st.text_input(
                "Player Name",
                value=selected_player,
                key="edit_roster_name"
            ).strip()

            new_position = st.selectbox(
                "Position",
                ["OH", "MB", "S", "L/DS", "DS"],
                index=["OH", "MB", "S", "L/DS", "DS"].index(
                    selected_row["Position"]
                ),
                key="edit_roster_position"
            )

            edit_submitted = st.form_submit_button("Save Changes")

            if edit_submitted:
                if not new_name:
                    st.error("Please enter a player name.")
                else:
                    try:
                        update_roster_player(
                            int(selected_row["id"])
                            if "id" in selected_row.index
                            else -1,
                            int(new_number),
                            new_name,
                            new_position
                        )
                        st.success("Player updated.")
                        st.rerun()
                    except Exception:
                        st.error(
                            "Could not update the player. "
                            "Check whether the name already exists."
                        )

        # Deactivate a player
        st.subheader("Remove Player From Active Roster")

        remove_player = st.selectbox(
            "Choose a player to deactivate",
            player_options,
            key="remove_roster_player"
        )

        
    if st.button("Deactivate Player", key="start_deactivate_player"):
        st.session_state.confirm_roster_remove = True

    if st.session_state.get("confirm_roster_remove", False):
        st.warning(
            f"Deactivate {remove_player} from {season_name}? "
            "Their historical statistics will be preserved."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirm Deactivation", key="confirm_deactivate"):
                selected_remove_row = roster[
                    roster["Player"] == remove_player
                ].iloc[0]

                deactivate_roster_player(int(selected_remove_row["id"]))

                st.session_state.confirm_roster_remove = False
                st.success(f"{remove_player} was deactivated.")
                st.rerun()

        with col2:
            if st.button("Cancel", key="cancel_deactivate"):
                st.session_state.confirm_roster_remove = False
                st.rerun()


elif page == "⚙ Settings":

    st.header("Settings")

    st.subheader("Create a New Season")

    with st.form("create_season_form"):
        new_season_name = st.text_input(
            "Season Name",
            placeholder="e.g. 2027 Season"
        ).strip()

        create_season_submitted = st.form_submit_button(
            "Create Season"
        )

        if create_season_submitted:
            if not new_season_name:
                st.error("Please enter a season name.")
            else:
                try:
                    add_season(new_season_name)
                    st.success(
                        f"{new_season_name} was created successfully!"
                    )
                    st.rerun()
                except Exception:
                    st.error(
                        "That season may already exist. "
                        "Please use a different name."
                    )

    
    st.divider()
    st.subheader("Delete a Season")

    # Get the available seasons
    conn = get_connection()
    seasons_df = pd.read_sql_query(
        "SELECT id, season_name FROM seasons ORDER BY season_name",
        conn
    )
    conn.close()

    if seasons_df.empty:
        st.info("There are no seasons to delete.")
    else:
        season_to_delete = st.selectbox(
            "Select a season to delete",
            seasons_df["season_name"].tolist(),
            key="delete_season_selection"
        )

        st.warning(
            "Deleting a season removes its roster and season record. "
            "It may affect historical statistics if other tables still "
            "reference that season."
        )

        confirm_delete = st.checkbox(
            f"I want to delete {season_to_delete}",
            key="confirm_delete_season"
        )

        if st.button("Delete Season", type="secondary"):
            if not confirm_delete:
                st.error("Please confirm the season you want to delete.")
            elif season_to_delete == "2026 Season":
                st.error("The original 2026 Season cannot be deleted here.")
            else:
                try:
                    if delete_season(season_to_delete):
                        st.success(f"{season_to_delete} was deleted.")
                        st.rerun()
                    else:
                        st.error("Season not found.")
                except Exception as e:
                    st.error(f"Could not delete the season: {e}")