"""
Student Dashboard — Cadet Training Interface (REDESIGNED)
Military dark aesthetic matching the landing page design system.
Army Drill Evaluation System
"""

import sys, os, cv2, numpy as np, streamlit as st, mediapipe as mp
import time, pandas as pd, plotly.graph_objects as go
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from posture_check.savdhan_check   import check_savdhan
from posture_check.vishram_check   import check_vishram
from posture_check.salute_check    import check_salute
from posture_check.dahine_mud_check import check_dahine_mud
from posture_check.bahine_mud_check import check_bahine_mud
from posture_check.piche_mud_check  import check_pichhe_mud
from data_manager import DataManager

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════

POSE_META = {
    "Savdhan (Attention)":     {"hindi":"सावधान", "icon":"⬆", "color":"#c8a96e", "tag":"Foundation Stance",  "tip":"Keep heels together, toes at 30°, thumbs along trouser seams."},
    "Vishram (Stand at Ease)": {"hindi":"विश्राम", "icon":"↔", "color":"#7eb8c9", "tag":"Rest Position",      "tip":"Left foot 12 inches out, right hand clasps left wrist behind back."},
    "Salute":                  {"hindi":"सैल्यूट","icon":"✋", "color":"#e8916a", "tag":"Honours Gesture",    "tip":"Middle finger to right brow, palm facing out, elbow level with shoulder."},
    "Dahine Mud (Right Turn)": {"hindi":"दाहिने मुड़","icon":"↱","color":"#a78bdb","tag":"Direction Command", "tip":"Pivot 90° right on right heel + left toe simultaneously — no shuffling."},
    "Bahine Mud (Left Turn)":  {"hindi":"बाहिने मुड़","icon":"↰","color":"#6abf8a","tag":"Direction Command", "tip":"Pivot 90° left on left heel + right toe simultaneously."},
    "Pichhe Mud (About Turn)": {"hindi":"पीछे मुड़","icon":"↩","color":"#e87a8a","tag":"Direction Command",  "tip":"Always turn RIGHT 180° on right heel + left toe. Never left. No shuffling."},
}

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Barlow Condensed, sans-serif", color="#c8cce0", size=12),
    xaxis=dict(gridcolor="#1e2130", linecolor="#1e2130", zerolinecolor="#1e2130"),
    yaxis=dict(gridcolor="#1e2130", linecolor="#1e2130", zerolinecolor="#1e2130"),
    margin=dict(l=10, r=10, t=40, b=10),
)

def acc_color(v):
    if v >= 85: return "#4caf82"
    if v >= 70: return "#4a90d9"
    if v >= 50: return "#e8a03a"
    return "#e05c6a"

def acc_label(v):
    if v >= 85: return "EXCELLENT"
    if v >= 70: return "GOOD"
    if v >= 50: return "FAIR"
    return "NEEDS WORK"

def acc_emoji(v):
    if v >= 85: return "🎖"
    if v >= 70: return "👍"
    if v >= 50: return "💪"
    return "📚"


# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════

STUDENT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600;700&family=Barlow:wght@300;400;500;600&display=swap');

:root {
    --dark:#07080d; --dark2:#0e1018; --panel:#12141c; --panel2:#161820;
    --border:#1e2130; --border2:#252838; --gold:#c8a96e; --gold2:#a07840;
    --text:#c8cce0; --muted:#4a4f6a;
}

