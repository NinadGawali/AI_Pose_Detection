"""
Teacher Dashboard — Command Intelligence Center
Redesigned with military dark aesthetic + rich cadet analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_manager import DataManager
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════════
# SHARED CSS
# ═══════════════════════════════════════════════════════════════════════════

TEACHER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600;700&family=Barlow:wght@300;400;500;600&display=swap');

:root {
    --dark:    #07080d;
    --dark2:   #0e1018;
    --panel:   #12141c;
    --panel2:  #161820;
    --border:  #1e2130;
    --border2: #252838;
    --gold:    #c8a96e;
    --gold2:   #a07840;
    --blue:    #4a90d9;
    --green:   #4caf82;
    --red:     #e05c6a;
    --amber:   #e8a03a;
    --text:    #c8cce0;
    --muted:   #4a4f6a;
}

.stApp { background: var(--dark) !important; font-family: 'Barlow', sans-serif; }
.block-container { padding: 1.5rem 2rem 4rem !important; max-width: 1400px !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── Command header ── */
.cmd-header {
    background: linear-gradient(135deg, #0e1018 0%, #12141c 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.cmd-header-left {}
.cmd-header-eyebrow {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 11px; font-weight: 700;
    letter-spacing: 4px; text-transform: uppercase;
    color: var(--gold); margin-bottom: 6px;
}
.cmd-header-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 44px; letter-spacing: 2px;
    color: #fff; line-height: 1;
}
.cmd-header-sub {
    font-family: 'Barlow', sans-serif;
    font-size: 14px; color: var(--muted);
    margin-top: 6px;
}
.cmd-header-badge {
    background: var(--gold);
    color: var(--dark);
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 6px 16px; border-radius: 99px;
}

/* ── KPI cards ── */
.kpi-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--kpi-color, var(--gold));
}
.kpi-icon { font-size: 22px; margin-bottom: 10px; }
.kpi-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 46px; line-height: 1;
    color: var(--kpi-color, var(--gold));
    margin-bottom: 4px;
}
.kpi-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 11px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--muted);
}
.kpi-delta {
    font-family: 'Barlow', sans-serif;
    font-size: 12px; margin-top: 6px;
    color: var(--muted);
}

/* ── Section titles ── */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 26px; letter-spacing: 2px;
    color: #fff; margin-bottom: 4px;
}
.section-sub {
    font-family: 'Barlow', sans-serif;
    font-size: 13px; color: var(--muted);
    margin-bottom: 20px;
}

/* ── Panel / card container ── */
.dash-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}

/* ── Student roster row ── */
.roster-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    margin-bottom: 8px;
    background: var(--panel2);
    transition: border-color 0.2s;
}
.roster-row:hover { border-color: var(--border2); }
.roster-avatar {
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 18px; color: #fff;
    flex-shrink: 0;
}
.roster-name {
    font-family: 'Barlow', sans-serif;
    font-size: 15px; font-weight: 600;
    color: var(--text); flex: 1;
}
.roster-id {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 12px; color: var(--muted);
    letter-spacing: 1px;
}
.roster-score {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
}
.roster-badge {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 4px 10px; border-radius: 99px;
}

/* ── Insight cards ── */
.insight-card {
    background: var(--panel2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
    border-left: 3px solid var(--ins-color, var(--gold));
}
.insight-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--ins-color, var(--gold));
    margin-bottom: 5px;
}
.insight-text {
    font-family: 'Barlow', sans-serif;
    font-size: 14px; color: var(--text);
    line-height: 1.5;
}

/* ── Activity feed ── */
.activity-row {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
}
.activity-row:last-child { border-bottom: none; }
.activity-dot {
    width: 8px; height: 8px;
    border-radius: 50%; flex-shrink: 0;
}
.activity-info { flex: 1; }
.activity-name {
    font-family: 'Barlow', sans-serif;
    font-size: 14px; font-weight: 600; color: var(--text);
}
.activity-detail {
    font-family: 'Barlow', sans-serif;
    font-size: 12px; color: var(--muted); margin-top: 1px;
}
.activity-score {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
}

/* ── Plotly chart dark theme ── */
.js-plotly-plot { background: transparent !important; }

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--gold) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 8px !important;
    margin-bottom: 24px !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] {
    background: var(--panel) !important;
    border-color: var(--border2) !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] * { color: var(--text) !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* ── Rank badge colors ── */
.rank-1 { background: #c8a96e22; color: #c8a96e; border: 1px solid #c8a96e44; }
.rank-2 { background: #c0c0c022; color: #c0c0c0; border: 1px solid #c0c0c044; }
.rank-3 { background: #cd7f3222; color: #cd7f32; border: 1px solid #cd7f3244; }
.rank-n { background: #1e213022; color: #4a4f6a; border: 1px solid #1e213044; }
</style>
"""


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Barlow Condensed", color="#c8cce0", size=12),
    xaxis=dict(gridcolor="#1e2130", linecolor="#1e2130", zerolinecolor="#1e2130"),
    yaxis=dict(gridcolor="#1e2130", linecolor="#1e2130", zerolinecolor="#1e2130"),
    margin=dict(l=10, r=10, t=40, b=10),
)

