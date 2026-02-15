"""
Student Dashboard
Practice poses with live feedback and accuracy tracking
"""

import sys
import os
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from posture_check.savdhan_check import check_savdhan
from posture_check.vishram_check import check_vishram
from posture_check.salute_check import check_salute
from posture_check.dahine_mud_check import check_dahine_mud
from posture_check.bahine_mud_check import check_bahine_mud
from posture_check.piche_mud_check import check_pichhe_mud
from data_manager import DataManager


def show_student_dashboard(username, full_name):
    """Display student dashboard with practice and stats"""
    
    st.markdown(f"""
    <style>
        /* Dark/Light mode compatible styles */
        .student-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        
        .student-title {{
            font-size: 46px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        .student-subtitle {{
            font-size: 22px;
            color: #e0e7ff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        .practice-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        
        .accuracy-display {{
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            color: white;
            margin: 15px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }}
        
        .analytics-container {{
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            min-height: 500px;
        }}
        
        .rule-status-item {{
            font-size: 18px;
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            font-weight: 500;
            background: rgba(249, 250, 251, 0.8);
        }}
        
        .rule-passed {{
            border-left: 5px solid #22c55e;
            color: #166534;
        }}
        
        .rule-failed {{
            border-left: 5px solid #ef4444;
            color: #991b1b;
        }}
        
        .suggestions-box {{
            background: #fef3c7;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #f59e0b;
            margin: 15px 0;
        }}
        
        .suggestion-item {{
            font-size: 17px;
            padding: 8px 0;
            color: #92400e;
            line-height: 1.6;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }}
        
        .stat-value {{
            font-size: 38px;
            font-weight: 700;
        }}
        
        .stat-label {{
            font-size: 16px;
            opacity: 0.95;
            margin-top: 8px;
        }}
        
        .countdown {{
            font-size: 100px;
            font-weight: 700;
            text-align: center;
            color: #ef4444;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.1); }}
        }}
        
        
        .stat-value {{
            font-size: 38px;
            font-weight: 700;
        }}
        
        .stat-label {{
            font-size: 16px;
            opacity: 0.95;
            margin-top: 8px;
        }}
        
        .countdown {{
            font-size: 100px;
            font-weight: 700;
            text-align: center;
            color: #ef4444;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.1); }}
        }}
        
        .section-header {{
            font-size: 22px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="student-header">
        <div class="student-title">🎯 Student Practice Portal</div>
        <div class="student-subtitle">Welcome, {full_name}!</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'practice_mode' not in st.session_state:
        st.session_state.practice_mode = False
    if 'show_stats' not in st.session_state:
        st.session_state.show_stats = False
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["🏋️ Practice", "📊 My Statistics"])
    
    with tab1:
        show_practice_section(username, full_name)
    
    with tab2:
        show_student_stats(username)


def show_practice_section(username, full_name):
    """Practice section with pose selection and live feedback"""
    
    st.markdown("### Select a Pose to Practice")
    
    # Pose selection with better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pose_option = st.selectbox(
            "Choose Drill Position",
            [
                "Savdhan (Attention)",
                "Vishram (Stand at Ease)",
                "Salute",
                "Dahine Mud (Right Turn)",
                "Bahine Mud (Left Turn)",
                "Pichhe Mud (About Turn)"
            ],
            key="pose_select"
        )
    
    with col2:
        st.markdown("### ")
        if st.button("🚀 Start Practice", use_container_width=True, type="primary"):
            st.session_state.practice_mode = True
            st.rerun()
    
    # Practice mode
    if st.session_state.practice_mode:
        run_practice_session(username, full_name, pose_option)


def run_practice_session(username, full_name, pose_option):
    """Run a practice session with countdown and accuracy tracking"""
    
    st.markdown("---")
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        stop_button = st.button("⏹ Stop Practice", use_container_width=True, type="secondary")
    
    if stop_button:
        st.session_state.practice_mode = False
        st.rerun()
    
    # Placeholders
    countdown_placeholder = st.empty()
    frame_placeholder = st.empty()
    info_placeholder = st.empty()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Could not access camera. Please check your camera connection.")
        st.session_state.practice_mode = False
        return
    
    # Countdown - increased to 5 seconds
    for i in range(5, 0, -1):
        countdown_placeholder.markdown(
            f"<div class='countdown'>Get Ready... {i}</div>",
            unsafe_allow_html=True
        )
        time.sleep(1)
    
    countdown_placeholder.markdown(
        "<div class='countdown' style='color: #22c55e;'>GO!</div>",
        unsafe_allow_html=True
    )
    time.sleep(0.5)
    countdown_placeholder.empty()
    
    # MediaPipe setup
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # Tracking variables
    accuracy_readings = []
    all_details = []
    all_suggestions = []
    start_time = time.time()
    recording_duration = 5  # Increased to 5 seconds
    
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as pose:
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            elapsed_time = time.time() - start_time
            
            # Stop after recording duration or if stop button pressed
            if elapsed_time > recording_duration:
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
                
                # Check pose based on selection
                if pose_option == "Savdhan (Attention)":
                    frame, accuracy, details, suggestions, _ = check_savdhan(frame, results.pose_landmarks)
                
                elif pose_option == "Vishram (Stand at Ease)":
                    frame, accuracy, details, suggestions, _ = check_vishram(frame, results.pose_landmarks)
                
                elif pose_option == "Salute":
                    frame, accuracy, details, suggestions, _ = check_salute(frame, results.pose_landmarks)
                
                elif pose_option == "Dahine Mud (Right Turn)":
                    frame, accuracy, details, suggestions, _ = check_dahine_mud(frame, results.pose_landmarks)
                
                elif pose_option == "Bahine Mud (Left Turn)":
                    frame, accuracy, details, suggestions, _ = check_bahine_mud(frame, results.pose_landmarks)
                
                elif pose_option == "Pichhe Mud (About Turn)":
                    frame, accuracy, details, suggestions, _ = check_pichhe_mud(frame, results.pose_landmarks)
                
                accuracy_readings.append(accuracy)
                if details:
                    all_details.append(details)
                if suggestions:
                    all_suggestions.extend(suggestions)
            
            # Create two-column layout: Video on left, Analytics on right
            col_video, col_analytics = st.columns([1.2, 1])
            
            # Left column: Video feed
            with col_video:
                frame_placeholder.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    use_container_width=True,
                    caption="Live Camera Feed"
                )
            
            # Right column: Analytics
            with col_analytics:
                with info_placeholder.container():
                    # Accuracy color
                    if accuracy >= 85:
                        color = "#22c55e"
                    elif accuracy >= 60:
                        color = "#f59e0b"
                    else:
                        color = "#ef4444"
                    
                    # Accuracy display
                    st.markdown(
                        f"<div class='accuracy-display' style='background-color:{color};'>"
                        f"{round(accuracy, 1)}%<br>"
                        f"<span style='font-size: 20px;'>⏱️ {int(elapsed_time)}/{recording_duration}s</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("<div class='analytics-container'>", unsafe_allow_html=True)
                    
                    # Rule Status Section
                    st.markdown("<div class='section-header'>✓ Rule Status</div>", unsafe_allow_html=True)
                    
                    if details:
                        for rule_name, passed in details.items():
                            status_emoji = "✅" if passed else "❌"
                            status_class = "rule-passed" if passed else "rule-failed"
                            st.markdown(
                                f"<div class='rule-status-item {status_class}'>"
                                f"{status_emoji} {rule_name}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("📍 Stand in frame to see rule status")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Suggestions Section
                    st.markdown("<div class='section-header'>💡 What You Need to Fix</div>", unsafe_allow_html=True)
                    
                    if suggestions:
                        st.markdown("<div class='suggestions-box'>", unsafe_allow_html=True)
                        for i, suggestion in enumerate(suggestions, 1):
                            st.markdown(
                                f"<div class='suggestion-item'>"
                                f"<strong>{i}.</strong> {suggestion}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        if accuracy > 0:  # Only show if pose is detected
                            st.success("✨ Perfect Posture! Keep it up!")
                        else:
                            st.info("🎯 Get into position to see suggestions")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Calculate final accuracy and compile rule details
    if accuracy_readings:
        final_accuracy = np.mean(accuracy_readings)
        
        # Analyze rule performance from collected data
        rules_passed_list = []
        rules_failed_list = []
        
        if all_details:
            # Get the most common rules from all frames
            rule_counts = {}
            for detail_frame in all_details:
                for rule, passed in detail_frame.items():
                    if rule not in rule_counts:
                        rule_counts[rule] = {'passed': 0, 'failed': 0}
                    if passed:
                        rule_counts[rule]['passed'] += 1
                    else:
                        rule_counts[rule]['failed'] += 1
            
            # Determine which rules mostly passed vs failed
            for rule, counts in rule_counts.items():
                if counts['passed'] > counts['failed']:
                    rules_passed_list.append(rule)
                else:
                    rules_failed_list.append(rule)
        
        rules_passed_str = ", ".join(rules_passed_list) if rules_passed_list else "None"
        rules_failed_str = ", ".join(rules_failed_list) if rules_failed_list else "None"
        
        # Get unique suggestions
        unique_suggestions = list(set(all_suggestions)) if all_suggestions else []
        
        # Save to database with detailed information
        data_manager = DataManager()
        success = data_manager.save_practice_record(
            student_id=username,
            student_name=full_name,
            pose_type=pose_option,
            accuracy=final_accuracy,
            duration=recording_duration,
            rules_passed=rules_passed_str,
            rules_failed=rules_failed_str
        )
        
        # Display results
        frame_placeholder.empty()
        info_placeholder.empty()
        
        if final_accuracy >= 85:
            result_color = "#22c55e"
            result_emoji = "🎉"
            result_message = "Excellent!"
        elif final_accuracy >= 70:
            result_color = "#3b82f6"
            result_emoji = "👍"
            result_message = "Good Job!"
        elif final_accuracy >= 50:
            result_color = "#f59e0b"
            result_emoji = "💪"
            result_message = "Keep Practicing!"
        else:
            result_color = "#ef4444"
            result_emoji = "📚"
            result_message = "Need More Practice"
        
        # Create results display with detailed feedback
        st.markdown(f"""
        <div style='background: {result_color}; padding: 40px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 8px 20px rgba(0,0,0,0.3);'>
            <div style='font-size: 80px;'>{result_emoji}</div>
            <div style='font-size: 42px; font-weight: 700; margin: 20px 0;'>{result_message}</div>
            <div style='font-size: 56px; font-weight: 700;'>{round(final_accuracy, 1)}%</div>
            <div style='font-size: 22px; margin-top: 10px;'>Final Accuracy Score</div>
            <div style='font-size: 18px; margin-top: 20px; opacity: 0.95;'>
                {'✅ Successfully saved to your practice history!' if success else '⚠️ Could not save record'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='background: rgba(34, 197, 94, 0.15); padding: 25px; border-radius: 15px; border-left: 5px solid #22c55e;'>
                <div style='font-size: 24px; font-weight: 700; margin-bottom: 15px; color: #166534;'>
                    ✅ What Went Right
                </div>
            """, unsafe_allow_html=True)
            
            if rules_passed_list:
                for rule in rules_passed_list:
                    st.markdown(f"<div style='font-size: 17px; padding: 8px 0; color: #166534;'>✓ {rule}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size: 16px; color: #6b7280;'>No rules passed consistently</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: rgba(239, 68, 68, 0.15); padding: 25px; border-radius: 15px; border-left: 5px solid #ef4444;'>
                <div style='font-size: 24px; font-weight: 700; margin-bottom: 15px; color: #991b1b;'>
                    ❌ What Needs Improvement
                </div>
            """, unsafe_allow_html=True)
            
            if rules_failed_list:
                for rule in rules_failed_list:
                    st.markdown(f"<div style='font-size: 17px; padding: 8px 0; color: #991b1b;'>✗ {rule}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size: 16px; color: #6b7280;'>All rules passed!</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Show key suggestions
        if unique_suggestions:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: #fef3c7; padding: 25px; border-radius: 15px; border-left: 5px solid #f59e0b;'>
                <div style='font-size: 24px; font-weight: 700; margin-bottom: 15px; color: #92400e;'>
                    💡 Key Suggestions for Next Time
                </div>
            """, unsafe_allow_html=True)
            
            for i, suggestion in enumerate(unique_suggestions[:5], 1):  # Show top 5 suggestions
                st.markdown(
                    f"<div style='font-size: 17px; padding: 8px 0; color: #92400e;'>"
                    f"<strong>{i}.</strong> {suggestion}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.session_state.practice_mode = False
    else:
        info_placeholder.warning("⚠️ No pose detected. Please ensure you're visible to the camera.")
        st.session_state.practice_mode = False


def show_student_stats(username):
    """Display student's personal statistics"""
    
    data_manager = DataManager()
    stats = data_manager.get_student_stats(username)
    
    if not stats:
        st.info("📚 No practice history yet. Start practicing to see your statistics!")
        return
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['total_sessions']}</div>
            <div class='stat-label'>Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['avg_accuracy']}%</div>
            <div class='stat-label'>Average Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['max_accuracy']}%</div>
            <div class='stat-label'>Best Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['min_accuracy']}%</div>
            <div class='stat-label'>Lowest Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent sessions
    st.markdown("### 📅 Recent Practice Sessions")
    
    if stats['recent_sessions']:
        import pandas as pd
        df = pd.DataFrame(stats['recent_sessions'])
        df = df[['Date', 'Time', 'Pose_Type', 'Accuracy', 'Duration_Seconds']]
        df.columns = ['Date', 'Time', 'Pose', 'Accuracy (%)', 'Duration (s)']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent sessions found.")
