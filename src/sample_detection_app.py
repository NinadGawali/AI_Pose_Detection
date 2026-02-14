import sys
import os
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from posture_check.savdhan_check import check_savdhan
from posture_check.vishram_check import check_vishram
from posture_check.salute_check import check_salute


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Army Drill Evaluation System",
    layout="wide",
)

# ==========================================================
# GLOBAL STYLES (TACTICAL THEME)
# ==========================================================

st.markdown("""
<style>

body {
    background-color: #0f172a;
    color: white;
}

.hero {
    position: relative;
    height: 80vh;
    background-image: url("https://images.unsplash.com/photo-1599058917212-d750089bc07e");
    background-size: cover;
    background-position: center;
    border-radius: 15px;
}

.hero-overlay {
    background: rgba(0, 0, 0, 0.6);
    padding: 80px;
    height: 100%;
    border-radius: 15px;
}

.hero-title {
    font-size: 60px;
    font-weight: 700;
    color: white;
}

.hero-sub {
    font-size: 20px;
    color: #d1d5db;
}

.navbar {
    font-size: 18px;
    font-weight: 600;
}

.accuracy-box {
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    color: white;
}

.section {
    padding: 50px 0px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE PAGE CONTROL
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

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
                AI-Powered Pose Analysis for Savdhan, Vishram & Salute Positions
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

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
    This platform is designed to evaluate Indian Army drill postures using 
    real-time computer vision and biomechanical analysis.

    ### Core Technologies
    - MediaPipe Pose Detection
    - OpenCV Real-Time Processing
    - Proportional Body-Based Rule Engine
    - AI-Assisted Posture Accuracy Metrics

    ### Objective
    To assist in:
    - Drill training evaluation
    - Posture correctness monitoring
    - Real-time feedback generation
    - Standardized discipline validation

    ### Designed For
    - Military drill instructors
    - Training academies
    - Defense research projects
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
            ["Savdhan (Attention)", "Vishram (Stand at Ease)", "Salute"]
        )

        start = st.button("▶ Start Camera")
        stop = st.button("⏹ Stop Camera")

    frame_placeholder = colB.empty()
    info_placeholder = st.empty()

    if start:

        cap = cv2.VideoCapture(0)

        for i in range(5,0,-1):
            frame_placeholder.markdown(f"### ⏳ Get Ready... {i}")
            time.sleep(1)

        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils

        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        ) as pose:

            running = True

            while running:

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
                        frame, accuracy, details, suggestions, _ = check_vishram(frame, results.pose_landmarks)

                    elif pose_option == "Salute":
                        frame, accuracy, details, suggestions, _ = check_salute(frame, results.pose_landmarks)

                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    use_container_width=True
                )

                # Accuracy Color
                if accuracy >= 85:
                    color = "#22c55e"
                elif accuracy >= 60:
                    color = "#f59e0b"
                else:
                    color = "#ef4444"

                with info_placeholder.container():

                    st.markdown(
                        f"<div class='accuracy-box' style='background-color:{color};'>Accuracy: {round(accuracy,2)}%</div>",
                        unsafe_allow_html=True
                    )

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

                if stop:
                    running = False

        cap.release()
        cv2.destroyAllWindows()