POSE_COLORS = {
    "Savdhan (Attention)":    "#c8a96e",
    "Vishram (Stand at Ease)":"#4a90d9",
    "Salute":                 "#e8916a",
    "Dahine Mud (Right Turn)":"#a78bdb",
    "Bahine Mud (Left Turn)": "#4caf82",
    "Pichhe Mud (About Turn)":"#e87a8a",
}

def acc_color(v):
    if v >= 85:  return "#4caf82"
    if v >= 70:  return "#4a90d9"
    if v >= 50:  return "#e8a03a"
    return "#e05c6a"

def acc_label(v):
    if v >= 85:  return "EXCELLENT"
    if v >= 70:  return "GOOD"
    if v >= 50:  return "FAIR"
    return "NEEDS WORK"

def rank_badge_class(i):
    return ["rank-1","rank-2","rank-3"][i] if i < 3 else "rank-n"

def rank_icon(i):
    return ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"

def avatar_color(i):
    palette = ["#c8a96e","#4a90d9","#4caf82","#e8916a","#a78bdb","#e87a8a","#7eb8c9"]
    return palette[i % len(palette)]

def kpi_html(icon, value, label, color, delta=""):
    return (
        '<div class="kpi-card" style="--kpi-color:' + color + ';">'
        '<div class="kpi-icon">' + icon + '</div>'
        '<div class="kpi-value">' + str(value) + '</div>'
        '<div class="kpi-label">' + label + '</div>'
        + ('<div class="kpi-delta">' + delta + '</div>' if delta else '') +
        '</div>'
    )

def insight_html(label, text, color):
    return (
        '<div class="insight-card" style="--ins-color:' + color + ';">'
        '<div class="insight-label">' + label + '</div>'
        '<div class="insight-text">' + text + '</div>'
        '</div>'
    )

