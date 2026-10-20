import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from database.queries import *
from utils.roster import load_roster

def normalize_stat(value, minimum, maximum):
    """Convert a statistic to a score from 0 to 100."""
    if value is None:
        return None

    score = (value - minimum) / (maximum - minimum) * 100
    return max(0, min(100, score))


def heatmap_color(score):
    """Return a red-yellow-green gradient color."""
    if score is None:
        return "#D1D5DB"  # Gray for missing values

    if score <= 50:
        # Red to yellow
        ratio = score / 50
        red = 255
        green = int(255 * ratio)
        blue = 0
    else:
        # Yellow to green
        ratio = (score - 50) / 50
        red = int(255 * (1 - ratio))
        green = 255
        blue = 0

    return f"#{red:02X}{green:02X}{blue:02X}"


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

    serving = get_serving_stats(practice_date, season_id, session_type=session)

    if serving.empty:

        serve_avg = 0.00

    else:

        total_score = (serving["Average"] * serving["Serves"]).sum()
        total_serves = serving["Serves"].sum()

        serve_avg = total_score / total_serves if total_serves > 0 else 0


    # ---------- Serve Receive ----------

    passing = get_serve_receive_stats(practice_date, season_id, session_type=session)

    if passing.empty:

        pass_avg = 0.00

    else:

        pass_avg = passing["Average"].mean()

    # ---------- KPI Dashboard ----------

    with c1:
        st.metric(
            label="🏐 Attack Percentage",
            value=f"{attack_pct:.3f}",
            help="(Kills - Errors) / Total Attempts"
        )

    with c2:
        st.metric(
            label="💥 Kill Percentage",
            value=f"{kill_pct:.1%}",
            help="Kills / Total Attempts"
        )

    with c3:
        st.metric(
            label="🚀 Serve Average",
            value=f"{serve_avg:.2f}",
            help="Average serving rating"
        )

    with c4:
        st.metric(
            label="🎯 Pass Average",
            value=f"{pass_avg:.2f}",
            help="Average serve-receive rating"
        )

    
    
    # ---------- Setter-Attacker Connection Matrix ----------

    st.divider()
    st.subheader("🏐 Setter–Attacker Connections")

    conn = get_connection()

    connection_data = pd.read_sql_query(
        """
        SELECT setter, attacker, result
        FROM attacks
        WHERE practice_date = ?
          AND season_id = ?
          AND session_type = ?
        """,
        conn,
        params=(practice_date, season_id, session)
    )

    conn.close()

    if not connection_data.empty:
        connection_summary = (
            connection_data.groupby(["setter", "attacker"])
            .agg(
                Kills=("result", lambda x: (x == "K").sum()),
                Errors=("result", lambda x: (x == "E").sum()),
                Attempts=("result", "count")
            )
            .reset_index()
        )

        connection_summary["Attack %"] = (
            (connection_summary["Kills"] - connection_summary["Errors"])
            / connection_summary["Attempts"]
        )

        connection_matrix = connection_summary.pivot(
            index="attacker",
            columns="setter",
            values="Attack %"
        )

        fig = px.imshow(
            connection_matrix,
            labels={
                "x": "Setter",
                "y": "Attacker",
                "color": "Attack %"
            },
            color_continuous_scale="RdYlGn",
            aspect="auto",
            text_auto=".3f",
            title="Attack Percentage by Setter and Attacker"
        )

        fig.update_layout(
            coloraxis_colorbar_title="Attack %"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No attack data available for this date and session.")

    st.divider()

    st.subheader("📋 Master Practice Report")

    master = get_master_report(practice_date, season_id, session_type=session)

    st.dataframe(
        master,
        use_container_width=True,
        hide_index=True
    )

    
    # ---------- Player Performance Heatmap ----------

    st.divider()
    st.subheader("🔥 Team Player Performance Heatmap")

    roster = load_roster(st.session_state.active_season_id)
    active_players = sorted(roster["Player"].dropna().unique())

    if active_players:
        heatmap_rows = []

        for player_name in active_players:
            player_attack = get_player_attack_stats(
                practice_date,
                player_name,
                season_id,
                session_type=session
            )

            player_serving = get_player_serving_stats(
                practice_date,
                player_name,
                season_id,
                session_type=session
            )

            player_passing = get_player_receive_stats(
                practice_date,
                player_name,
                season_id,
                session_type=session
            )

            kills = (player_attack["result"] == "K").sum()
            errors = (player_attack["result"] == "E").sum()
            attempts = len(player_attack)

            player_attack_pct = (
                (kills - errors) / attempts if attempts > 0 else 0
            )

            player_serve_avg = (
                player_serving["result"].mean()
                if not player_serving.empty else 0
            )

            player_pass_avg = (
                player_passing["rating"].mean()
                if not player_passing.empty else 0
            )

            heatmap_rows.append({
                "Player": player_name,
                "Attack %": player_attack_pct,
                "Serve Avg": player_serve_avg,
                "Pass Avg": player_pass_avg
            })

        
        # Keep the original statistics for displaying on the heat map
        heatmap_df = pd.DataFrame(heatmap_rows).set_index("Player")

        # Normalize each statistic separately to a 0-100 scale
        normalized_df = heatmap_df.copy()

        normalized_df["Attack %"] = normalized_df["Attack %"].apply(
            lambda x: normalize_stat(x, -1, 1)
        )

        normalized_df["Serve Avg"] = normalized_df["Serve Avg"].apply(
            lambda x: normalize_stat(x, 0, 4)
        )

        normalized_df["Pass Avg"] = normalized_df["Pass Avg"].apply(
            lambda x: normalize_stat(x, 0, 3)
        )

        # Draw the heat map using normalized values
        fig = px.imshow(
            normalized_df,
            labels=dict(
                x="Statistic",
                y="Player",
                color="Performance Score"
        ),
            color_continuous_scale=[
                [0.0, "red"],
                [0.5, "yellow"],
                [1.0, "green"]
            ],
            zmin=0,
            zmax=100,
            aspect="auto",
            text_auto=False
        )

        # Display the original statistic values inside each cell
        for row_index, player in enumerate(heatmap_df.index):
            for col_index, stat in enumerate(heatmap_df.columns):
                value = heatmap_df.iloc[row_index, col_index]

                if pd.notna(value):
                    fig.add_annotation(
                        x=col_index,
                        y=row_index,
                        text=f"{value:.2f}",
                        showarrow=False,
                        font=dict(color="black", size=12)
                    )

        fig.update_layout(
            title="Player Performance by Statistic",
            height=max(350, len(active_players) * 35),
            coloraxis_colorbar=dict(
                title="Performance",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["Worst", "Low", "Average", "High", "Best"]
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No active players found in this season's roster.")


    st.divider()

    st.subheader("👤 Player Dashboard")

    player = st.selectbox(
        "Select Player",
        sorted(load_roster(st.session_state.active_season_id)["Player"]),
        key="player_dashboard"
    )

    attack = get_player_attack_stats(practice_date, player, season_id, session_type=session)

    
    # ---------- Six-Zone Attack Court ----------
    st.divider()
    st.subheader("🏐 Attack Target Zones")

    conn = get_connection()

    zone_data = pd.read_sql_query(
        """
        SELECT target_zone, result
        FROM attacks
        WHERE season_id = ?
        AND session_type = ?
        AND target_zone IS NOT NULL
        """,
        conn,
        params=(season_id, session)
    )

    conn.close()

    if not zone_data.empty:
        zone_summary = (
            zone_data.groupby(["target_zone", "result"])
            .size()
            .unstack(fill_value=0)
        )

        # Make sure all outcome columns exist
        for outcome in ["K", "E", "A"]:
            if outcome not in zone_summary.columns:
                zone_summary[outcome] = 0

        # Draw six court zones
        fig = go.Figure()

        zone_positions = {
            4: (0, 1),
            3: (1, 1),
            2: (2, 1),
            5: (0, 0),
            6: (1, 0),
            1: (2, 0)
        }

        for zone, (x, y) in zone_positions.items():
            kills = int(zone_summary.loc[zone, "K"]) if zone in zone_summary.index else 0
            errors = int(zone_summary.loc[zone, "E"]) if zone in zone_summary.index else 0
            attempts = int(zone_summary.loc[zone, "A"]) if zone in zone_summary.index else 0
            total = kills + errors + attempts

            
            # Calculate attack success for this zone
            success_rate = (kills / total) if total > 0 else 0

            # Color zones based on kill percentage
            if total == 0:
                zone_color = "#E5E7EB"  # Gray: no attacks
            elif success_rate >= 0.50:
                zone_color = "#86EFAC"  # Green: high kill rate
            elif success_rate >= 0.30:
                zone_color = "#FDE68A"  # Yellow: medium kill rate
            else:
                zone_color = "#FCA5A5"  # Red: low kill rate

            fig.add_shape(
                type="rect",
                x0=x, y0=y, x1=x + 1, y1=y + 1,
                line=dict(color="white", width=3),
                fillcolor=zone_color
            )

            fig.add_annotation(
                x=x + 0.5,
                y=y + 0.5,
                text=(
                    f"<b>Zone {zone}</b><br>"
                    f"Attacks: {total}<br>"
                    f"Kill rate: {success_rate:.1%}<br>"
                    f"🟢 Kills: {kills}<br>"
                    f"🔴 Errors: {errors}<br>"
                    f"🟡 In play: {attempts}"
                ),
                showarrow=False,
                font=dict(size=13, color="#111827")
            )

        fig.update_layout(
            title="Attack Results by Target Zone",
            xaxis=dict(range=[0, 3], visible=False, fixedrange=True),
            yaxis=dict(range=[0, 2], visible=False, fixedrange=True),
            height=450,
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            "**Zone Colors:** "
            "🟢 Green = 50%+ kill rate | "
            "🟡 Yellow = 30–49% | "
            "🔴 Red = below 30% | "
            "⬜ Gray = no attacks"
        )

        st.caption(
            "Zones follow standard volleyball numbering. "
            "Only attacks with a recorded target zone are included."
        )
    else:
        st.info(
            "No attacks with target zones recorded for this date and session yet. "
            "Select a zone when entering attacks to populate this court."
        )
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

    