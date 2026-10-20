import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from database.queries import *
from utils.roster import load_roster


def reports_page():

    st.title("📊 Reports Dashboard")

    season_id = st.session_state.active_season_id

    st.divider()

    st.subheader("Filters")

    col1, col2, col3 = st.columns(3)

    with col1:

        session = st.selectbox(
            "Session",
            [
                "Practice",
                "Match"
        ]
        )

    with col2:

        practice_date = st.session_state.practice_date

    with col3:

        category = st.selectbox(
            "Category",
            [
                "Attack",
                "Serving",
                "Serve Receive",
                "Team Summary"
            ]
        )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    stats = get_attack_stats(practice_date, season_id, session_type=session)

    if stats.empty:

        attack_pct = 0.000
        kill_pct = 0.000

    else:

        total_kills = stats["Kills"].sum()
        total_errors = stats["Errors"].sum()
        total_attempts = stats["TotalAttempts"].sum()

        attack_pct = (
            (total_kills - total_errors)
            / total_attempts
            if total_attempts > 0 else 0
        )

        kill_pct = (
            total_kills
            / total_attempts
            if total_attempts > 0 else 0
        )

    # ---------- Serving ----------

    serving = get_serving_stats(practice_date, season_id)

    if serving.empty:

        serve_avg = 0.00

    else:

        total_score = (serving["Average"] * serving["Serves"]).sum()
        total_serves = serving["Serves"].sum()

        serve_avg = total_score / total_serves if total_serves > 0 else 0


    # ---------- Serve Receive ----------

    passing = get_serve_receive_stats(practice_date, season_id)

    if passing.empty:

        pass_avg = 0.00

    else:

        pass_avg = passing["Average"].mean()

    with c1:

        st.metric(
            "Attack %",
            f"{attack_pct:.3f}"
        )

    with c2:

        st.metric(
            "Kill %",
            f"{kill_pct:.3f}"
        )

    with c3:

        st.metric(
            "Serve Avg",
            f"{serve_avg:.2f}"
        )

    with c4:

        st.metric(
            "Pass Avg",
            f"{pass_avg:.2f}"
        )
        
    st.divider()

    st.subheader("📋 Master Practice Report")

    master = get_master_report(practice_date, season_id, session_type=session)

    st.dataframe(
        master,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("👤 Player Dashboard")

    player = st.selectbox(
        "Select Player",
        sorted(load_roster(st.session_state.active_season_id)["Player"]),
        key="player_dashboard"
    )

    attack = get_player_attack_stats(practice_date, player, season_id, session_type=session)
    serving_player = get_player_serving_stats(practice_date, player, season_id, session_type=session)
    passing_player = get_player_receive_stats(practice_date, player, season_id, session_type=session)

    kills = len(attack[attack["result"] == "K"])
    errors = len(attack[attack["result"] == "E"])
    attempts = len(attack)

    player_attack_pct = (
        (kills - errors) / attempts
        if attempts > 0 else 0
    )

    player_kill_pct = (
        kills / attempts
        if attempts > 0 else 0
    )

    player_serve_avg = (
        serving_player["result"].mean()
        if not serving_player.empty else 0
    )

    player_pass_avg = (
        passing_player["rating"].mean()
        if not passing_player.empty else 0
    )

    pc1, pc2, pc3, pc4 = st.columns(4)

    with pc1:
        st.metric("Attack %", f"{player_attack_pct:.3f}")

    with pc2:
        st.metric("Kill %", f"{player_kill_pct:.3f}")

    with pc3:
        st.metric("Serve Avg", f"{player_serve_avg:.2f}")

    with pc4:
        st.metric("Pass Avg", f"{player_pass_avg:.2f}")

    st.divider()

    st.subheader(f"📈 {player} Attack Breakdown")

    if not attack.empty:

        attack_by_setter = (
            attack.groupby("setter")
            .agg(
                Kills=("result", lambda x: (x == "K").sum()),
                Errors=("result", lambda x: (x == "E").sum()),
                Attempts=("result", "count")
            )
            .reset_index()
        )

        st.write("### By Setter")

        fig = go.Figure()

        fig.add_bar(
            x=attack_by_setter["setter"],
            y=attack_by_setter["Kills"],
            name="Kills",
            marker_color="green"
        )

        fig.add_bar(
            x=attack_by_setter["setter"],
            y=attack_by_setter["Attempts"],
            name="Attempts",
            marker_color="gold"
        )

        fig.add_bar(
            x=attack_by_setter["setter"],
            y=attack_by_setter["Errors"],
            name="Errors",
            marker_color="red"
        )

        fig.update_layout(
            title="Attack by Setter",
            barmode="group",
            xaxis_title="Setter",
            yaxis_title="Count"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.info("No attack data for this player.")

    if "attack_side" in attack.columns and not attack.empty:

        attack_by_side = (
        attack.groupby("attack_side")
        .agg(
            Kills=("result", lambda x: (x == "K").sum()),
            Errors=("result", lambda x: (x == "E").sum()),
            Attempts=("result", "count")
        )
        .reset_index()
    )

        st.write("### By Attack Side")

        fig = go.Figure()

        fig.add_bar(
            x=attack_by_side["attack_side"],
            y=attack_by_side["Kills"],
            name="Kills",
            marker_color="#0C7C59"
        )

        fig.add_bar(
            x=attack_by_side["attack_side"],
            y=attack_by_side["Attempts"],
            name="Attempts",
            marker_color="#FFC72C"
        )

        fig.add_bar(
            x=attack_by_side["attack_side"],
            y=attack_by_side["Errors"],
            name="Errors",
            marker_color="#C8102E"
        )

        fig.update_layout(
            barmode="group",
            xaxis_title="Attack Side",
            yaxis_title="Attempts",
            legend_title="Statistic"
        )

        st.plotly_chart(fig, use_container_width=True)
    

    if "rotation" in attack.columns and not attack.empty:

        attack_by_rotation = (
        attack.groupby("rotation")
        .agg(
            Kills=("result", lambda x: (x == "K").sum()),
            Errors=("result", lambda x: (x == "E").sum()),
            Attempts=("result", "count")
        )
        .reset_index()
    )

        st.write("### By Rotation")

        fig.add_bar(
            x=attack_by_rotation["rotation"],
            y=attack_by_rotation["Kills"],
            name="Kills",
            marker_color="#0C7C59"
        )

        fig.add_bar(
            x=attack_by_rotation["rotation"],
            y=attack_by_rotation["Attempts"],
            name="Attempts",
            marker_color="#FFC72C"
        )

        fig.add_bar(
            x=attack_by_rotation["rotation"],
            y=attack_by_rotation["Errors"],
            name="Errors",
            marker_color="#C8102E"
        )

        fig.update_layout(
            barmode="group",
            xaxis_title="Rotation",
            yaxis_title="Attempts",
            legend_title="Statistic"
        )

        st.plotly_chart(fig, use_container_width=True)

    
    # ---------- Player Comparison ----------

    st.divider()
    st.subheader("👥 Player Comparison")

    comparison_session = st.radio(
        "Compare data from:",
        ["Practice", "Match"],
        horizontal=True,
        key="comparison_session"
    )

    roster = load_roster(st.session_state.active_season_id)

    # Choose the position to compare
    position = st.selectbox(
        "Select Position",
        sorted(roster["Position"].dropna().unique()),
        key="comparison_position"
    )

    # Get players at the selected position
    position_players = sorted(
        roster.loc[
            roster["Position"] == position,
            "Player"
        ].dropna().unique()
    )

    if len(position_players) == 0:
        st.info("There are no active players at this position.")

    elif len(position_players) == 1:
        st.info("At least two active players at this position are needed to compare.")

    else:
        col1, col2 = st.columns(2)

        with col1:
            player1 = st.selectbox(
                "First Player",
                position_players,
                key="comparison_player1"
            )

        with col2:
            # Avoid selecting the same player twice
            player2_options = [
                name for name in position_players
                if name != player1
            ]

            player2 = st.selectbox(
                "Second Player",
                player2_options,
                key="comparison_player2"
            )

        st.info(
            f"Comparing {player1} and {player2} "
            f"using {comparison_session.lower()} data."
        )

        season_id = st.session_state.active_season_id

        # Get attacking statistics
        attack1 = get_player_attack_stats(
            practice_date, player1, season_id,
            session_type=comparison_session
        )

        attack2 = get_player_attack_stats(
            practice_date, player2, season_id,
            session_type=comparison_session
        )

        # Get serving statistics
        serve1 = get_player_serving_stats(
            practice_date, player1, season_id,
            session_type=comparison_session
        )

        serve2 = get_player_serving_stats(
            practice_date, player2, season_id,
            session_type=comparison_session
        )

        # Get serve-receive statistics
        pass1 = get_player_receive_stats(
            practice_date, player1, season_id,
            session_type=comparison_session
        )

        pass2 = get_player_receive_stats(
            practice_date, player2, season_id,
            session_type=comparison_session
        )

        st.subheader("Attacking Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{player1}**")
            st.dataframe(attack1, use_container_width=True)

        with col2:
            st.markdown(f"**{player2}**")
            st.dataframe(attack2, use_container_width=True)

        st.subheader("Serving Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{player1}**")
            st.dataframe(serve1, use_container_width=True)

        with col2:
            st.markdown(f"**{player2}**")
            st.dataframe(serve2, use_container_width=True)

        st.subheader("Serve-Receive Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{player1}**")
            st.dataframe(pass1, use_container_width=True)

        with col2:
            st.markdown(f"**{player2}**")
            st.dataframe(pass2, use_container_width=True)

    st.divider()

    st.subheader("Attack Statistics Breakdown")

    attack_breakdown = st.selectbox(
        "Separate attacking stats by:",
        [
            "Overall",
            "By Drill",
            "By Setter",
            "By Drill and Setter"
        ],
        key="attack_stats_breakdown"
    )

    if attack_breakdown == "Overall":
        attack_report = stats

    elif attack_breakdown == "By Drill":
        attack_report = get_attack_stats_by_drill(practice_date, season_id, session_type=session)

    elif attack_breakdown == "By Setter":
        attack_report = get_attack_stats_by_setter_total(practice_date, season_id, session_type=session)

    else:
        attack_report = get_attack_stats_by_drill_setter(practice_date, season_id, session_type=session)

    if attack_report.empty:
        st.info("No attacking stats recorded for this date.")

    else:
        st.dataframe(
            attack_report,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Serving Statistics")

    st.dataframe(
        serving,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Serve Receive Statistics")

    st.dataframe(
        passing,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📈 Trends")

    trend_type = st.radio(
        "Trend Type",
        [
            "Team",
            "Player"
        ],
        horizontal=True
    )

    player = None

    if trend_type == "Player":

        player = st.selectbox(
            "Select Player",
            sorted(load_roster(st.session_state.active_season_id)["Player"]),
            key="trend_player"
        )

    attack_trend = get_attack_trend(season_id, player, session_type=session)


    fig = px.line(
        attack_trend,
        x="practice_date",
        y="Attack %",
        markers=True,
        title="Attack Percentage"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        attack_trend,
        x="practice_date",
        y="Kill %",
        markers=True,
        title="Kill Percentage"
    )

    st.plotly_chart(fig, use_container_width=True)

    serve_trend = get_serving_trend(season_id, player, session_type=session)

    fig = px.line(
        serve_trend,
        x="practice_date",
        y="ServeAverage",
        markers=True,
        title="Serve Average"
    )

    st.plotly_chart(fig, use_container_width=True)

    pass_trend = get_passing_trend(season_id, player, session_type=session)

    fig = px.line(
        pass_trend,
        x="practice_date",
        y="PassAverage",
        markers=True,
        title="Pass Average"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        pass_trend,
        x="practice_date",
        y="Perfect %",
        markers=True,
        title="Perfect Pass Percentage"
    )

    st.plotly_chart(fig, use_container_width=True)

    