def generate_insights(students_summary, pose_stats):
    """Generate actionable instructor insights from data."""
    insights = []

    if not students_summary:
        return insights

    df = pd.DataFrame(students_summary)

    # Top performer
    top = df.loc[df["Avg_Accuracy"].idxmax()]
    insights.append(("🏆 TOP PERFORMER", f"<b>{top['Student_Name']}</b> leads with <b>{top['Avg_Accuracy']}%</b> avg accuracy across {int(top['Total_Sessions'])} sessions.", "#c8a96e"))

    # Needs attention
    low = df[df["Avg_Accuracy"] < 50]
    if not low.empty:
        names = ", ".join(low["Student_Name"].tolist())
        insights.append(("⚠️ NEEDS ATTENTION", f"<b>{names}</b> scored below 50%. Consider dedicated one-on-one drill review.", "#e05c6a"))

    # Most improved (highest session count with decent accuracy)
    active = df[df["Total_Sessions"] >= 3].nlargest(1, "Total_Sessions")
    if not active.empty:
        a = active.iloc[0]
        insights.append(("📈 MOST DEDICATED", f"<b>{a['Student_Name']}</b> has completed <b>{int(a['Total_Sessions'])}</b> sessions — the most of any cadet.", "#4a90d9"))

    # Hardest pose
    if pose_stats:
        ps = pd.DataFrame(pose_stats).T.reset_index()
        ps.columns = ["Pose", "Average", "Sessions", "Best", "Worst"]
        hardest = ps.loc[ps["Average"].idxmin()]
        insights.append(("🎯 UNIT WEAKNESS", f"<b>{hardest['Pose']}</b> has the lowest avg accuracy at <b>{hardest['Average']}%</b>. Schedule extra drills.", "#e8a03a"))

        easiest = ps.loc[ps["Average"].idxmax()]
        insights.append(("✅ UNIT STRENGTH", f"<b>{easiest['Pose']}</b> is the strongest command — avg <b>{easiest['Average']}%</b>.", "#4caf82"))

    # Consistency check (gap between best and worst)
    df["spread"] = df["Max_Accuracy"] - df["Min_Accuracy"]
    inconsistent = df.nlargest(1, "spread")
    if not inconsistent.empty:
        row = inconsistent.iloc[0]
        insights.append(("📊 INCONSISTENT PERFORMANCE", f"<b>{row['Student_Name']}</b> has a large score spread ({row['Min_Accuracy']}% – {row['Max_Accuracy']}%). May need consistency drills.", "#a78bdb"))

    return insights


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════════════════

def show_teacher_dashboard(username, full_name):
    st.markdown(TEACHER_CSS, unsafe_allow_html=True)

    # Header
    now_str = datetime.now().strftime("%d %b %Y  •  %H:%M")
    st.markdown(
        '<div class="cmd-header">'
        '<div class="cmd-header-left">'
        '<div class="cmd-header-eyebrow">Command Intelligence Center</div>'
        '<div class="cmd-header-title">INSTRUCTOR PORTAL</div>'
        '<div class="cmd-header-sub">Signed in as <b style="color:#c8cce0;">' + full_name + '</b> &nbsp;·&nbsp; ' + now_str + '</div>'
        '</div>'
        '<div class="cmd-header-badge">🎖 Instructor Access</div>'
        '</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📡  OVERVIEW",
        "🪖  CADET ROSTER",
        "🔍  INDIVIDUAL DRILL",
        "📊  POSE ANALYSIS",
        "💡  INSIGHTS",
    ])

    with tab1: _tab_overview()
    with tab2: _tab_roster()
    with tab3: _tab_individual()
    with tab4: _tab_pose_analysis()
    with tab5: _tab_insights()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════