.stApp { background: var(--dark) !important; font-family: 'Barlow', sans-serif; }
.block-container { padding: 1.5rem 2rem 4rem !important; max-width: 1400px !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.cadet-header {
    background: linear-gradient(135deg,#0e1018 0%,#12141c 100%);
    border: 1px solid var(--border); border-left: 4px solid var(--gold);
    border-radius: 12px; padding: 22px 32px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.cadet-header-eyebrow { font-family:'Barlow Condensed',sans-serif; font-size:11px; font-weight:700; letter-spacing:4px; text-transform:uppercase; color:var(--gold); margin-bottom:4px; }
.cadet-header-title { font-family:'Bebas Neue',sans-serif; font-size:38px; letter-spacing:2px; color:#fff; line-height:1; }
.cadet-header-sub { font-size:13px; color:var(--muted); margin-top:4px; }
.cadet-rank-badge { background:linear-gradient(135deg,var(--gold),#a07840); color:#07080d; font-family:'Barlow Condensed',sans-serif; font-size:11px; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:6px 18px; border-radius:99px; }

.kpi-card { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:20px 16px; text-align:center; position:relative; overflow:hidden; }
.kpi-card::before { content:""; position:absolute; top:0; left:0; right:0; height:3px; background:var(--kpi-color,var(--gold)); }
.kpi-icon { font-size:20px; margin-bottom:8px; }
.kpi-value { font-family:'Bebas Neue',sans-serif; font-size:40px; line-height:1; color:var(--kpi-color,var(--gold)); margin-bottom:4px; }
.kpi-label { font-family:'Barlow Condensed',sans-serif; font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:var(--muted); }
.kpi-delta { font-size:11px; margin-top:5px; color:var(--muted); }

.pose-sel-card { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:16px 18px; transition:all 0.2s; }
.pose-sel-card.active { border-color:var(--sel-color); }
.pose-sel-icon { font-size:24px; margin-bottom:8px; }
.pose-sel-name { font-family:'Bebas Neue',sans-serif; font-size:18px; color:#fff; letter-spacing:1px; }
.pose-sel-hindi { font-size:12px; color:var(--muted); font-style:italic; }
.pose-sel-tag { font-family:'Barlow Condensed',sans-serif; font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--sel-color); margin-top:4px; }

.acc-ring-wrap { background:var(--dark2); border-radius:12px; padding:20px; text-align:center; border:1px solid var(--border); margin-bottom:14px; }
.acc-big { font-family:'Bebas Neue',sans-serif; font-size:72px; line-height:1; margin-bottom:4px; }
.acc-sub { font-family:'Barlow Condensed',sans-serif; font-size:11px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:var(--muted); }
.acc-timer { font-size:16px; color:var(--muted); margin-top:8px; }

.prog-bar-wrap { background:#1e2130; border-radius:99px; height:6px; overflow:hidden; margin:10px 0 16px; }
.prog-bar { height:100%; border-radius:99px; transition:width 0.3s ease; }

.rule-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:8px; margin-bottom:6px; border:1px solid var(--border); background:var(--dark2); font-size:13px; font-weight:500; color:var(--text); }
.rule-item.pass { border-color:rgba(76,175,130,0.4); background:rgba(76,175,130,0.08); color:#6abf8a; }
.rule-item.fail { border-color:rgba(224,92,106,0.4); background:rgba(224,92,106,0.08); color:#e87a8a; }
.rule-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }

.tip-card { background:rgba(200,169,110,0.08); border:1px solid rgba(200,169,110,0.25); border-left:3px solid var(--gold); border-radius:8px; padding:12px 16px; font-size:13px; color:rgba(200,169,110,0.9); line-height:1.55; margin-bottom:14px; }
.tip-label { font-family:'Barlow Condensed',sans-serif; font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:var(--gold); margin-bottom:5px; }

.suggestion-item { display:flex; gap:10px; padding:10px 14px; border-radius:8px; background:rgba(232,160,58,0.07); border:1px solid rgba(232,160,58,0.2); margin-bottom:6px; font-size:13px; color:#e8c07a; line-height:1.5; }
.suggestion-num { font-family:'Bebas Neue',sans-serif; font-size:18px; color:var(--gold); flex-shrink:0; line-height:1; margin-top:1px; }

.section-title { font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:2px; color:#fff; margin-bottom:4px; line-height:1; }
.section-sub { font-size:12px; color:var(--muted); margin-bottom:16px; }

.result-card { border-radius:16px; padding:36px; text-align:center; border:1px solid var(--border2); margin-bottom:20px; }
.result-emoji { font-size:64px; margin-bottom:12px; }
.result-label { font-family:'Bebas Neue',sans-serif; font-size:38px; letter-spacing:2px; color:#fff; margin-bottom:8px; }
.result-score { font-family:'Bebas Neue',sans-serif; font-size:80px; line-height:1; }
.result-sub { font-family:'Barlow Condensed',sans-serif; font-size:14px; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.5); margin-top:6px; }
.pb-badge { display:inline-block; font-family:'Barlow Condensed',sans-serif; font-size:12px; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:6px 18px; border-radius:99px; margin-top:14px; background:rgba(200,169,110,0.15); border:1px solid rgba(200,169,110,0.4); color:var(--gold); }

.breakdown-col { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:22px; }
.breakdown-title { font-family:'Bebas Neue',sans-serif; font-size:18px; letter-spacing:1.5px; margin-bottom:14px; }
.breakdown-item { font-size:13px; padding:9px 0; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:8px; color:var(--text); }
.breakdown-item:last-child { border-bottom:none; }

.insight-card { background:var(--panel2); border:1px solid var(--border); border-radius:10px; padding:16px 20px; margin-bottom:10px; border-left:3px solid var(--ins-color,var(--gold)); }
.insight-label { font-family:'Barlow Condensed',sans-serif; font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:var(--ins-color,var(--gold)); margin-bottom:4px; }
.insight-text { font-size:13px; color:var(--text); line-height:1.5; }

.countdown-wrap { background:var(--dark2); border:1px solid var(--border); border-radius:16px; padding:40px; text-align:center; margin:20px 0; }
.countdown-num { font-family:'Bebas Neue',sans-serif; font-size:120px; color:#e05c6a; line-height:1; text-shadow:0 0 40px rgba(224,92,106,0.4); animation:pulse 1s ease-in-out infinite; }
.countdown-num.go { color:#4caf82; text-shadow:0 0 40px rgba(76,175,130,0.4); }
.countdown-sub { font-family:'Barlow Condensed',sans-serif; font-size:14px; letter-spacing:4px; text-transform:uppercase; color:var(--muted); margin-top:8px; }
@keyframes pulse { 0%,100%{transform:scale(1);opacity:1;} 50%{transform:scale(1.06);opacity:0.7;} }

button[data-baseweb="tab"] { font-family:'Barlow Condensed',sans-serif !important; font-size:13px !important; font-weight:700 !important; letter-spacing:2px !important; text-transform:uppercase !important; color:var(--muted) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:var(--gold) !important; }
[data-testid="stTabs"] [role="tablist"] { border-bottom:1px solid var(--border) !important; gap:6px !important; margin-bottom:24px !important; }

div.stButton > button { background:linear-gradient(135deg,#c8a96e,#a07840) !important; color:#07080d !important; border:none !important; border-radius:8px !important; font-family:'Barlow Condensed',sans-serif !important; font-size:13px !important; font-weight:700 !important; letter-spacing:2px !important; text-transform:uppercase !important; padding:12px 20px !important; transition:all 0.2s !important; width:100% !important; }
div.stButton > button:hover { opacity:0.88 !important; transform:translateY(-1px) !important; }
div.stButton > button[kind="secondary"] { background:var(--panel) !important; color:var(--text) !important; border:1px solid var(--border2) !important; }
div.stButton > button[kind="secondary"]:hover { border-color:var(--gold) !important; color:var(--gold) !important; }

div[data-baseweb="select"] { background:var(--panel) !important; border-color:var(--border2) !important; border-radius:8px !important; }
div[data-baseweb="select"] * { color:var(--text) !important; }
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
hr { border-color:var(--border) !important; margin:24px 0 !important; }
</style>
"""


# ══════════════════════════════════════════════════════════
# MAIN ENTRY
# ══════════════════════════════════════════════════════════

def show_student_dashboard(username, full_name):
    st.markdown(STUDENT_CSS, unsafe_allow_html=True)

    dm    = DataManager()
    stats = dm.get_student_stats(username)

    sessions_count = stats["total_sessions"] if stats else 0
    avg_acc        = stats["avg_accuracy"]   if stats else 0
    rank_label     = acc_label(avg_acc)       if stats else "RECRUIT"

    st.markdown(
        '<div class="cadet-header"><div>'
        '<div class="cadet-header-eyebrow">Cadet Training Interface</div>'
        '<div class="cadet-header-title">DRILL MASTER AI</div>'
        '<div class="cadet-header-sub">Welcome, <b style="color:#c8cce0;">' + full_name + '</b>'
        ' &nbsp;·&nbsp; ' + str(sessions_count) + ' sessions completed</div>'
        '</div><div class="cadet-rank-badge">🎖 ' + rank_label + '</div></div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["🎯  PRACTICE SESSION", "📊  MY ANALYTICS", "🏅  PROGRESS REPORT"])
    with tab1: _tab_practice(username, full_name, dm)
    with tab2: _tab_analytics(username, dm)
    with tab3: _tab_progress(username, full_name, dm)


# ══════════════════════════════════════════════════════════
# TAB 1 — PRACTICE SESSION
# ══════════════════════════════════════════════════════════

def _kpi_html(icon, val, label, color, delta=""):
    return (
        '<div class="kpi-card" style="--kpi-color:' + color + ';">'
        '<div class="kpi-icon">' + icon + '</div>'
        '<div class="kpi-value">' + val + '</div>'
        '<div class="kpi-label">' + label + '</div>'
        + ('<div class="kpi-delta">' + delta + '</div>' if delta else '') +
        '</div>'
    )


def _tab_practice(username, full_name, dm):
    stats = dm.get_student_stats(username)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(_kpi_html("📋", str(stats["total_sessions"]) if stats else "0",   "TOTAL SESSIONS", "#4a90d9", ""), unsafe_allow_html=True)
    with c2: st.markdown(_kpi_html("🎯", f"{stats['avg_accuracy']}%"  if stats else "—",   "AVG ACCURACY",   acc_color(stats["avg_accuracy"]) if stats else "#4a4f6a", acc_label(stats["avg_accuracy"]) if stats else ""), unsafe_allow_html=True)
    with c3: st.markdown(_kpi_html("🏅", f"{stats['max_accuracy']}%"  if stats else "—",   "PERSONAL BEST",  "#4caf82", "all time"), unsafe_allow_html=True)
    with c4: st.markdown(_kpi_html("⚡", str(_streak(username, dm)),                         "DAY STREAK",     "#c8a96e", "consecutive days"), unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">SELECT DRILL COMMAND</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Choose the position you want to practice today</div>', unsafe_allow_html=True)

    if "selected_pose_key" not in st.session_state:
        st.session_state.selected_pose_key = list(POSE_META.keys())[0]

    poses = list(POSE_META.items())
    row1  = st.columns(3, gap="small")
    row2  = st.columns(3, gap="small")

    for idx, (key, meta) in enumerate(poses):
        col    = row1[idx % 3] if idx < 3 else row2[idx % 3]
        active = st.session_state.selected_pose_key == key
        with col:
            aclass = " active" if active else ""
            st.markdown(
                '<div class="pose-sel-card' + aclass + '" style="--sel-color:' + meta["color"] + ';">'
                '<div class="pose-sel-icon">' + meta["icon"] + '</div>'
                '<div class="pose-sel-name">' + key.split("(")[0].strip() + '</div>'
                '<div class="pose-sel-hindi">' + meta["hindi"] + '</div>'
                '<div class="pose-sel-tag">' + meta["tag"] + '</div>'
                '</div>', unsafe_allow_html=True
            )
            if st.button("Select", key="sel_" + key, use_container_width=True):
                st.session_state.selected_pose_key = key
                st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    selected_pose = st.session_state.selected_pose_key
    selected_meta = POSE_META[selected_pose]

    st.markdown(
        '<div class="tip-card"><div class="tip-label">💡 Quick Tip — ' + selected_pose + '</div>'
        + selected_meta["tip"] + '</div>', unsafe_allow_html=True
    )

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button("🎯  Begin Practice Session", use_container_width=True):
            st.session_state.practice_mode = True
            st.rerun()

    # Open dialog when practice_mode is True
    if st.session_state.get("practice_mode", False):
        _practice_dialog(username, full_name, selected_pose, selected_meta, dm)


@st.dialog("🎯  DRILL PRACTICE SESSION", width="large")
def _practice_dialog(username, full_name, pose_option, pose_meta, dm):
    """Full-screen modal: countdown → live camera + HUD → results — all in one place."""

    # ── Dialog CSS tweaks ──────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Make the dialog wider and give it the dark panel look */
    div[data-testid="stDialog"] > div { max-width: 980px !important; }
    div[data-testid="stDialog"] section { background: #12141c !important; border-radius: 16px !important; }
    div[data-testid="stDialogHeader"] { border-bottom: 1px solid #1e2130 !important; padding-bottom: 12px !important; }
    div[data-testid="stDialogHeader"] p { font-family: 'Bebas Neue', sans-serif !important; font-size: 22px !important; letter-spacing: 2px !important; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Pose info banner ───────────────────────────────────────────────────
    color = pose_meta["color"]
    st.markdown(
        '<div style="background:' + color + '12;border:1px solid ' + color + '33;border-radius:10px;'
        'padding:12px 20px;display:flex;align-items:center;gap:14px;margin-bottom:16px;">'
        '<span style="font-size:28px;">' + pose_meta["icon"] + '</span>'
        '<div>'
        '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:10px;font-weight:700;'
        'letter-spacing:3px;text-transform:uppercase;color:' + color + ';margin-bottom:2px;">' + pose_meta["tag"] + '</div>'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:22px;letter-spacing:2px;color:#fff;">'
        + pose_option + '</div>'
        '<div style="font-size:12px;color:#4a4f6a;">' + pose_meta["tip"] + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # Placeholders — everything lives inside these, so nothing shifts
    status_ph    = st.empty()   # countdown  →  live feed + HUD
    results_ph   = st.empty()   # results appear here after camera closes

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        status_ph.error("❌ Camera not accessible. Check your camera connection.")
        st.session_state.practice_mode = False
        return

    # ── PHASE 1: Countdown ─────────────────────────────────────────────────
    for i in range(10, 0, -1):
        sub = "STEP IN FRONT OF CAMERA &amp; FIND YOUR MARK" if i > 5 else "GET INTO POSITION — " + pose_option.upper()
        status_ph.markdown(
            '<div class="countdown-wrap">'
            '<div class="countdown-num">' + str(i) + '</div>'
            '<div class="countdown-sub">' + sub + '</div>'
            '</div>', unsafe_allow_html=True
        )
        time.sleep(1)

    status_ph.markdown(
        '<div class="countdown-wrap"><div class="countdown-num go">GO!</div>'
        '<div class="countdown-sub">HOLD THE POSITION — RECORDING NOW</div></div>',
        unsafe_allow_html=True
    )
    time.sleep(1)
    status_ph.empty()

    # ── PHASE 2: Live camera inside status_ph ──────────────────────────────
    mp_pose    = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    accuracy_readings = []
    all_details       = []
    all_suggestions   = []
    start_time        = time.time()
    DURATION          = 10

    checker_map = {
        "Savdhan (Attention)":     check_savdhan,
        "Vishram (Stand at Ease)": check_vishram,
        "Salute":                  check_salute,
        "Dahine Mud (Right Turn)": check_dahine_mud,
        "Bahine Mud (Left Turn)":  check_bahine_mud,
        "Pichhe Mud (About Turn)": check_pichhe_mud,
    }

    with mp_pose.Pose(static_image_mode=False, model_complexity=1,
                      min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
        while True:
            ret, frame = cap.read()
            if not ret: break
            elapsed = time.time() - start_time
            if elapsed > DURATION: break

            frame   = cv2.flip(frame, 1)
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            accuracy = 0; details = {}; suggestions = []

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(200,169,110), thickness=2, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(74,144,217), thickness=2)
                )
                if pose_option in checker_map:
                    frame, accuracy, details, suggestions, _ = checker_map[pose_option](frame, results.pose_landmarks)
                accuracy_readings.append(accuracy)
                if details:     all_details.append(details)
                if suggestions: all_suggestions.extend(suggestions)

            # Render camera + HUD inside the single status_ph placeholder
            with status_ph.container():
                col_cam, col_hud = st.columns([1.3, 1], gap="medium")

                with col_cam:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                             use_container_width=True, caption="📷 LIVE — " + pose_option)

                with col_hud:
                    c = acc_color(accuracy)
                    prog = int((elapsed / DURATION) * 100)

                    # Big accuracy number
                    st.markdown(
                        '<div class="acc-ring-wrap">'
                        '<div class="acc-big" style="color:' + c + ';">' + f'{accuracy:.0f}%' + '</div>'
                        '<div class="acc-sub">LIVE ACCURACY</div>'
                        '<div class="acc-timer">⏱ ' + f'{int(elapsed)} / {DURATION}s' + '</div>'
                        '</div>', unsafe_allow_html=True
                    )
                    # Progress bar
                    st.markdown(
                        '<div class="prog-bar-wrap"><div class="prog-bar" style="width:'
                        + str(prog) + '%;background:' + c + ';"></div></div>', unsafe_allow_html=True
                    )
                    # Rule status
                    st.markdown('<div class="section-title" style="font-size:15px;">RULE STATUS</div>', unsafe_allow_html=True)
                    if details:
                        for rule, passed in details.items():
                            cls   = "pass" if passed else "fail"
                            dot_c = "#4caf82" if passed else "#e05c6a"
                            st.markdown(
                                '<div class="rule-item ' + cls + '">'
                                '<div class="rule-dot" style="background:' + dot_c + ';"></div>'
                                + ("✓ " if passed else "✗ ") + rule + '</div>', unsafe_allow_html=True
                            )
                    else:
                        st.markdown('<div class="rule-item">👤 Step into frame…</div>', unsafe_allow_html=True)

                    # Live corrections
                    if suggestions:
                        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                        st.markdown('<div class="section-title" style="font-size:15px;">CORRECTIONS</div>', unsafe_allow_html=True)
                        for i, s in enumerate(suggestions[:3], 1):
                            st.markdown(
                                '<div class="suggestion-item"><div class="suggestion-num">' + str(i)
                                + '</div><div>' + s + '</div></div>', unsafe_allow_html=True
                            )
                    elif accuracy > 0:
                        st.success("✨ Perfect! Hold this position.")

    cap.release()
    cv2.destroyAllWindows()

    # ── PHASE 3: Results replace camera inside status_ph ──────────────────
    status_ph.empty()

    if not accuracy_readings:
        results_ph.warning("⚠️ No pose detected. Make sure you're fully visible to the camera.")
        st.session_state.practice_mode = False
        return

    final_acc          = float(np.mean(accuracy_readings))
    res_color          = acc_color(final_acc)
    emoji              = acc_emoji(final_acc)
    res_label          = acc_label(final_acc)
    rules_passed, rules_failed = _analyze_rules(all_details)
    unique_suggestions = list(set(all_suggestions))

    prev_stats = dm.get_student_stats(username)
    prev_best  = prev_stats["max_accuracy"] if prev_stats else 0
    is_pb      = final_acc > prev_best

    success = dm.save_practice_record(
        student_id=username, student_name=full_name, pose_type=pose_option,
        accuracy=final_acc, duration=DURATION,
        rules_passed=", ".join(rules_passed) if rules_passed else "None",
        rules_failed=", ".join(rules_failed) if rules_failed else "None"
    )

    # Results rendered in the same space the camera occupied
    with results_ph.container():
        col_score, col_break = st.columns([1, 1.2], gap="medium")

        with col_score:
            st.markdown(
                '<div class="result-card" style="background:' + res_color + '18;border-color:' + res_color + '44;padding:28px 20px;">'
                '<div class="result-emoji">' + emoji + '</div>'
                '<div class="result-label">' + res_label + '</div>'
                '<div class="result-score" style="color:' + res_color + ';">' + f'{final_acc:.1f}%' + '</div>'
                '<div class="result-sub">FINAL ACCURACY SCORE</div>'
                + ('<div class="pb-badge">🏅 NEW PERSONAL BEST!</div>' if is_pb else '') +
                '</div>', unsafe_allow_html=True
            )
            if success:
                st.markdown(
                    '<div style="text-align:center;font-family:Barlow Condensed,sans-serif;'
                    'font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#4a4f6a;margin-top:6px;">'
                    '✓ Saved to training record</div>', unsafe_allow_html=True
                )

        with col_break:
            # What went right
            st.markdown(
                '<div class="breakdown-col" style="margin-bottom:10px;">'
                '<div class="breakdown-title" style="color:#4caf82;font-size:15px;">✅ WHAT WENT RIGHT</div>'
                + ("".join(
                    '<div class="breakdown-item"><span style="color:#4caf82;margin-right:6px;">✓</span>' + r + '</div>'
                    for r in rules_passed)
                   if rules_passed else
                   '<div class="breakdown-item" style="color:var(--muted);">No rules passed consistently</div>')
                + '</div>', unsafe_allow_html=True
            )
            # Needs improvement
            st.markdown(
                '<div class="breakdown-col">'
                '<div class="breakdown-title" style="color:#e05c6a;font-size:15px;">❌ NEEDS IMPROVEMENT</div>'
                + ("".join(
                    '<div class="breakdown-item"><span style="color:#e05c6a;margin-right:6px;">✗</span>' + r + '</div>'
                    for r in rules_failed)
                   if rules_failed else
                   '<div class="breakdown-item" style="color:#4caf82;">All rules passed! 🎉</div>')
                + '</div>', unsafe_allow_html=True
            )

        # Suggestions strip
        if unique_suggestions:
            st.markdown(
                '<div style="margin-top:12px;">'
                '<div class="section-title" style="font-size:15px;margin-bottom:8px;">💡 KEY CORRECTIONS FOR NEXT TIME</div>'
                + "".join(
                    '<div class="suggestion-item" style="margin-bottom:4px;">'
                    '<div class="suggestion-num">' + str(i) + '</div>'
                    '<div>' + s + '</div></div>'
                    for i, s in enumerate(unique_suggestions[:4], 1)
                )
                + '</div>', unsafe_allow_html=True
            )

        # Action buttons
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2, gap="medium")
        with btn1:
            if st.button("🔁  Practice Again", key="dialog_again", use_container_width=True):
                st.session_state.practice_mode = True
                st.rerun()
        with btn2:
            if st.button("✕  Close", key="dialog_close", use_container_width=True):
                st.session_state.practice_mode = False
                st.rerun()

    st.session_state.practice_mode = False


# ══════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════════════════

def _tab_analytics(username, dm):
    stats = dm.get_student_stats(username)
    if not stats or stats["total_sessions"] == 0:
        st.markdown(
            '<div class="insight-card" style="--ins-color:#c8a96e;text-align:center;padding:40px;">'
            '<div style="font-size:40px;margin-bottom:12px;">🎯</div>'
            '<div class="section-title">No Data Yet</div>'
            '<div style="color:var(--muted);font-size:14px;margin-top:8px;">'
            'Complete your first practice session to unlock full analytics.</div></div>', unsafe_allow_html=True
        )
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(_kpi_html("📋", str(stats["total_sessions"]), "SESSIONS",      "#4a90d9", ""), unsafe_allow_html=True)
    with c2: st.markdown(_kpi_html("🎯", f"{stats['avg_accuracy']}%",  "AVG ACCURACY",  acc_color(stats["avg_accuracy"]), acc_label(stats["avg_accuracy"])), unsafe_allow_html=True)
    with c3: st.markdown(_kpi_html("🏅", f"{stats['max_accuracy']}%",  "PERSONAL BEST", "#4caf82", "all time"), unsafe_allow_html=True)
    with c4: st.markdown(_kpi_html("📉", f"{stats['min_accuracy']}%",  "LOWEST SCORE",  "#e05c6a", "all time"), unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    df = pd.DataFrame(stats["recent_sessions"])
    df["Session #"] = range(1, len(df) + 1)
    df["Accuracy"]  = df["Accuracy"].astype(float)

    # Trajectory
    st.markdown('<div class="section-title">ACCURACY TRAJECTORY</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your performance trend — coloured by result quality, with 3-session rolling average</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for y0, y1, c in [(85,100,"#4caf82"),(70,85,"#4a90d9"),(50,70,"#e8a03a"),(0,50,"#e05c6a")]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=c, opacity=0.04, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color="#4a4f6a",
                  annotation_text="Target 70%", annotation_font_color="#4a4f6a")
    if len(df) >= 3:
        df["Rolling"] = df["Accuracy"].rolling(3, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=df["Session #"], y=df["Rolling"], mode="lines",
            line=dict(color="rgba(200,169,110,0.3)", width=1.5, dash="dot"), name="3-session trend", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=df["Session #"], y=df["Accuracy"], mode="lines+markers",
        line=dict(color="#c8a96e", width=2.5),
        marker=dict(size=10, color=df["Accuracy"].apply(acc_color), line=dict(color="#07080d", width=2)),
        name="Accuracy", hovertemplate="<b>Session %{x}</b><br>%{y:.1f}%<extra></extra>"))
    fig.update_layout(**PLOTLY_DARK, height=320, yaxis_range=[0,105],
                      xaxis_title="Session", yaxis_title="Accuracy (%)", showlegend=True,
                      legend=dict(orientation="h", y=1.1, font=dict(color="#c8cce0")))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns([1.2, 1], gap="large")

    pose_df = df.groupby("Pose_Type")["Accuracy"].agg(["mean","count","max","min"]).reset_index()
    pose_df.columns = ["Pose","Avg","Sessions","Best","Worst"]
    pose_df = pose_df.sort_values("Avg", ascending=True)

    with col1:
        st.markdown('<div class="section-title">PERFORMANCE BY POSE</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Average accuracy for each drill command you\'ve practiced</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=pose_df["Avg"], y=pose_df["Pose"], orientation="h",
            marker_color=[acc_color(v) for v in pose_df["Avg"]],
            text=[f'{v:.1f}%' for v in pose_df["Avg"]], textposition="outside", textfont=dict(color="#c8cce0"),
        ))
        fig2.add_vline(x=70, line_dash="dash", line_color="#4a4f6a")
        fig2.update_layout(**PLOTLY_DARK, xaxis_range=[0,110], height=max(260,len(pose_df)*52), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">STRENGTHS &amp; GAPS</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Where to focus your next training session</div>', unsafe_allow_html=True)
        for _, row in pose_df.sort_values("Avg", ascending=False).iterrows():
            color  = "#4caf82" if row["Avg"] >= 70 else ("#e8a03a" if row["Avg"] >= 50 else "#e05c6a")
            status = "STRONG" if row["Avg"] >= 70 else ("FAIR" if row["Avg"] >= 50 else "FOCUS HERE")
            st.markdown(
                '<div class="insight-card" style="--ins-color:' + color + ';">'
                '<div class="insight-label">' + status + '</div>'
                '<div class="insight-text"><b>' + row["Pose"] + '</b> — '
                + f'{row["Avg"]:.1f}% avg ({int(row["Sessions"])} sessions) · Best: {row["Best"]:.0f}%'
                '</div></div>', unsafe_allow_html=True
            )

    if len(pose_df) >= 3:
        st.markdown("---")
        st.markdown('<div class="section-title">SKILL RADAR</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Your accuracy map vs target across all practiced commands</div>', unsafe_allow_html=True)
        theta = list(pose_df["Pose"]) + [pose_df["Pose"].iloc[0]]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=list(pose_df["Avg"])+[pose_df["Avg"].iloc[0]], theta=theta,
            fill="toself", fillcolor="rgba(200,169,110,0.1)", line=dict(color="#c8a96e",width=2), marker=dict(color="#c8a96e",size=7), name="You"))
        fig_r.add_trace(go.Scatterpolar(r=[70]*len(theta), theta=theta,
            fill="toself", fillcolor="rgba(74,144,217,0.05)", line=dict(color="#4a90d9",width=1,dash="dot"), name="Target 70%"))
        fig_r.update_layout(**PLOTLY_DARK,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                       radialaxis=dict(visible=True,range=[0,100],gridcolor="#1e2130",tickfont=dict(color="#4a4f6a",size=10)),
                       angularaxis=dict(gridcolor="#1e2130",tickfont=dict(color="#c8cce0",size=11))),
            height=360, legend=dict(orientation="h",y=-0.1,font=dict(color="#c8cce0")))
        st.plotly_chart(fig_r, use_container_width=True)


# ══════════════════════════════════════════════════════════
# TAB 3 — PROGRESS REPORT
# ══════════════════════════════════════════════════════════

def _tab_progress(username, full_name, dm):
    stats = dm.get_student_stats(username)
    if not stats or stats["total_sessions"] == 0:
        st.markdown(
            '<div class="insight-card" style="--ins-color:#c8a96e;text-align:center;padding:40px;">'
            '<div style="font-size:40px;margin-bottom:12px;">📊</div>'
            '<div class="section-title">No Sessions Yet</div>'
            '<div style="color:var(--muted);font-size:14px;margin-top:8px;">'
            'Start practicing to unlock your progress report.</div></div>', unsafe_allow_html=True
        )
        return

    df = pd.DataFrame(stats["recent_sessions"])
    df["Accuracy"] = df["Accuracy"].astype(float)
    df["Date"]     = pd.to_datetime(df["Date"])

    st.markdown('<div class="section-title">IMPROVEMENT ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">How your performance has evolved over your training career</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if len(df) >= 6:
            diff  = df.tail(3)["Accuracy"].mean() - df.head(3)["Accuracy"].mean()
            sign  = "+" if diff >= 0 else ""
            color = "#4caf82" if diff >= 0 else "#e05c6a"
            st.markdown(_kpi_html("📈", sign + f'{diff:.1f}%', "IMPROVEMENT", color, "first 3 vs last 3"), unsafe_allow_html=True)
        else:
            st.markdown(_kpi_html("📈", "—", "IMPROVEMENT", "#4a4f6a", "need 6+ sessions"), unsafe_allow_html=True)

    with c2:
        consistency = max(0, 100 - df["Accuracy"].std()) if len(df) > 1 else 100
        st.markdown(_kpi_html("🎯", f'{consistency:.0f}%', "CONSISTENCY", acc_color(consistency), "lower variance = better"), unsafe_allow_html=True)

    with c3:
        pose_avg   = df.groupby("Pose_Type")["Accuracy"].mean()
        best_pose  = pose_avg.idxmax() if not pose_avg.empty else "—"
        best_val   = pose_avg.max()     if not pose_avg.empty else 0
        best_short = best_pose.split("(")[0].strip().upper() if best_pose != "—" else "—"
        st.markdown(
            '<div class="kpi-card" style="--kpi-color:#4caf82;">'
            '<div class="kpi-icon">🏆</div>'
            '<div class="kpi-value" style="font-size:22px;">' + best_short + '</div>'
            '<div class="kpi-label">STRONGEST POSE</div>'
            '<div class="kpi-delta">' + f'{best_val:.1f}% avg' + '</div></div>', unsafe_allow_html=True
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">PERSONALISED COACHING NOTES</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">AI-generated recommendations based on your training data</div>', unsafe_allow_html=True)

    for label, text, color in _generate_personal_insights(df, stats):
        st.markdown(
            '<div class="insight-card" style="--ins-color:' + color + ';">'
            '<div class="insight-label">' + label + '</div>'
            '<div class="insight-text">' + text + '</div></div>', unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown('<div class="section-title">FULL TRAINING LOG</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Every session you\'ve completed, colour-coded by accuracy</div>', unsafe_allow_html=True)

    display = df[["Date","Time","Pose_Type","Accuracy","Duration_Seconds"]].copy()
    display["Date"]     = display["Date"].dt.strftime("%Y-%m-%d")
    display["Accuracy"] = display["Accuracy"].round(1)
    display.columns     = ["Date","Time","Pose","Accuracy (%)","Duration (s)"]
    st.dataframe(display.sort_values("Date", ascending=False).style.background_gradient(
        subset=["Accuracy (%)"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-title">SCORE DISTRIBUTION</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">How your sessions spread across performance bands</div>', unsafe_allow_html=True)
        bins       = [0, 50, 70, 85, 100]
        bin_labels = ["Needs Work\n(0-50%)", "Fair\n(50-70%)", "Good\n(70-85%)", "Excellent\n(85%+)"]
        bin_colors = ["#e05c6a","#e8a03a","#4a90d9","#4caf82"]
        counts     = pd.cut(df["Accuracy"], bins=bins, labels=bin_labels).value_counts().reindex(bin_labels).fillna(0)
        fig_d = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color=bin_colors,
            text=counts.values.astype(int), textposition="outside", textfont=dict(color="#c8cce0")))
        fig_d.update_layout(**PLOTLY_DARK, height=280, showlegend=False, yaxis_title="Sessions")
        st.plotly_chart(fig_d, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">PRACTICE MIX</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Which poses you\'ve trained most — aim for balanced coverage</div>', unsafe_allow_html=True)
        pose_counts      = df["Pose_Type"].value_counts()
        pose_colors_list = [POSE_META.get(p, {}).get("color","#c8a96e") for p in pose_counts.index]
        fig_pie = go.Figure(go.Pie(labels=pose_counts.index, values=pose_counts.values,
            marker_colors=pose_colors_list, hole=0.4, textfont=dict(color="#07080d",size=11)))
        fig_pie.update_layout(**PLOTLY_DARK, height=280, legend=dict(font=dict(color="#c8cce0",size=10)))
        st.plotly_chart(fig_pie, use_container_width=True)


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════

def _analyze_rules(all_details):
    passed, failed = [], []
    if not all_details:
        return passed, failed
    rule_counts = {}
    for frame in all_details:
        for rule, ok in frame.items():
            if rule not in rule_counts:
                rule_counts[rule] = {"p":0,"f":0}
            if ok: rule_counts[rule]["p"] += 1
            else:  rule_counts[rule]["f"] += 1
    for rule, c in rule_counts.items():
        (passed if c["p"] > c["f"] else failed).append(rule)
    return passed, failed


def _streak(username, dm):
    try:
        stats = dm.get_student_stats(username)
        if not stats or not stats["recent_sessions"]: return 0
        df    = pd.DataFrame(stats["recent_sessions"])
        days  = sorted(pd.to_datetime(df["Date"]).dt.date.unique(), reverse=True)
        today = datetime.now().date()
        streak = 0
        for i, d in enumerate(days):
            if d == today - timedelta(days=i): streak += 1
            else: break
        return streak
    except Exception:
        return 0


def _generate_personal_insights(df, stats):
    insights = []
    avg = stats["avg_accuracy"]

    if avg >= 85:
        insights.append(("🏆 ELITE PERFORMANCE",
            f"Your average of <b>{avg}%</b> puts you in the top tier. Challenge yourself to maintain this across all six commands.",
            "#c8a96e"))
    elif avg >= 70:
        insights.append(("👍 GOOD STANDING",
            f"You're averaging <b>{avg}%</b> — above the 70% target. Push toward 85% excellence to earn a higher rank.",
            "#4a90d9"))
    elif avg >= 50:
        insights.append(("💪 KEEP PUSHING",
            f"At <b>{avg}%</b> average you're progressing, but still below target. Add one extra session per day.",
            "#e8a03a"))
    else:
        insights.append(("📚 FOCUS REQUIRED",
            f"Your average of <b>{avg}%</b> needs reinforcement. Study the pose guides on the landing page before practicing.",
            "#e05c6a"))

    if len(df) > 0:
        pose_avg = df.groupby("Pose_Type")["Accuracy"].mean()
        if not pose_avg.empty:
            worst_pose = pose_avg.idxmin(); worst_val = pose_avg.min()
            best_pose  = pose_avg.idxmax(); best_val  = pose_avg.max()
            tip = POSE_META.get(worst_pose,{}).get("tip","Review the execution guide.")
            insights.append(("🎯 PRIORITY FOCUS",
                f"<b>{worst_pose}</b> is your weakest at <b>{worst_val:.1f}%</b>. Drill tip: {tip}", "#e05c6a"))
            insights.append(("✅ YOUR STRENGTH",
                f"<b>{best_pose}</b> is your strongest at <b>{best_val:.1f}%</b>. Use this confidence to tackle harder commands.", "#4caf82"))

    std = df["Accuracy"].std() if len(df) > 1 else 0
    if std < 10:
        insights.append(("🔒 HIGHLY CONSISTENT",
            f"Score variance of only <b>{std:.1f}%</b> shows you perform reliably — a hallmark of true discipline.", "#4caf82"))
    elif std > 25:
        insights.append(("⚡ INCONSISTENT RESULTS",
            f"High variance of <b>{std:.1f}%</b> means your performance fluctuates. Focus on repeatable technique over one-off scores.", "#e8a03a"))

    total = stats["total_sessions"]
    if total < 5:
        insights.append(("📅 BUILD VOLUME",
            f"Only <b>{total} sessions</b> so far. Aim for 2–3 sessions daily to build the muscle memory needed for consistent results.", "#4a90d9"))
    elif total >= 20:
        insights.append(("🔥 DEDICATED CADET",
            f"<b>{total} sessions</b> completed — your dedication is clear. Now drill the full rotation of all 6 commands daily.", "#c8a96e"))

    return insights