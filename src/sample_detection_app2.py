import sys
import os
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp
import time

# ===============================
# IMPORT POSTURE CHECK MODULES
# ===============================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from posture_check.savdhan_check import check_savdhan
from posture_check.vishram_check import check_vishram
from posture_check.salute_check import check_salute
from posture_check.dahine_mud_check import check_dahine_mud
from posture_check.bahine_mud_check import check_bahine_mud
from posture_check.piche_mud_check import check_pichhe_mud


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Army Drill Evaluation System",
    layout="wide",
)

# ==========================================================
# GLOBAL STYLES
# ==========================================================

st.markdown("""
<style>

body {
    background-color: #0f172a;
    color: white;
}

.hero {
    position: relative;
    height: 70vh;
    background-image: url("https://images.unsplash.com/photo-1599058917212-d750089bc07e");
    background-size: cover;
    background-position: center;
    border-radius: 15px;
}

.hero-overlay {
    background: rgba(0, 0, 0, 0.65);
    padding: 80px;
    height: 100%;
    border-radius: 15px;
}

.hero-title {
    font-size: 55px;
    font-weight: 700;
    color: white;
}

.hero-sub {
    font-size: 20px;
    color: #d1d5db;
}

.accuracy-box {
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE INIT
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "camera_running" not in st.session_state:
    st.session_state.camera_running = False


# ==========================================================
# NAVBAR
# ==========================================================

col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    st.markdown("## 🇮🇳 Drill Evaluation System")

with col2:
    if st.button("Home"):
        st.session_state.page = "home"

with col3:
    if st.button("Evaluation"):
        st.session_state.page = "evaluation"

with col4:
    if st.button("About"):
        st.session_state.page = "about"

st.markdown("---")


# ==========================================================
# HOME PAGE
# ==========================================================

if st.session_state.page == "home":

    st.markdown("""
    <div class="hero">
        <div class="hero-overlay">
            <div class="hero-title">
                Real-Time Army Drill Validation
            </div>
            <div class="hero-sub">
                AI-Based Pose Evaluation for Army Drill Commands
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    center_col = st.columns([3,2,3])[1]

    with center_col:
        if st.button("🚀 START EVALUATION"):
            st.session_state.page = "evaluation"
            st.rerun()


# ==========================================================
# ABOUT PAGE
# ==========================================================

elif st.session_state.page == "about":

    st.markdown("## About the System")

    st.markdown("""
    This platform evaluates Indian Army drill postures using:

    - MediaPipe Pose Estimation
    - OpenCV Real-Time Processing
    - Proportional Body-Based Rule Engine
    - AI-Assisted Posture Scoring

    Designed for drill validation and training enhancement.
    """)


# ==========================================================
# EVALUATION PAGE
# ==========================================================

elif st.session_state.page == "evaluation":

    st.markdown("## 🎯 Drill Evaluation Mode")

    colA, colB = st.columns([1,2])

    with colA:

        pose_option = st.selectbox(
            "Select Position",
            [
                "Savdhan (Attention)",
                "Vishram (Stand at Ease)",
                "Salute",
                "Dahine Mud (Right Turn)",
                "Bahine Mud (Left Turn)",
                "Pichhe Mud (About Turn)"
            ]
        )

        if st.button("▶ Start Camera"):
            st.session_state.camera_running = True

        if st.button("⏹ Stop Camera"):
            st.session_state.camera_running = False

    frame_placeholder = colB.empty()
    info_placeholder = st.empty()

    if st.session_state.camera_running:

        cap = cv2.VideoCapture(0)

        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils

        pose_hold_start = None
        stable_accuracy = 0

        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        ) as pose:

            while st.session_state.camera_running:

                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)

                accuracy = 0
                details = {}
                suggestions = []

                if results.pose_landmarks:

                    mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )

                    if pose_option == "Savdhan (Attention)":
                        frame, accuracy, details, suggestions, _ = check_savdhan(frame, results.pose_landmarks)

                    elif pose_option == "Vishram (Stand at Ease)":
                        frame, accuracy, details, suggestions, meta = check_vishram(frame, results.pose_landmarks)

                    elif pose_option == "Salute":
                        frame, accuracy, details, suggestions, meta = check_salute(frame, results.pose_landmarks)

                    elif pose_option == "Dahine Mud (Right Turn)":
                        frame, accuracy, details, suggestions, meta = check_dahine_mud(frame, results.pose_landmarks)

                    elif pose_option == "Bahine Mud (Left Turn)":
                        frame, accuracy, details, suggestions, meta = check_bahine_mud(frame, results.pose_landmarks)

                    elif pose_option == "Pichhe Mud (About Turn)":
                        frame, accuracy, details, suggestions, meta = check_pichhe_mud(frame, results.pose_landmarks)

                # ===============================
                # POSE HOLD STABILITY (2 SEC)
                # ===============================

                if accuracy >= 85:
                    if pose_hold_start is None:
                        pose_hold_start = time.time()
                    elif time.time() - pose_hold_start >= 2:
                        stable_accuracy = accuracy
                else:
                    pose_hold_start = None
                    stable_accuracy = 0

                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    use_container_width=True
                )

                # ===============================
                # DISPLAY RESULTS
                # ===============================
                if meta.get("status") == "INCOMPLETE_VIEW":
                    cv2.putText(frame, "STEP BACK: SHOW ENTIRE BODY", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    
                if accuracy >= 85:
                    color = "#22c55e"
                elif accuracy >= 60:
                    color = "#f59e0b"
                else:
                    color = "#ef4444"

                with info_placeholder.container():

                    st.markdown(
                        f"<div class='accuracy-box' style='background-color:{color};'>Live Accuracy: {round(accuracy,2)}%</div>",
                        unsafe_allow_html=True
                    )

                    if stable_accuracy > 0:
                        st.success(f"✔ Pose Held Stable (2 sec) - Final Score: {round(stable_accuracy,2)}%")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### Rule Status")
                        for k in details:
                            status = "✅" if details[k] else "❌"
                            st.write(f"{status} {k}")

                    with col2:
                        st.markdown("### Suggestions")
                        if suggestions:
                            for s in suggestions:
                                st.write(f"• {s}")
                        else:
                            st.success("Perfect Posture!")

                time.sleep(0.01)

        cap.release()
        cv2.destroyAllWindows()