def _tab_overview():
    dm = DataManager()
    summary    = dm.get_all_students_summary()
    activities = dm.get_recent_activities(limit=20)
    pose_stats = dm.get_pose_statistics()

    if not summary:
        st.info("No cadet data yet. Students need to complete practice sessions.")
        return

    df = pd.DataFrame(summary)
    total_students  = len(df)
    total_sessions  = int(df["Total_Sessions"].sum())
    avg_acc         = round(df["Avg_Accuracy"].mean(), 1)
    top             = df.loc[df["Avg_Accuracy"].idxmax()]
    active_today    = 0
    if activities:
        today = datetime.now().strftime("%Y-%m-%d")
        active_today = len(set(a["Student_Name"] for a in activities if str(a.get("Date","")) == today))

    # ── KPI row ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "🪖", str(total_students), "CADETS ENROLLED",   "#c8a96e", ""),
        (c2, "📋", str(total_sessions), "TOTAL SESSIONS",    "#4a90d9", ""),
        (c3, "🎯", f"{avg_acc}%",       "UNIT AVG ACCURACY", acc_color(avg_acc), acc_label(avg_acc)),
        (c4, "🏆", str(top["Student_Name"]).split()[0], "TOP PERFORMER", "#4caf82", f"{top['Avg_Accuracy']}% avg"),
        (c5, "⚡", str(active_today),   "ACTIVE TODAY",      "#e8a03a", "cadets"),
    ]
    for col, icon, val, label, color, delta in cards:
        with col:
            st.markdown(kpi_html(icon, val, label, color, delta), unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── Main split: Activity feed | Performance heatmap ──────────────────
    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.markdown('<div class="section-title">LIVE FEED</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Most recent cadet practice sessions</div>', unsafe_allow_html=True)

        if activities:
            for act in activities[:12]:
                score = float(act.get("Accuracy", 0))
                color = acc_color(score)
                st.markdown(
                    '<div class="activity-row">'
                    '<div class="activity-dot" style="background:' + color + ';"></div>'
                    '<div class="activity-info">'
                    '<div class="activity-name">' + str(act["Student_Name"]) + ' &mdash; ' + str(act["Pose_Type"]) + '</div>'
                    '<div class="activity-detail">📅 ' + str(act["Date"]) + ' at ' + str(act["Time"]) + '</div>'
                    '</div>'
                    '<div class="activity-score" style="color:' + color + ';">' + str(round(score, 1)) + '%</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No activity yet.")

    with right:
        st.markdown('<div class="section-title">UNIT PERFORMANCE</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Average accuracy per cadet</div>', unsafe_allow_html=True)

        df_sorted = df.sort_values("Avg_Accuracy", ascending=True)
        colors_bar = [acc_color(v) for v in df_sorted["Avg_Accuracy"]]

        fig = go.Figure(go.Bar(
            x=df_sorted["Avg_Accuracy"],
            y=df_sorted["Student_Name"],
            orientation="h",
            marker_color=colors_bar,
            text=[f'{v:.1f}%' for v in df_sorted["Avg_Accuracy"]],
            textposition="outside",
            textfont=dict(color="#c8cce0", size=12),
        ))
        fig.add_vline(x=70, line_dash="dash", line_color="#4a4f6a",
                      annotation_text="Target 70%", annotation_font_color="#4a4f6a")
        fig.update_layout(
            **PLOTLY_DARK,
            xaxis_range=[0, 110],
            height=max(280, total_students * 44),
            showlegend=False,
            bargap=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Pose performance radar ─────────────────────────────────────────────
    if pose_stats:
        st.markdown("---")
        st.markdown('<div class="section-title">POSE COMMAND RADAR</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Unit-wide average accuracy across all six drill commands</div>', unsafe_allow_html=True)

        ps = pd.DataFrame(pose_stats).T.reset_index()
        ps.columns = ["Pose", "Average", "Sessions", "Best", "Worst"]
        ps["Average"] = ps["Average"].astype(float)

        fig_r = go.Figure(go.Scatterpolar(
            r=list(ps["Average"]) + [ps["Average"].iloc[0]],
            theta=list(ps["Pose"]) + [ps["Pose"].iloc[0]],
            fill="toself",
            fillcolor="rgba(200,169,110,0.12)",
            line=dict(color="#c8a96e", width=2),
            marker=dict(color="#c8a96e", size=7),
        ))
        fig_r.update_layout(
            **PLOTLY_DARK,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e2130",
                                tickfont=dict(color="#4a4f6a", size=10)),
                angularaxis=dict(gridcolor="#1e2130", tickfont=dict(color="#c8cce0", size=11)),
            ),
            height=380,
        )
        st.plotly_chart(fig_r, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — CADET ROSTER
# ═══════════════════════════════════════════════════════════════════════════

def _tab_roster():
    dm = DataManager()
    summary = dm.get_all_students_summary()

    if not summary:
        st.info("No cadet data available yet.")
        return

    df = pd.DataFrame(summary).sort_values("Avg_Accuracy", ascending=False).reset_index(drop=True)

    st.markdown('<div class="section-title">CADET ROSTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ranked by average accuracy · click a row to drill down</div>', unsafe_allow_html=True)

    # ── Roster cards ──────────────────────────────────────────────────────
    for i, row in df.iterrows():
        score  = float(row["Avg_Accuracy"])
        color  = acc_color(score)
        avatar = avatar_color(i)
        initials = "".join([w[0].upper() for w in str(row["Student_Name"]).split()[:2]])

        st.markdown(
            '<div class="roster-row">'
            '<div class="roster-avatar" style="background:' + avatar + '22;color:' + avatar + ';border:1px solid ' + avatar + '44;">' + initials + '</div>'
            '<div style="flex:1">'
            '<div class="roster-name">' + str(row["Student_Name"]) + '</div>'
            '<div class="roster-id">' + str(row["Student_ID"]) + ' &nbsp;·&nbsp; ' + str(int(row["Total_Sessions"])) + ' sessions &nbsp;·&nbsp; Last: ' + str(row["Last_Practice"]) + '</div>'
            '</div>'
            '<div class="roster-badge ' + rank_badge_class(i) + '">' + rank_icon(i) + '</div>'
            '&nbsp;&nbsp;'
            '<div class="roster-score" style="color:' + color + ';">' + f'{score:.1f}%' + '</div>'
            '&nbsp;&nbsp;'
            '<div class="roster-badge" style="background:' + color + '22;color:' + color + ';border:1px solid ' + color + '44;">' + acc_label(score) + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Comparison chart ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">SCORE RANGE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Best, average and lowest score per cadet</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Best", x=df["Student_Name"], y=df["Max_Accuracy"],
                         marker_color="#4caf82", opacity=0.85))
    fig.add_trace(go.Bar(name="Average", x=df["Student_Name"], y=df["Avg_Accuracy"],
                         marker_color="#c8a96e", opacity=0.9))
    fig.add_trace(go.Bar(name="Lowest", x=df["Student_Name"], y=df["Min_Accuracy"],
                         marker_color="#e05c6a", opacity=0.7))
    fig.update_layout(**PLOTLY_DARK, barmode="group", height=340,
                      yaxis_range=[0, 105], legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)

    # ── Sessions distribution ─────────────────────────────────────────────
    st.markdown('<div class="section-title">TRAINING VOLUME</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(df, values="Total_Sessions", names="Student_Name",
                      color_discrete_sequence=["#c8a96e","#4a90d9","#4caf82","#e8916a","#a78bdb","#e87a8a"])
        fig2.update_layout(**PLOTLY_DARK, height=300,
                           legend=dict(font=dict(color="#c8cce0")))
        fig2.update_traces(textfont_color="#07080d")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = go.Figure(go.Bar(
            x=df["Student_Name"], y=df["Total_Sessions"],
            marker_color=[avatar_color(i) for i in range(len(df))],
            text=df["Total_Sessions"], textposition="outside",
            textfont=dict(color="#c8cce0"),
        ))
        fig3.update_layout(**PLOTLY_DARK, height=300, showlegend=False,
                           yaxis_title="Sessions")
        st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — INDIVIDUAL DRILL
# ═══════════════════════════════════════════════════════════════════════════

def _tab_individual():
    dm = DataManager()
    summary = dm.get_all_students_summary()

    if not summary:
        st.info("No cadet data available yet.")
        return

    options = {s["Student_Name"]: s["Student_ID"] for s in summary}
    selected_name = st.selectbox("Select Cadet", list(options.keys()), key="ind_select")
    selected_id   = options[selected_name]

    stats = dm.get_student_stats(selected_id)
    if not stats:
        st.warning("No data for this cadet.")
        return

    # ── Mini KPI row ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    mini = [
        (c1, "📋", str(stats["total_sessions"]),    "SESSIONS",      "#4a90d9"),
        (c2, "🎯", f"{stats['avg_accuracy']}%",     "AVG ACCURACY",  acc_color(stats["avg_accuracy"])),
        (c3, "🏅", f"{stats['max_accuracy']}%",     "BEST SCORE",    "#4caf82"),
        (c4, "📉", f"{stats['min_accuracy']}%",     "LOWEST SCORE",  "#e05c6a"),
    ]
    for col, icon, val, label, color in mini:
        with col:
            st.markdown(kpi_html(icon, val, label, color), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if not stats["recent_sessions"]:
        st.info("No sessions recorded yet.")
        return

    df_s = pd.DataFrame(stats["recent_sessions"])
    df_s["Session"] = range(1, len(df_s) + 1)
    df_s["Accuracy"] = df_s["Accuracy"].astype(float)

    # ── Progress line chart ───────────────────────────────────────────────
    st.markdown('<div class="section-title">PROGRESS TRAJECTORY</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Accuracy over time — each point is one session</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_hrect(y0=85, y1=100, fillcolor="#4caf82", opacity=0.04, line_width=0)
    fig.add_hrect(y0=70, y1=85,  fillcolor="#4a90d9", opacity=0.04, line_width=0)
    fig.add_hrect(y0=50, y1=70,  fillcolor="#e8a03a", opacity=0.04, line_width=0)
    fig.add_hrect(y0=0,  y1=50,  fillcolor="#e05c6a", opacity=0.04, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color="#4a4f6a",
                  annotation_text="Target", annotation_font_color="#4a4f6a")

    fig.add_trace(go.Scatter(
        x=df_s["Session"], y=df_s["Accuracy"],
        mode="lines+markers",
        line=dict(color="#c8a96e", width=2.5),
        marker=dict(size=9, color=df_s["Accuracy"].apply(acc_color),
                    line=dict(color="#07080d", width=2)),
        hovertemplate="Session %{x}<br>Accuracy: %{y:.1f}%<br>Pose: " +
                      df_s.get("Pose_Type", pd.Series([""] * len(df_s))).fillna("").tolist()[0] +
                      "<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_DARK, height=300, yaxis_range=[0, 105],
                      xaxis_title="Session #", yaxis_title="Accuracy (%)")
    st.plotly_chart(fig, use_container_width=True)

    # ── Pose breakdown for this cadet ─────────────────────────────────────
    st.markdown('<div class="section-title">POSE BREAKDOWN</div>', unsafe_allow_html=True)
    pose_df = df_s.groupby("Pose_Type")["Accuracy"].agg(["mean","count","max","min"]).reset_index()
    pose_df.columns = ["Pose", "Avg %", "Sessions", "Best %", "Worst %"]
    pose_df = pose_df.sort_values("Avg %", ascending=False)

    col1, col2 = st.columns([1.2, 1], gap="large")
    with col1:
        fig_p = go.Figure(go.Bar(
            x=pose_df["Pose"], y=pose_df["Avg %"],
            marker_color=[POSE_COLORS.get(p, "#c8a96e") for p in pose_df["Pose"]],
            text=[f'{v:.1f}%' for v in pose_df["Avg %"]],
            textposition="outside",
            textfont=dict(color="#c8cce0"),
        ))
        fig_p.add_hline(y=70, line_dash="dash", line_color="#4a4f6a")
        fig_p.update_layout(**PLOTLY_DARK, height=300, yaxis_range=[0, 110],
                            showlegend=False, xaxis_tickangle=-25)
        st.plotly_chart(fig_p, use_container_width=True)

    with col2:
        # Strengths and weaknesses
        strong = pose_df[pose_df["Avg %"] >= 70]
        weak   = pose_df[pose_df["Avg %"] < 70]

        if not strong.empty:
            st.markdown('<div class="section-title" style="font-size:18px;">✅ STRENGTHS</div>', unsafe_allow_html=True)
            for _, r in strong.iterrows():
                st.markdown(
                    insight_html("STRONG", f'<b>{r["Pose"]}</b> — {r["Avg %"]:.1f}% avg over {int(r["Sessions"])} sessions', "#4caf82"),
                    unsafe_allow_html=True
                )

        if not weak.empty:
            st.markdown('<div class="section-title" style="font-size:18px;margin-top:16px;">❌ NEEDS WORK</div>', unsafe_allow_html=True)
            for _, r in weak.iterrows():
                st.markdown(
                    insight_html("WEAK", f'<b>{r["Pose"]}</b> — {r["Avg %"]:.1f}% avg. Focus required.', "#e05c6a"),
                    unsafe_allow_html=True
                )

    # ── Session log table ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">SESSION LOG</div>', unsafe_allow_html=True)

    display = df_s[["Date", "Time", "Pose_Type", "Accuracy", "Duration_Seconds"]].copy()
    display.columns = ["Date", "Time", "Pose", "Accuracy (%)", "Duration (s)"]
    display["Accuracy (%)"] = display["Accuracy (%)"].round(1)
    st.dataframe(
        display.style.background_gradient(subset=["Accuracy (%)"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True, hide_index=True
    )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — POSE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def _tab_pose_analysis():
    dm = DataManager()
    pose_stats = dm.get_pose_statistics()

    if not pose_stats:
        st.info("No pose data available yet.")
        return

    ps = pd.DataFrame(pose_stats).T.reset_index()
    ps.columns = ["Pose", "Average", "Sessions", "Best", "Worst"]
    ps[["Average","Sessions","Best","Worst"]] = ps[["Average","Sessions","Best","Worst"]].astype(float)
    ps = ps.sort_values("Average", ascending=False).reset_index(drop=True)

    # ── Difficulty ranking cards ─────────────────────────────────────────
    st.markdown('<div class="section-title">COMMAND DIFFICULTY RANKING</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ranked easiest → hardest by unit-wide average accuracy</div>', unsafe_allow_html=True)

    cols = st.columns(len(ps))
    for i, (col, (_, row)) in enumerate(zip(cols, ps.iterrows())):
        color = acc_color(row["Average"])
        with col:
            st.markdown(
                '<div class="kpi-card" style="--kpi-color:' + color + ';">'
                '<div class="kpi-icon">' + POSE_COLORS.get(row["Pose"], "") + '</div>'
                '<div style="font-size:11px;font-weight:700;letter-spacing:2px;color:' + color + ';text-transform:uppercase;margin-bottom:8px;">' + rank_icon(i) + '</div>'
                '<div class="kpi-value" style="font-size:36px;">' + f'{row["Average"]:.0f}%' + '</div>'
                '<div class="kpi-label">' + str(row["Pose"]).split("(")[0].strip().upper() + '</div>'
                '<div class="kpi-delta">' + str(int(row["Sessions"])) + ' sessions</div>'
                '</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── Dual chart: avg accuracy + session count ──────────────────────────
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-title">AVG ACCURACY BY POSE</div>', unsafe_allow_html=True)
        fig1 = go.Figure(go.Bar(
            x=ps["Pose"], y=ps["Average"],
            marker_color=[acc_color(v) for v in ps["Average"]],
            text=[f'{v:.1f}%' for v in ps["Average"]],
            textposition="outside", textfont=dict(color="#c8cce0"),
        ))
        fig1.add_hline(y=70, line_dash="dash", line_color="#4a4f6a",
                       annotation_text="Target 70%", annotation_font_color="#4a4f6a")
        fig1.update_layout(**PLOTLY_DARK, height=320, yaxis_range=[0, 110],
                           showlegend=False, xaxis_tickangle=-20)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">PRACTICE VOLUME BY POSE</div>', unsafe_allow_html=True)
        fig2 = px.pie(ps, values="Sessions", names="Pose",
                      color_discrete_sequence=list(POSE_COLORS.values()))
        fig2.update_layout(**PLOTLY_DARK, height=320,
                           legend=dict(font=dict(color="#c8cce0", size=11)))
        fig2.update_traces(textfont_color="#07080d")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Best vs Worst per pose ────────────────────────────────────────────
    st.markdown('<div class="section-title">SCORE RANGE PER POSE</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Best", x=ps["Pose"], y=ps["Best"],
                          marker_color="#4caf82", opacity=0.85))
    fig3.add_trace(go.Bar(name="Average", x=ps["Pose"], y=ps["Average"],
                          marker_color="#c8a96e", opacity=0.9))
    fig3.add_trace(go.Bar(name="Worst", x=ps["Pose"], y=ps["Worst"],
                          marker_color="#e05c6a", opacity=0.7))
    fig3.update_layout(**PLOTLY_DARK, barmode="group", height=320,
                       yaxis_range=[0, 110],
                       legend=dict(orientation="h", y=1.08, font=dict(color="#c8cce0")),
                       xaxis_tickangle=-20)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Teaching priority table ───────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">TEACHING PRIORITY TABLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Use this to plan your next drill session</div>', unsafe_allow_html=True)

    ps_display = ps.copy()
    ps_display["Priority"] = ps_display["Average"].apply(
        lambda v: "🔴 HIGH" if v < 50 else ("🟡 MEDIUM" if v < 70 else "🟢 LOW")
    )
    ps_display["Spread"] = (ps_display["Best"] - ps_display["Worst"]).round(1)
    ps_display = ps_display[["Pose","Average","Sessions","Best","Worst","Spread","Priority"]]
    ps_display.columns = ["Pose","Avg %","Sessions","Best %","Worst %","Score Spread","Teaching Priority"]
    ps_display["Avg %"] = ps_display["Avg %"].round(1)

    st.dataframe(
        ps_display.style.background_gradient(subset=["Avg %"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True, hide_index=True
    )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════

def _tab_insights():
    dm = DataManager()
    summary    = dm.get_all_students_summary()
    pose_stats = dm.get_pose_statistics()

    if not summary:
        st.info("No data yet. Insights will appear after cadets complete practice sessions.")
        return

    st.markdown('<div class="section-title">COMMAND INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Automated analysis to help you prioritise training time</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    insights = generate_insights(summary, pose_stats)
    for label, text, color in insights:
        st.markdown(insight_html(label, text, color), unsafe_allow_html=True)

    st.markdown("---")

    # ── Cadets below target ───────────────────────────────────────────────
    df = pd.DataFrame(summary)
    below = df[df["Avg_Accuracy"] < 70].sort_values("Avg_Accuracy")
    above = df[df["Avg_Accuracy"] >= 70].sort_values("Avg_Accuracy", ascending=False)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-title" style="font-size:20px;color:#e05c6a;">⚠️ BELOW TARGET</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Cadets averaging under 70% — require intervention</div>', unsafe_allow_html=True)
        if below.empty:
            st.success("All cadets are above the 70% target. 🎉")
        else:
            for _, row in below.iterrows():
                gap = 70 - float(row["Avg_Accuracy"])
                st.markdown(
                    insight_html(
                        "NEEDS INTERVENTION",
                        f'<b>{row["Student_Name"]}</b> &mdash; {row["Avg_Accuracy"]}% avg ({gap:.1f}% below target)',
                        "#e05c6a"
                    ),
                    unsafe_allow_html=True
                )

    with col2:
        st.markdown('<div class="section-title" style="font-size:20px;color:#4caf82;">✅ ABOVE TARGET</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Cadets performing at or above the 70% target</div>', unsafe_allow_html=True)
        if above.empty:
            st.warning("No cadets have reached the 70% target yet.")
        else:
            for _, row in above.iterrows():
                st.markdown(
                    insight_html(
                        "ON TRACK",
                        f'<b>{row["Student_Name"]}</b> &mdash; {row["Avg_Accuracy"]}% avg across {int(row["Total_Sessions"])} sessions',
                        "#4caf82"
                    ),
                    unsafe_allow_html=True
                )

    # ── Recommended drill plan ────────────────────────────────────────────
    if pose_stats:
        st.markdown("---")
        st.markdown('<div class="section-title">📋 RECOMMENDED DRILL PLAN</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Suggested next session based on unit performance gaps</div>', unsafe_allow_html=True)

        ps = pd.DataFrame(pose_stats).T.reset_index()
        ps.columns = ["Pose","Average","Sessions","Best","Worst"]
        ps["Average"] = ps["Average"].astype(float)
        ps_sorted = ps.sort_values("Average")

        plan_items = []
        for _, row in ps_sorted.iterrows():
            if row["Average"] < 50:
                plan_items.append(("🔴 PRIORITY DRILL", f'<b>{row["Pose"]}</b> — Unit avg {row["Average"]:.0f}%. Dedicate 30+ min. Break into individual components.', "#e05c6a"))
            elif row["Average"] < 70:
                plan_items.append(("🟡 REVIEW NEEDED", f'<b>{row["Pose"]}</b> — Unit avg {row["Average"]:.0f}%. 15 min warm-up review recommended.', "#e8a03a"))
            else:
                plan_items.append(("🟢 MAINTENANCE", f'<b>{row["Pose"]}</b> — Unit avg {row["Average"]:.0f}%. Standard 5-min maintenance drill.', "#4caf82"))

        for label, text, color in plan_items:
            st.markdown(insight_html(label, text, color), unsafe_allow_html=True)