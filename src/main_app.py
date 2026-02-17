"""
Main Application
Landing page + Login / Signup system + Dashboard router
Army Drill Evaluation System
"""

import streamlit as st
import sys
import os
import base64
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth_utils import (
    initialize_session,
    login,
    logout,
    is_authenticated,
    get_current_user,
    register,
    check_username_exists,
)

from student_app import show_student_dashboard
from teacher_app import show_teacher_dashboard

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drill Master AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_session()


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ═══════════════════════════════════════════════════════════════════════════
# SHARED STYLES
# ═══════════════════════════════════════════════════════════════════════════

def inject_auth_styles(encoded_img):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;600;700&display=swap');

    .stApp {{
        background: #09090f;
        font-family: 'Barlow', sans-serif;
    }}
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}
    [data-testid="stHeader"] {{ display: none; }}

    /* ── Left image panel ── */
    .left-panel {{
        position: relative;
        height: 100vh;
        background-image: url("data:image/png;base64,{encoded_img}");
        background-size: cover;
        background-position: center top;
        border-radius: 0 24px 24px 0;
        overflow: hidden;
    }}
    .left-panel::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.72) 100%);
    }}
    .left-overlay {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        padding: 40px;
        z-index: 10;
        color: white;
    }}
    .left-overlay .badge {{
        display: inline-block;
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.22);
        color: #fff;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 99px;
        margin-bottom: 16px;
    }}
    .left-overlay h1 {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 46px;
        line-height: 1.05;
        margin: 0 0 10px;
        letter-spacing: 1.5px;
    }}
    .left-overlay p {{
        color: rgba(255,255,255,0.68);
        font-size: 14px;
        font-weight: 300;
        margin: 0;
        line-height: 1.6;
    }}
    .left-overlay .rule {{
        width: 40px; height: 2px;
        background: #c8a96e;
        margin-bottom: 16px;
    }}

    /* ── Form typography ── */
    .form-header {{ margin-bottom: 22px; }}
    .form-header .eyebrow {{
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #c8a96e;
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .form-header h2 {{
        color: #ffffff;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 38px;
        letter-spacing: 1.5px;
        margin: 0 0 5px;
    }}
    .form-header .sub {{
        color: #55556a;
        font-size: 13px;
        margin: 0;
    }}

    /* ── Section label above widgets ── */
    .section-label {{
        color: #55556a;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 600;
        margin: 16px 0 6px;
    }}

    /* ── Radio pills ── */
    div[data-testid="stHorizontalRadio"] label {{
        background: #13131f !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 8px !important;
        padding: 7px 18px !important;
        color: #888 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        margin-right: 8px !important;
    }}
    div[data-testid="stHorizontalRadio"] label:has(input:checked) {{
        background: #1e1a2e !important;
        border-color: #c8a96e !important;
        color: #c8a96e !important;
    }}
    div[data-testid="stHorizontalRadio"] input[type="radio"] {{
        display: none !important;
    }}

    /* ── Input fields ── */
    div[data-baseweb="input"] {{
        background: #13131f !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 10px !important;
        transition: border-color 0.2s !important;
    }}
    div[data-baseweb="input"]:focus-within {{
        border-color: #c8a96e !important;
        box-shadow: 0 0 0 3px rgba(200,169,110,0.12) !important;
    }}
    input {{
        color: #e8e8f0 !important;
        font-size: 14px !important;
        font-family: 'Barlow', sans-serif !important;
    }}
    input::placeholder {{ color: #3a3a50 !important; }}
    .stTextInput label p {{
        color: #55556a !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }}

    /* ── Checkbox ── */
    .stCheckbox label p {{ color: #55556a !important; font-size: 12px !important; }}
    .stCheckbox {{ margin-top: 10px !important; }}

    /* ── Primary button (gold) ── */
    div.stButton > button {{
        width: 100% !important;
        background: linear-gradient(135deg, #c8a96e 0%, #a07840 100%) !important;
        color: #09090f !important;
        border: none !important;
        padding: 14px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
        transition: opacity 0.2s, transform 0.2s !important;
        font-family: 'Barlow', sans-serif !important;
    }}
    div.stButton > button:hover {{
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }}

    /* ── Dot grid ── */
    .dots-grid {{
        position: fixed;
        top: 0; right: 0;
        width: 50vw; height: 100vh;
        background-image: radial-gradient(circle, #2a2a3a 1px, transparent 1px);
        background-size: 28px 28px;
        opacity: 0.32;
        pointer-events: none;
        z-index: 0;
    }}
    section[data-testid="stMain"] > div {{ position: relative; z-index: 1; }}

    /* ── Password strength ── */
    .strength-wrap {{
        height: 4px;
        background: #2a2a3a;
        border-radius: 4px;
        margin: 6px 0 2px;
        overflow: hidden;
    }}
    .strength-bar {{ height: 100%; border-radius: 4px; }}
    .strength-label {{ font-size: 11px; letter-spacing: 1px; margin-bottom: 4px; }}
    </style>
    <div class="dots-grid"></div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════


POSE_DATA = {
    "Savdhan": {
        "hindi": "सावधान",
        "subtitle": "Attention",
        "icon": "⬆",
        "color": "#c8a96e",
        "tag": "Foundation Stance",
        "description": (
            "Savdhan is the foundational position of military drill. Every other "
            "command begins and ends here. It demands complete stillness, perfect "
            "alignment and unwavering composure."
        ),
        "steps": [
            "Heels together, toes pointing outward at 30°",
            "Legs straight, knees slightly braced — not locked stiffly",
            "Body erect, weight evenly distributed on both feet",
            "Arms hanging naturally, thumbs along trouser seams",
            "Chest out, shoulders back and level — neither raised nor drooped",
            "Head erect, chin slightly drawn in, eyes looking straight ahead",
            "Mouth closed, breathing slow and steady",
        ],
        "key_points": ["Heels together", "30° toe angle", "Chin in", "Thumbs on seams"],
        "common_errors": ["Swaying body", "Raised shoulders", "Eyes wandering", "Bent knees"],
    },
    "Vishram": {
        "hindi": "विश्राम",
        "subtitle": "Stand at Ease",
        "icon": "↔",
        "color": "#7eb8c9",
        "tag": "Rest Position",
        "description": (
            "Vishram is the rest position, taken from Savdhan. It provides relief "
            "while maintaining military bearing. The left foot moves out while the "
            "hands clasp behind the back."
        ),
        "steps": [
            "From Savdhan, move left foot 12 inches to the left",
            "Feet should be shoulder-width apart, weight equally distributed",
            "Left foot moves first — on the word 'Vishram'",
            "Hands move simultaneously to the back",
            "Right hand grips left wrist behind the back, just below the waistline",
            "Fingers of right hand wrap around left wrist, thumb pointing down",
            "Body remains erect, head still, eyes to the front",
        ],
        "key_points": ["12-inch step left", "Hands clasped behind", "Body upright", "Head still"],
        "common_errors": ["Step too wide or narrow", "Hands clasped in front", "Slouching body"],
    },
    "Salute": {
        "hindi": "सैल्यूट",
        "subtitle": "Salute",
        "icon": "✋",
        "color": "#e8916a",
        "tag": "Honours Gesture",
        "description": (
            "The salute is the highest mark of respect in military tradition. "
            "It must be crisp, precise and held for the correct duration — "
            "never casual or sloppy."
        ),
        "steps": [
            "From Savdhan, raise the right hand smartly",
            "Upper arm horizontal, forearm at 45° to the upper arm",
            "Palm facing outward and slightly downward",
            "Middle finger touches the right eyebrow (or hat brim if worn)",
            "Fingers together, thumb close to forefinger",
            "Elbow in line with the shoulder — not drooping",
            "Eyes make contact with the officer being saluted",
            "Hold for 2 counts, then bring hand smartly back to the side",
        ],
        "key_points": ["Middle finger to brow", "Palm facing out", "Elbow level", "2-count hold"],
        "common_errors": ["Palm facing inward", "Drooping elbow", "Fingers spread apart", "No eye contact"],
    },
    "Dahine Mud": {
        "hindi": "दाहिने मुड़",
        "subtitle": "Right Turn",
        "icon": "↱",
        "color": "#a78bdb",
        "tag": "Direction Command",
        "description": (
            "Dahine Mud is a 90° turn to the right, executed in two crisp counts. "
            "The pivot is on the right heel and left toe simultaneously, maintaining "
            "body erect throughout."
        ),
        "steps": [
            "From Savdhan, await the command 'Dahine — Mud'",
            "On 'Mud': pivot 90° to the right on the right heel and left toe",
            "Right heel and left toe act as the two pivot points",
            "Body turns as one unit — no bending at the waist",
            "Left foot is brought to the right foot smartly (Count 2)",
            "Finish in Savdhan position, now facing right",
            "Arms remain at the side throughout the movement",
        ],
        "key_points": ["Pivot on heel + toe", "90° turn only", "Two-count move", "End in Savdhan"],
        "common_errors": ["Turning more than 90°", "Stepping before pivoting", "Arms swinging", "Leaning forward"],
    },
    "Bahine Mud": {
        "hindi": "बाहिने मुड़",
        "subtitle": "Left Turn",
        "icon": "↰",
        "color": "#6abf8a",
        "tag": "Direction Command",
        "description": (
            "Bahine Mud is the mirror image of Dahine Mud — a 90° turn to the left "
            "on the left heel and right toe. Equal precision is required on both sides."
        ),
        "steps": [
            "From Savdhan, await the command 'Bahine — Mud'",
            "On 'Mud': pivot 90° to the left on the left heel and right toe",
            "Left heel and right toe act as the two pivot points",
            "Body turns as one unit — shoulders level, head erect",
            "Right foot is brought to the left foot smartly (Count 2)",
            "Finish in Savdhan position, now facing left",
            "Arms remain steady at the side",
        ],
        "key_points": ["Left heel pivot", "Right toe pivot", "90° turn", "End in Savdhan"],
        "common_errors": ["Over-rotating", "Hopping instead of pivoting", "Slouching during turn"],
    },
    "Pichhe Mud": {
        "hindi": "पीछे मुड़",
        "subtitle": "About Turn",
        "icon": "↩",
        "color": "#e87a8a",
        "tag": "Direction Command",
        "description": (
            "Pichhe Mud is a 180° about turn — the most demanding direction command. "
            "It is executed in three counts on the right heel and left toe, turning "
            "to the right."
        ),
        "steps": [
            "From Savdhan, await the command 'Pichhe — Mud'",
            "On 'Mud': turn 180° to the RIGHT (always right, never left)",
            "Pivot on the right heel and left toe simultaneously",
            "Turn must be completed in one smooth movement — no shuffling",
            "Left foot is brought to right foot to complete Savdhan (Count 2)",
            "You are now facing the opposite direction",
            "Maintain erect posture and level shoulders throughout",
        ],
        "key_points": ["Always turn RIGHT", "180° only", "Heel + toe pivot", "No shuffling"],
        "common_errors": ["Turning left", "Multiple small steps", "Incomplete 180°", "Arms flailing"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

def _landing_css(encoded_img: str) -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300&family=Barlow+Condensed:wght@300;400;600;700&display=swap');

    :root {{
        --gold:   #c8a96e;
        --gold2:  #a07840;
        --dark:   #07080d;
        --dark2:  #0e1018;
        --panel:  #12141c;
        --border: #1e2130;
        --text:   #d4d8e8;
        --muted:  #4a4f6a;
    }}

    /* ── Reset ── */
    .stApp {{ background: var(--dark) !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}

    /* ── HERO ── */
    .hero {{
        position: relative;
        width: 100vw;
        height: 100vh;
        margin-left: calc(-50vw + 50%);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .hero-bg {{
        position: absolute;
        inset: 0;
        background-image: url("data:image/png;base64,{encoded_img}");
        background-size: cover;
        background-position: center 30%;
        filter: brightness(0.38) saturate(0.6);
        transform: scale(1.03);
    }}
    .hero-grain {{
        position: absolute;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
        opacity: 0.4;
        pointer-events: none;
    }}
    .hero-vignette {{
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at center, transparent 40%, rgba(7,8,13,0.85) 100%);
    }}
    .hero-bottom-fade {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 200px;
        background: linear-gradient(transparent, var(--dark));
    }}

    /* ── Hero content ── */
    .hero-content {{
        position: relative;
        z-index: 10;
        text-align: center;
        padding: 0 40px;
        animation: heroIn 1.2s cubic-bezier(0.16,1,0.3,1) both;
    }}
    @keyframes heroIn {{
        from {{ opacity:0; transform: translateY(30px); }}
        to   {{ opacity:1; transform: translateY(0); }}
    }}
    .hero-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 24px;
    }}
    .hero-eyebrow::before, .hero-eyebrow::after {{
        content: "";
        width: 30px; height: 1px;
        background: var(--gold);
        opacity: 0.5;
    }}
    .hero-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(52px, 8vw, 110px);
        line-height: 0.92;
        letter-spacing: 3px;
        color: #ffffff;
        margin: 0 0 8px;
        text-shadow: 0 4px 40px rgba(0,0,0,0.6);
    }}
    .hero-title span {{ color: var(--gold); }}
    .hero-sub {{
        font-family: 'Crimson Pro', serif;
        font-style: italic;
        font-size: 22px;
        color: rgba(255,255,255,0.55);
        margin: 16px 0 44px;
        letter-spacing: 0.5px;
    }}
    .hero-cta-row {{
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
    }}
    .hero-btn {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 14px 36px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.25s;
        text-decoration: none;
        border: none;
    }}
    .hero-btn-primary {{
        background: linear-gradient(135deg, var(--gold), var(--gold2));
        color: #07080d;
    }}
    .hero-btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(200,169,110,0.35); }}
    .hero-btn-ghost {{
        background: transparent;
        color: rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .hero-btn-ghost:hover {{ border-color: var(--gold); color: var(--gold); transform: translateY(-2px); }}

    /* ── Scroll hint ── */
    .scroll-hint {{
        position: absolute;
        bottom: 32px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        color: rgba(255,255,255,0.3);
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 10px;
        letter-spacing: 3px;
        text-transform: uppercase;
        animation: bounce 2.5s ease-in-out infinite;
    }}
    .scroll-hint-line {{
        width: 1px;
        height: 40px;
        background: linear-gradient(var(--gold), transparent);
    }}
    @keyframes bounce {{
        0%,100% {{ transform: translateX(-50%) translateY(0); }}
        50%      {{ transform: translateX(-50%) translateY(8px); }}
    }}

    /* ── Stats bar ── */
    .stats-bar {{
        background: var(--panel);
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        padding: 28px 60px;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }}
    .stat-item {{ text-align: center; }}
    .stat-num {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 42px;
        color: var(--gold);
        line-height: 1;
    }}
    .stat-desc {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--muted);
        margin-top: 4px;
    }}
    .stat-divider {{
        width: 1px;
        height: 50px;
        background: var(--border);
    }}

    /* ── Section: Pillars ── */
    .pillars-section {{
        background: var(--dark);
        padding: 90px 60px;
    }}
    .section-header {{
        text-align: center;
        margin-bottom: 60px;
    }}
    .section-tag {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 12px;
    }}
    .section-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 56px;
        letter-spacing: 2px;
        color: #ffffff;
        line-height: 1;
    }}
    .section-desc {{
        font-family: 'Crimson Pro', serif;
        font-size: 18px;
        color: var(--muted);
        margin-top: 12px;
        font-style: italic;
    }}

    /* ── Pose grid ── */
    .pose-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        max-width: 1100px;
        margin: 0 auto;
    }}

    /* ── Pose card ── */
    .pose-card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 32px 28px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
        position: relative;
        overflow: hidden;
    }}
    .pose-card::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, var(--card-color, var(--gold)) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.3s;
        border-radius: 16px;
    }}
    .pose-card:hover {{ transform: translateY(-6px); border-color: var(--card-color, var(--gold)); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }}
    .pose-card:hover::before {{ opacity: 0.06; }}

    .pose-card-icon {{
        font-size: 32px;
        margin-bottom: 16px;
        display: block;
    }}
    .pose-card-tag {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--card-color, var(--gold));
        margin-bottom: 8px;
    }}
    .pose-card-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 28px;
        letter-spacing: 1.5px;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 4px;
    }}
    .pose-card-hindi {{
        font-family: 'Crimson Pro', serif;
        font-style: italic;
        font-size: 15px;
        color: var(--muted);
        margin-bottom: 14px;
    }}
    .pose-card-desc {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 13px;
        color: rgba(212,216,232,0.6);
        line-height: 1.5;
        font-weight: 300;
    }}
    .pose-card-footer {{
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .pose-card-cta {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--card-color, var(--gold));
    }}
    .pose-card-arrow {{
        font-size: 18px;
        color: var(--card-color, var(--gold));
        transition: transform 0.3s;
    }}
    .pose-card:hover .pose-card-arrow {{ transform: translateX(5px); }}

    /* ── CTA section ── */
    .cta-section {{
        background: linear-gradient(135deg, #0e1018 0%, #12141c 100%);
        border-top: 1px solid var(--border);
        padding: 80px 60px;
        text-align: center;
    }}
    .cta-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 52px;
        letter-spacing: 2px;
        color: #ffffff;
        margin-bottom: 12px;
    }}
    .cta-sub {{
        font-family: 'Crimson Pro', serif;
        font-style: italic;
        font-size: 18px;
        color: var(--muted);
        margin-bottom: 36px;
    }}

    /* ── MODAL ── */
    .modal-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(7,8,13,0.92);
        backdrop-filter: blur(12px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        animation: fadeIn 0.2s ease;
    }}
    @keyframes fadeIn {{ from{{opacity:0}} to{{opacity:1}} }}
    .modal-box {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        width: 100%;
        max-width: 860px;
        max-height: 88vh;
        overflow-y: auto;
        animation: slideUp 0.3s cubic-bezier(0.16,1,0.3,1);
        scrollbar-width: thin;
        scrollbar-color: var(--border) transparent;
    }}
    @keyframes slideUp {{ from{{opacity:0;transform:translateY(24px)}} to{{opacity:1;transform:translateY(0)}} }}
    .modal-header {{
        padding: 36px 40px 0;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 20px;
    }}
    .modal-meta {{ flex: 1; }}
    .modal-tag {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .modal-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 52px;
        letter-spacing: 2px;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 4px;
    }}
    .modal-hindi {{
        font-family: 'Crimson Pro', serif;
        font-style: italic;
        font-size: 20px;
        color: var(--muted);
    }}
    .modal-close {{
        background: rgba(255,255,255,0.06);
        border: 1px solid var(--border);
        color: rgba(255,255,255,0.5);
        font-size: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        flex-shrink: 0;
        line-height: 1;
    }}
    .modal-close:hover {{ background: rgba(255,255,255,0.12); color: #fff; }}

    .modal-divider {{
        height: 1px;
        background: var(--border);
        margin: 24px 40px;
    }}
    .modal-body {{ padding: 0 40px 40px; }}
    .modal-desc {{
        font-family: 'Crimson Pro', serif;
        font-size: 18px;
        line-height: 1.7;
        color: rgba(212,216,232,0.75);
        font-style: italic;
        margin-bottom: 32px;
    }}

    /* Steps */
    .modal-section-label {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 16px;
    }}
    .steps-list {{ list-style: none; padding: 0; margin: 0 0 32px; }}
    .step-item {{
        display: flex;
        gap: 16px;
        align-items: flex-start;
        padding: 14px 0;
        border-bottom: 1px solid rgba(30,33,48,0.6);
    }}
    .step-item:last-child {{ border-bottom: none; }}
    .step-num {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 22px;
        line-height: 1;
        flex-shrink: 0;
        width: 28px;
    }}
    .step-text {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 16px;
        font-weight: 400;
        color: var(--text);
        line-height: 1.5;
        padding-top: 2px;
    }}

    /* Key points + errors */
    .modal-chips-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 28px;
    }}
    .chip {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 99px;
    }}
    .chip-good  {{ background: rgba(106,191,138,0.15); color: #6abf8a; border: 1px solid rgba(106,191,138,0.3); }}
    .chip-bad   {{ background: rgba(232,122,138,0.15); color: #e87a8a; border: 1px solid rgba(232,122,138,0.3); }}

    /* Streamlit buttons styling on landing */
    div.stButton > button {{
        background: linear-gradient(135deg, var(--gold, #c8a96e), #a07840) !important;
        color: #07080d !important;
        border: none !important;
        padding: 14px 40px !important;
        border-radius: 6px !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        transition: all 0.25s !important;
        width: 100% !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(200,169,110,0.35) !important;
    }}
    </style>
    """


# ═══════════════════════════════════════════════════════════════════════════
# POSE MODAL  (shown when a card is clicked)
# ═══════════════════════════════════════════════════════════════════════════

def show_pose_modal(pose_key: str):
    """Renders the pose detail page using native Streamlit components."""
    pose  = POSE_DATA[pose_key]
    color = pose["color"]

    # ── Back button at top ───────────────────────────────────────────────
    col_back, col_gap = st.columns([1, 5])
    with col_back:
        if st.button("← Back", key=f"back_{pose_key}", use_container_width=True):
            st.session_state.pop("active_pose", None)
            st.rerun()

    # Build header HTML without nested quotes in f-string (fixes Streamlit raw-text bug)
    _c    = color
    _tag  = pose["tag"]
    _name = pose_key.upper()
    _hin  = pose["hindi"]
    _sub  = pose["subtitle"]
    _desc = pose["description"]

    _h = (
        '<div style="background:' + _c + '18;border:1px solid ' + _c + '44;'
        'border-radius:16px;padding:32px 40px 24px;margin:8px 0 24px;">'

        '<div style="font-family:sans-serif;font-size:11px;font-weight:700;'
        'letter-spacing:4px;text-transform:uppercase;color:' + _c + ';margin-bottom:8px;">'
        + _tag + '</div>'

        '<div style="font-size:52px;font-weight:900;letter-spacing:3px;'
        'color:#ffffff;line-height:1;margin-bottom:4px;">'
        + _name + '</div>'

        '<div style="font-style:italic;font-size:20px;color:#888aaa;margin-bottom:20px;">'
        + _hin + ' &mdash; ' + _sub + '</div>'

        '<div style="font-size:17px;line-height:1.75;'
        'color:rgba(212,216,232,0.78);font-style:italic;">'
        + _desc + '</div>'

        '</div>'
    )
    st.markdown(_h, unsafe_allow_html=True)

    # ── Two-column layout: Steps | Key points + Errors ───────────────────
    left, right = st.columns([1.3, 1], gap="large")

    with left:
        st.markdown(
            '<div style="font-family:sans-serif;font-size:11px;font-weight:700;'
            'letter-spacing:4px;text-transform:uppercase;color:#4a4f6a;margin-bottom:16px;">'
            'Step-by-step execution</div>',
            unsafe_allow_html=True)

        for i, step in enumerate(pose["steps"], 1):
            _step_html = (
                '<div style="display:flex;gap:16px;align-items:flex-start;'
                'padding:13px 0;border-bottom:1px solid #1e2130;">'
                '<span style="font-size:24px;font-weight:900;color:' + color + ';'
                'line-height:1;flex-shrink:0;width:30px;">' + f'{i:02d}' + '</span>'
                '<span style="font-size:16px;color:#d4d8e8;line-height:1.5;padding-top:3px;">'
                + step + '</span></div>'
            )
            st.markdown(_step_html, unsafe_allow_html=True)

    with right:
        # Key checkpoints
        st.markdown(
            '<div style="font-family:sans-serif;font-size:11px;font-weight:700;'
            'letter-spacing:4px;text-transform:uppercase;color:#4a4f6a;margin-bottom:14px;">'
            'Key checkpoints</div>',
            unsafe_allow_html=True)

        for kp in pose["key_points"]:
            st.markdown(
                '<div style="background:rgba(106,191,138,0.12);border:1px solid rgba(106,191,138,0.28);'
                'color:#6abf8a;font-size:13px;font-weight:600;letter-spacing:1px;'
                'text-transform:uppercase;padding:7px 14px;border-radius:99px;'
                'display:inline-block;margin:4px 4px 4px 0;">&#10003; ' + kp + '</div>',
                unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        # Common errors
        st.markdown(
            '<div style="font-family:sans-serif;font-size:11px;font-weight:700;'
            'letter-spacing:4px;text-transform:uppercase;color:#4a4f6a;margin-bottom:14px;">'
            'Common errors to avoid</div>',
            unsafe_allow_html=True)

        for err in pose["common_errors"]:
            st.markdown(
                '<div style="background:rgba(232,122,138,0.12);border:1px solid rgba(232,122,138,0.28);'
                'color:#e87a8a;font-size:13px;font-weight:600;letter-spacing:1px;'
                'text-transform:uppercase;padding:7px 14px;border-radius:99px;'
                'display:inline-block;margin:4px 4px 4px 0;">&#10007; ' + err + '</div>',
                unsafe_allow_html=True)

    # ── Bottom close button ──────────────────────────────────────────────
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✕  Close Guide", key=f"close_{pose_key}", use_container_width=True):
            st.session_state.pop("active_pose", None)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════

def show_landing_page():
    image_path  = os.path.join(os.path.dirname(__file__), "..", "images", "landing_bg.png")
    encoded_img = get_base64_image(image_path)

    # Inject all CSS
    st.markdown(_landing_css(encoded_img), unsafe_allow_html=True)

    # ── If a pose modal is open, show it and stop ────────────────────────
    if st.session_state.get("active_pose"):
        show_pose_modal(st.session_state["active_pose"])
        return

    # ─────────────────────────────────────────────────────────────────────
    # HERO
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
      <div class="hero-bg"></div>
      <div class="hero-grain"></div>
      <div class="hero-vignette"></div>
      <div class="hero-bottom-fade"></div>

      <div class="hero-content">
        <div class="hero-eyebrow">Army Drill Evaluation System</div>
        <div class="hero-title">DRILL<br><span>MASTER</span><br>AI</div>
        <div class="hero-sub">Precision in every move. Excellence in every drill.</div>
      </div>

      <div class="scroll-hint">
        <div class="scroll-hint-line"></div>
        Scroll
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA Buttons ──────────────────────────────────────────────────────
    st.markdown('<div style="background:#07080d; padding: 48px 60px;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        b1, b2 = st.columns(2, gap="large")
        with b1:
            if st.button("🚀  Start Training", use_container_width=True, key="hero_student"):
                st.session_state.page = "login"
                st.session_state.selected_role = "student"
                st.rerun()
        with b2:
            if st.button("🎖  Instructor Portal", use_container_width=True, key="hero_teacher"):
                st.session_state.page = "login"
                st.session_state.selected_role = "teacher"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # STATS BAR
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-num">6</div>
        <div class="stat-desc">Drill Commands</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">AI</div>
        <div class="stat-desc">Pose Analysis</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">RT</div>
        <div class="stat-desc">Real-Time Feedback</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">∞</div>
        <div class="stat-desc">Practice Sessions</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # SIX PILLARS — clickable cards
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="pillars-section">
      <div class="section-header">
        <div class="section-tag">The Six Pillars of Discipline</div>
        <div class="section-title">DRILL COMMANDS</div>
        <div class="section-desc">Click any command to view the complete execution guide</div>
      </div>
    """, unsafe_allow_html=True)

    poses = list(POSE_DATA.items())  # list of (key, data) tuples

    # Row 1
    row1 = st.columns(3, gap="medium")
    for col, (key, pose) in zip(row1, poses[:3]):
        with col:
            st.markdown(f"""
            <div class="pose-card" style="--card-color:{pose['color']};">
              <span class="pose-card-icon">{pose['icon']}</span>
              <div class="pose-card-tag">{pose['tag']}</div>
              <div class="pose-card-title">{key.upper()}</div>
              <div class="pose-card-hindi">{pose['hindi']} — {pose['subtitle']}</div>
              <div class="pose-card-desc">{pose['description'][:90]}…</div>
              <div class="pose-card-footer">
                <span class="pose-card-cta">View Guide</span>
                <span class="pose-card-arrow">→</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {key}", key=f"card_{key}", use_container_width=True):
                st.session_state["active_pose"] = key
                st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Row 2
    row2 = st.columns(3, gap="medium")
    for col, (key, pose) in zip(row2, poses[3:]):
        with col:
            st.markdown(f"""
            <div class="pose-card" style="--card-color:{pose['color']};">
              <span class="pose-card-icon">{pose['icon']}</span>
              <div class="pose-card-tag">{pose['tag']}</div>
              <div class="pose-card-title">{key.upper()}</div>
              <div class="pose-card-hindi">{pose['hindi']} — {pose['subtitle']}</div>
              <div class="pose-card-desc">{pose['description'][:90]}…</div>
              <div class="pose-card-footer">
                <span class="pose-card-cta">View Guide</span>
                <span class="pose-card-arrow">→</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {key}", key=f"card_{key}", use_container_width=True):
                st.session_state["active_pose"] = key
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close pillars-section

    # ─────────────────────────────────────────────────────────────────────
    # BOTTOM CTA
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cta-section">
      <div class="cta-title">READY TO BEGIN TRAINING?</div>
      <div class="cta-sub">Join your unit and start mastering the six pillars of military precision.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⚡  Enlist Now", use_container_width=True, key="bottom_cta"):
            st.session_state.page = "signup"
            st.session_state.selected_role = "student"
            st.rerun()

    st.markdown('<div style="height:60px; background:#07080d;"></div>', unsafe_allow_html=True)
def show_login_page():
    image_path   = os.path.join(os.path.dirname(__file__), "..", "images", "landing_bg.png")
    encoded_img  = get_base64_image(image_path)
    role_default = st.session_state.get("selected_role", "student")

    inject_auth_styles(encoded_img)

    left_col, right_col = st.columns([1.1, 0.9], gap="small")

    # Role-specific left panel text
    _role = st.session_state.get("selected_role", "student")
    _left_h1 = "Precision In<br>Every Move" if _role == "student" else "Train The<br>Next Generation"
    _left_p  = "Master military drill commands with<br>AI-powered real-time analysis." if _role == "student" else "Monitor your cadets, track progress<br>and elevate unit performance."

    with left_col:
        st.markdown(
            '<div class="left-panel"><div class="left-overlay">'
            '<div class="badge">🎖 Army Drill Evaluation System</div>'
            '<div class="rule"></div>'
            '<h1>' + _left_h1 + '</h1>'
            '<p>' + _left_p + '</p>'
            '</div></div>',
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown("<div style='height:14vh'></div>", unsafe_allow_html=True)

        # Role is already set from landing page button — just display it as a badge
        role = st.session_state.get("selected_role", "student")
        role_label  = "Student" if role == "student" else "Instructor"
        role_icon   = "🎓" if role == "student" else "🎖"
        role_color  = "#c8a96e" if role == "student" else "#7eb8c9"

        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:8px;'
            'background:' + role_color + '18;border:1px solid ' + role_color + '44;'
            'border-radius:99px;padding:6px 16px;margin-bottom:20px;">'
            '<span style="font-size:14px;">' + role_icon + '</span>'
            '<span style="font-size:11px;font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;color:' + role_color + ';">' + role_label + ' Portal</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="form-header">
            <div class="eyebrow">Welcome back</div>
            <h2>Sign In</h2>
            <p class="sub">New here? Use the button below to create an account.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Service ID / Username", placeholder="e.g. CADET123")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            st.checkbox("Remember me")
            submit = st.form_submit_button("→  Sign In")

            if submit:
                if not username or not password:
                    st.error("Please fill in all fields.")
                elif login(username.lower().strip(), password, role):
                    st.success("✓ Access Granted")
                    st.rerun()
                else:
                    st.error("✗ Invalid credentials. Check your username and password.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("✚  Create New Account", key="goto_signup", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# SIGNUP PAGE
# ═══════════════════════════════════════════════════════════════════════════

def _password_strength(pw: str):
    score = 0
    if len(pw) >= 6:                                          score += 1
    if len(pw) >= 10:                                         score += 1
    if any(c.isupper() for c in pw):                          score += 1
    if any(c.isdigit() or not c.isalnum() for c in pw):       score += 1
    labels = ["", "Weak", "Fair", "Strong", "Very Strong"]
    colors = ["#2a2a3a", "#ef4444", "#f59e0b", "#3b82f6", "#22c55e"]
    return score, labels[score], colors[score]


def show_signup_page():
    image_path   = os.path.join(os.path.dirname(__file__), "..", "images", "landing_bg.png")
    encoded_img  = get_base64_image(image_path)
    role_default = st.session_state.get("selected_role", "student")

    inject_auth_styles(encoded_img)

    left_col, right_col = st.columns([1.1, 0.9], gap="small")

    # ── Left panel ──────────────────────────────────────────────────────────
    with left_col:
        st.markdown("""
        <div class="left-panel">
            <div class="left-overlay">
                <div class="badge">🎖 Army Drill Evaluation System</div>
                <div class="rule"></div>
                <h1>Join The<br>Ranks</h1>
                <p>Create your cadet profile and start<br>your precision training today.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right panel ─────────────────────────────────────────────────────────
    with right_col:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-header">
            <div class="eyebrow">Enlist Today</div>
            <h2>Create Account</h2>
            <p class="sub">Already enlisted? Sign in instead.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← Back to Sign In", key="goto_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Role carried from landing page — display as badge only
        role = st.session_state.get("selected_role", "student")
        role_label  = "Student" if role == "student" else "Instructor"
        role_icon   = "🎓" if role == "student" else "🎖"
        role_color  = "#c8a96e" if role == "student" else "#7eb8c9"

        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:8px;'
            'background:' + role_color + '18;border:1px solid ' + role_color + '44;'
            'border-radius:99px;padding:6px 16px;margin-bottom:16px;">'
            '<span style="font-size:14px;">' + role_icon + '</span>'
            '<span style="font-size:11px;font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;color:' + role_color + ';">' + role_label + ' Account</span>'
            '</div>',
            unsafe_allow_html=True
        )

        # ── Form ────────────────────────────────────────────────────────────
        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input(
                "Full Name",
                placeholder="e.g. Arjun Singh",
            )
            username = st.text_input(
                "Service ID / Username",
                placeholder="e.g. CADET123  (no spaces, min 3 chars)",
            )
            col_pw, col_conf = st.columns(2, gap="medium")
            with col_pw:
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Min 6 characters",
                )
            with col_conf:
                confirm_pw = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat password",
                )

            agreed = st.checkbox("I agree to the Terms & Conditions")
            submit = st.form_submit_button("⚡  Create Account")

            # Password strength indicator
            if password:
                score, label, color = _password_strength(password)
                st.markdown(f"""
                <div class="strength-wrap">
                    <div class="strength-bar" style="width:{score*25}%; background:{color};"></div>
                </div>
                <div class="strength-label" style="color:{color};">{label}</div>
                """, unsafe_allow_html=True)

            # ── Validation & submission ──────────────────────────────────────
            if submit:
                errors = []
                if not full_name.strip():
                    errors.append("Full name is required.")
                if not username.strip():
                    errors.append("Username is required.")
                elif len(username.strip()) < 3:
                    errors.append("Username must be at least 3 characters.")
                elif " " in username.strip():
                    errors.append("Username must not contain spaces.")
                if len(password) < 6:
                    errors.append("Password must be at least 6 characters.")
                if password != confirm_pw:
                    errors.append("Passwords do not match.")
                if not agreed:
                    errors.append("You must agree to the Terms & Conditions.")

                if errors:
                    for err in errors:
                        st.error(f"✗ {err}")
                else:
                    # auth_utils.register(username, password, full_name, role)
                    # which calls data_manager.register_user(username, password, full_name, role)
                    success, msg = register(
                        username.strip(),
                        password,
                        full_name.strip(),
                        role,
                    )
                    if success:
                        st.success(f"✓ {msg}  Redirecting to sign in…")
                        time.sleep(1.8)
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(f"✗ {msg}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════

def main():
    if not is_authenticated():
        if "page" not in st.session_state:
            st.session_state.page = "landing"

        if st.session_state.page not in ("landing", "login", "signup"):
            st.session_state.page = "landing"

        page = st.session_state.page
        if page == "landing":
            show_landing_page()
        elif page == "login":
            show_login_page()
        elif page == "signup":
            show_signup_page()

    else:
        user = get_current_user()

        col1, col2, col3 = st.columns([0.5, 3, 1])
        with col1:
            st.markdown("### 🎖")
        with col2:
            st.markdown(
                f"**Army Drill Evaluation**  \n{user['full_name']} • {user['role'].title()}"
            )
        with col3:
            if st.button("Sign Out"):
                logout()
                st.session_state.page = "landing"
                st.rerun()

        st.markdown("---")

        if user["role"] == "student":
            show_student_dashboard(user["username"], user["full_name"])
        elif user["role"] == "teacher":
            show_teacher_dashboard(user["username"], user["full_name"])


if __name__ == "__main__":
    main()
