import cv2
import time
import uuid
import os
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
import mediapipe as mp

# ============================================
# CONFIG
# ============================================

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

EXCEL_PATH = os.path.join(OUTPUT_DIR, "pose_data.xlsx")

POSES = [
    "Vishraam",
    "Saavdhan",
    "Dahine Mud",
    "Bahine Mud",
    "Pichhe Mud",
    "Salute"
]

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# ============================================
# ANGLE FUNCTION
# ============================================

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def calculate_vertical_angle(point_top, point_bottom):
    """Calculate vertical alignment angle (should be close to 90° for straight posture)"""
    angle = np.arctan2(point_bottom[0] - point_top[0], point_bottom[1] - point_top[1])
    return abs(angle * 180.0 / np.pi)


# ============================================
# FULL BODY CHECK
# ============================================

def full_body_visible(landmarks):
    """Check if full body is visible with good confidence"""
    
    def vis(id, threshold=0.7):
        return landmarks[id].visibility > threshold

    required = [
        mp_pose.PoseLandmark.NOSE.value,
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_ELBOW.value,
        mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        mp_pose.PoseLandmark.LEFT_WRIST.value,
        mp_pose.PoseLandmark.RIGHT_WRIST.value,
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value
    ]

    return all(vis(i) for i in required)


# ============================================
# POSE EVALUATION 
# ============================================

def evaluate_pose(landmarks, pose_name):
    """Evaluate pose with strict criteria"""
    
    tips = []
    score = 100
    deductions = []

    def get(id):
        lm = landmarks[id]
        return [lm.x, lm.y]

    # Get all required landmarks
    nose = get(mp_pose.PoseLandmark.NOSE.value)
    
    shoulder_l = get(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    shoulder_r = get(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
    
    elbow_l = get(mp_pose.PoseLandmark.LEFT_ELBOW.value)
    elbow_r = get(mp_pose.PoseLandmark.RIGHT_ELBOW.value)
    
    wrist_l = get(mp_pose.PoseLandmark.LEFT_WRIST.value)
    wrist_r = get(mp_pose.PoseLandmark.RIGHT_WRIST.value)
    
    hip_l = get(mp_pose.PoseLandmark.LEFT_HIP.value)
    hip_r = get(mp_pose.PoseLandmark.RIGHT_HIP.value)
    
    knee_l = get(mp_pose.PoseLandmark.LEFT_KNEE.value)
    knee_r = get(mp_pose.PoseLandmark.RIGHT_KNEE.value)
    
    ankle_l = get(mp_pose.PoseLandmark.LEFT_ANKLE.value)
    ankle_r = get(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

    # Calculate useful metrics
    shoulder_width = abs(shoulder_l[0] - shoulder_r[0])
    hip_width = abs(hip_l[0] - hip_r[0])
    feet_dist = abs(ankle_l[0] - ankle_r[0])
    
    # Body alignment - vertical straightness
    body_tilt = abs(shoulder_l[0] - hip_l[0])
    
    # Leg straightness
    left_leg_angle = calculate_angle(hip_l, knee_l, ankle_l)
    right_leg_angle = calculate_angle(hip_r, knee_r, ankle_r)

    # ================= SAAVDHAN (Attention) =================
    if pose_name == "Saavdhan":
        # 1. Feet should be together
        if feet_dist > 0.08:
            deduction = 25
            score -= deduction
            tips.append(f"Feet too far apart (-{deduction})")
        elif feet_dist > 0.05:
            deduction = 15
            score -= deduction
            tips.append(f"Bring heels closer together (-{deduction})")
        
        # 2. Hands should be straight beside thighs
        # Check if wrists are below hips (hands down)
        left_hand_pos = wrist_l[1] - hip_l[1]
        right_hand_pos = wrist_r[1] - hip_r[1]
        
        if left_hand_pos < 0.05 or right_hand_pos < 0.05:
            deduction = 20
            score -= deduction
            tips.append(f"Hands should be straight down beside thighs (-{deduction})")
        
        # Check hand lateral position (should be close to body)
        left_hand_lateral = abs(wrist_l[0] - hip_l[0])
        right_hand_lateral = abs(wrist_r[0] - hip_r[0])
        
        if left_hand_lateral > 0.15 or right_hand_lateral > 0.15:
            deduction = 15
            score -= deduction
            tips.append(f"Keep hands close to body sides (-{deduction})")
        
        # 3. Arms should be straight
        left_arm_angle = calculate_angle(shoulder_l, elbow_l, wrist_l)
        right_arm_angle = calculate_angle(shoulder_r, elbow_r, wrist_r)
        
        if left_arm_angle < 160 or right_arm_angle < 160:
            deduction = 15
            score -= deduction
            tips.append(f"Keep arms straight (-{deduction})")
        
        # 4. Body should be straight
        if body_tilt > 0.06:
            deduction = 20
            score -= deduction
            tips.append(f"Stand straight - body is tilted (-{deduction})")
        
        # 5. Legs should be straight
        if left_leg_angle < 165 or right_leg_angle < 165:
            deduction = 15
            score -= deduction
            tips.append(f"Keep legs straight, don't bend knees (-{deduction})")
        
        # 6. Shoulders should be level
        shoulder_level = abs(shoulder_l[1] - shoulder_r[1])
        if shoulder_level > 0.05:
            deduction = 10
            score -= deduction
            tips.append(f"Keep shoulders level (-{deduction})")

    # ================= VISHRAAM (At Ease) =================
    elif pose_name == "Vishraam":
        ideal_feet_dist = shoulder_width * 1.3
        
        # 1. Feet distance check
        if feet_dist < ideal_feet_dist * 0.7:
            deduction = 25
            score -= deduction
            tips.append(f"Spread feet wider (shoulder-width apart) (-{deduction})")
        elif feet_dist > ideal_feet_dist * 1.6:
            deduction = 20
            score -= deduction
            tips.append(f"Feet too far apart (-{deduction})")
        
        # 2. Hands should be behind back
        # Check if hands are behind the body (x-position should be between hips)
        hands_behind = (
            (wrist_l[0] > hip_l[0] - 0.1 and wrist_l[0] < hip_r[0] + 0.1) and
            (wrist_r[0] > hip_l[0] - 0.1 and wrist_r[0] < hip_r[0] + 0.1)
        )
        
        # Hands should be at hip level or slightly lower
        hands_at_back = (
            abs(wrist_l[1] - hip_l[1]) < 0.15 and 
            abs(wrist_r[1] - hip_r[1]) < 0.15
        )
        
        if not hands_at_back:
            deduction = 30
            score -= deduction
            tips.append(f"Place hands behind back at waist level (-{deduction})")
        
        # 3. Body alignment
        if body_tilt > 0.08:
            deduction = 20
            score -= deduction
            tips.append(f"Keep body straight (-{deduction})")
        
        # 4. Legs should be straight
        if left_leg_angle < 160 or right_leg_angle < 160:
            deduction = 15
            score -= deduction
            tips.append(f"Keep legs straight (-{deduction})")

    # ================= SALUTE =================
    elif pose_name == "Salute":
        # 1. Right arm should be raised with proper angle
        right_arm_angle = calculate_angle(shoulder_r, elbow_r, wrist_r)
        
        # Elbow angle should be around 80-110 degrees for proper salute
        if right_arm_angle < 60 or right_arm_angle > 130:
            deduction = 30
            score -= deduction
            tips.append(f"Incorrect arm angle for salute (-{deduction})")
        
        # 2. Right elbow should be at shoulder height or slightly below
        elbow_height_diff = abs(elbow_r[1] - shoulder_r[1])
        if elbow_height_diff > 0.15:
            deduction = 20
            score -= deduction
            tips.append(f"Raise elbow to shoulder height (-{deduction})")
        
        # 3. Right hand should be near forehead/temple
        hand_to_head = np.sqrt((wrist_r[0] - nose[0])**2 + (wrist_r[1] - nose[1])**2)
        if hand_to_head > 0.15:
            deduction = 25
            score -= deduction
            tips.append(f"Bring hand to forehead/temple (-{deduction})")
        
        # 4. Left hand should be down beside thigh
        left_hand_pos = wrist_l[1] - hip_l[1]
        if left_hand_pos < 0.05:
            deduction = 15
            score -= deduction
            tips.append(f"Keep left hand straight down (-{deduction})")
        
        # 5. Feet should be together (like Saavdhan)
        if feet_dist > 0.08:
            deduction = 15
            score -= deduction
            tips.append(f"Bring feet together (-{deduction})")
        
        # 6. Body should be straight
        if body_tilt > 0.06:
            deduction = 15
            score -= deduction
            tips.append(f"Keep body straight (-{deduction})")

    # ================= DAHINE MUD (Right Turn) =================
    elif pose_name == "Dahine Mud":
        # 1. Check shoulder rotation - should be perpendicular
        # When turned right, right shoulder should be significantly behind left shoulder
        shoulder_depth = shoulder_r[0] - shoulder_l[0]
        
        # For proper right turn, this should be negative and significant
        if shoulder_depth > -0.15:
            deduction = 40
            score -= deduction
            tips.append(f"Turn body 90° to the right (-{deduction})")
        
        # 2. Check hip rotation (should match shoulder rotation)
        hip_depth = hip_r[0] - hip_l[0]
        
        if hip_depth > -0.10:
            deduction = 25
            score -= deduction
            tips.append(f"Rotate hips properly with body (-{deduction})")
        
        # 3. Feet should be together
        if feet_dist > 0.08:
            deduction = 15
            score -= deduction
            tips.append(f"Keep feet together (-{deduction})")
        
        # 4. Body should remain upright
        if abs(shoulder_l[1] - hip_l[1] - (shoulder_r[1] - hip_r[1])) > 0.1:
            deduction = 10
            score -= deduction
            tips.append(f"Keep body upright while turned (-{deduction})")

    # ================= BAHINE MUD (Left Turn) =================
    elif pose_name == "Bahine Mud":
        # 1. Check shoulder rotation - should be perpendicular
        # When turned left, left shoulder should be significantly behind right shoulder
        shoulder_depth = shoulder_l[0] - shoulder_r[0]
        
        # For proper left turn, this should be negative and significant
        if shoulder_depth > -0.15:
            deduction = 40
            score -= deduction
            tips.append(f"Turn body 90° to the left (-{deduction})")
        
        # 2. Check hip rotation
        hip_depth = hip_l[0] - hip_r[0]
        
        if hip_depth > -0.10:
            deduction = 25
            score -= deduction
            tips.append(f"Rotate hips properly with body (-{deduction})")
        
        # 3. Feet should be together
        if feet_dist > 0.08:
            deduction = 15
            score -= deduction
            tips.append(f"Keep feet together (-{deduction})")
        
        # 4. Body should remain upright
        if abs(shoulder_l[1] - hip_l[1] - (shoulder_r[1] - hip_r[1])) > 0.1:
            deduction = 10
            score -= deduction
            tips.append(f"Keep body upright while turned (-{deduction})")

    # ================= PICHHE MUD (About Turn) =================
    elif pose_name == "Pichhe Mud":
        # 1. Check if person is facing away
        # When facing away, shoulders will be very close in x-position
        shoulder_visibility_avg = (
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility +
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility
        ) / 2
        
        # Also check if back is visible (nose should have low visibility)
        nose_visibility = landmarks[mp_pose.PoseLandmark.NOSE.value].visibility
        
        if nose_visibility > 0.3:
            deduction = 50
            score -= deduction
            tips.append(f"Turn completely around (180°) - face away from camera (-{deduction})")
        
        # 2. Shoulders should be close together (facing away)
        if shoulder_width > 0.15:
            deduction = 30
            score -= deduction
            tips.append(f"Complete the turn - shoulders should be aligned (-{deduction})")
        
        # 3. Body should be straight
        if body_tilt > 0.08:
            deduction = 10
            score -= deduction
            tips.append(f"Keep body straight (-{deduction})")

    # Ensure score doesn't go below 0
    score = max(0, score)

    # Add success message if score is high
    if score >= 90:
        tips.insert(0, "Excellent posture! ⭐")
    elif score >= 75:
        tips.insert(0, "Good form, minor improvements needed")
    elif score >= 65:
        tips.insert(0, "Acceptable, but needs practice")
    else:
        tips.insert(0, "Needs significant improvement")

    return score, tips


# ============================================
# HISTORY FUNCTIONS
# ============================================

def get_history(candidate_id):
    """Get candidate's history from Excel"""
    if not os.path.exists(EXCEL_PATH):
        return pd.DataFrame()

    df = pd.read_excel(EXCEL_PATH)
    return df[df["ID"] == candidate_id]


def save_result(row):
    """Save result to Excel"""
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
        # Convert Time column to datetime if it exists
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(EXCEL_PATH, index=False)


# ============================================
# CAMERA + RECORD + ANALYZE
# ============================================

def record_and_analyze(pose_name, candidate_id):
    """Record video and analyze pose in real-time"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    frame_placeholder = st.empty()
    status_placeholder = st.empty()

    ready = False
    scores = []
    tips_final = []

    status_placeholder.info("🔍 Stand back until full body is visible")

    # -------- WAIT FOR FULL BODY --------
    wait_start = time.time()
    
    while time.time() - wait_start < 30:  # 30 second timeout
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.process(rgb)

        if result.pose_landmarks:
            mp_draw.draw_landmarks(
                frame,
                result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            lm = result.pose_landmarks.landmark

            if full_body_visible(lm):
                cv2.putText(frame, "FULL BODY DETECTED - GET READY",
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            3)
                ready = True
            else:
                cv2.putText(frame, "MOVE BACK - FULL BODY NEEDED",
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            3)
        else:
            cv2.putText(frame, "NO PERSON DETECTED",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3)

        frame_placeholder.image(frame, channels="BGR")

        if ready:
            time.sleep(1)  # Give user 1 second to prepare
            break

    if not ready:
        cap.release()
        detector.close()
        st.error("Timeout: Full body not detected. Please try again.")
        return None, None, None

    status_placeholder.success(f"✅ Recording {pose_name} for 5 seconds...")

    # -------- RECORD VIDEO --------
    video_path = os.path.join(
        VIDEO_DIR,
        f"{candidate_id}_{pose_name}_{uuid.uuid4().hex[:8]}.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 20, (1280, 720))

    start = time.time()
    frame_count = 0

    while time.time() - start < 5:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.process(rgb)

        if result.pose_landmarks:
            mp_draw.draw_landmarks(
                frame,
                result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # Evaluate pose
            score, tips = evaluate_pose(
                result.pose_landmarks.landmark,
                pose_name
            )

            scores.append(score)
            tips_final = tips
            frame_count += 1

            # Display current score on frame
            cv2.putText(frame, f"Score: {score}%",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 255, 255),
                        3)
            
            # Display timer
            remaining = 5 - int(time.time() - start)
            cv2.putText(frame, f"Time: {remaining}s",
                        (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 0),
                        2)

        out.write(frame)
        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    out.release()
    detector.close()

    # Calculate average accuracy
    if scores:
        accuracy = int(np.mean(scores))
    else:
        accuracy = 0
        tips_final = ["No pose detected during recording"]

    return accuracy, tips_final, video_path


# ============================================
# STREAMLIT UI
# ============================================

st.set_page_config(page_title="Indian Army Pose Evaluation", page_icon="🎖️", layout="wide")

st.title("🇮🇳 Indian Army Pose Evaluation System")
st.markdown("**Real-time Military Drill Posture Analysis with AI**")

col1, col2 = st.columns([2, 1])

with col1:
    candidate_id = st.text_input("🆔 Candidate ID", placeholder="e.g., IND2024001")
    name = st.text_input("👤 Candidate Name", placeholder="e.g., Rajesh Kumar")
    
with col2:
    pose_name = st.selectbox("🎯 Select Pose", POSES)
    st.markdown(f"""
    **Passing Score:** 65%  
    **Excellent:** 90%+
    """)

st.markdown("---")

if st.button("▶️ Start Evaluation", type="primary", use_container_width=True):
    
    if not candidate_id or not name:
        st.warning("⚠️ Please enter Candidate ID and Name")
        st.stop()

    history = get_history(candidate_id)
    attempt_no = len(history) + 1

    with st.spinner(f"Initializing camera for {pose_name} evaluation..."):
        result = record_and_analyze(pose_name, candidate_id)
    
    if result[0] is None:
        st.stop()
    
    accuracy, tips, video_path = result

    # Calculate improvement
    previous = history.iloc[-1]["Accuracy"] if not history.empty else None

    if previous is None:
        improvement = "First Attempt"
        improvement_color = "blue"
    else:
        diff = accuracy - previous
        if diff > 0:
            improvement = f"+{diff}% improvement"
            improvement_color = "green"
        elif diff < 0:
            improvement = f"{diff}% decline"
            improvement_color = "red"
        else:
            improvement = "No change"
            improvement_color = "gray"

    # Determine result
    result_status = "PASS ✅" if accuracy >= 65 else "FAIL ❌"
    result_color = "green" if accuracy >= 65 else "red"

    # Save to Excel
    row = {
        "Time": datetime.now(),  # Store as datetime object, not string
        "ID": candidate_id,
        "Name": name,
        "Pose": pose_name,
        "Accuracy": accuracy,
        "Result": "PASS" if accuracy >= 65 else "FAIL",
        "Attempt": attempt_no,
        "Video": video_path
    }

    save_result(row)

    # Display Results
    st.markdown("---")
    st.subheader("📊 Evaluation Results")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Attempt Number", f"#{attempt_no}")
    
    with col2:
        st.metric("Accuracy Score", f"{accuracy}%", 
                  delta=improvement if previous is not None else None)
    
    with col3:
        st.metric("Result", result_status)
    
    with col4:
        if accuracy >= 90:
            grade = "A+ (Excellent)"
        elif accuracy >= 80:
            grade = "A (Very Good)"
        elif accuracy >= 70:
            grade = "B (Good)"
        elif accuracy >= 65:
            grade = "C (Pass)"
        else:
            grade = "F (Fail)"
        st.metric("Grade", grade)

    st.markdown("---")

    # Feedback Section
    st.subheader("💬 Detailed Feedback")

    if accuracy >= 65:
        st.success(f"**PASSED** - Well done! You have successfully completed the {pose_name} pose.")
    else:
        st.error(f"**FAILED** - You need more practice with the {pose_name} pose.")

    st.markdown("**Areas for Improvement:**")
    for i, tip in enumerate(tips, 1):
        if "Excellent" in tip or "⭐" in tip:
            st.success(f"✅ {tip}")
        elif "Good" in tip:
            st.info(f"ℹ️ {tip}")
        else:
            st.warning(f"⚠️ {tip}")

    # Motivational message
    if accuracy >= 90:
        st.balloons()
        st.success("🏆 Outstanding performance! Maintain this standard!")
    elif accuracy >= 65:
        st.info("✅ Keep practicing to achieve excellence!")
    else:
        st.warning("📚 Practice daily and review the feedback. You can do it!")

    st.markdown(f"**Video saved at:** `{video_path}`")

# History Section
st.markdown("---")
if st.checkbox("📜 Show Performance History"):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
        
        if not df.empty:
            # Convert Time column to datetime for proper sorting
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            
            st.dataframe(
                df.sort_values('Time', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Show statistics
            st.subheader("📈 Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Evaluations", len(df))
            with col2:
                pass_rate = (df['Result'] == 'PASS').sum() / len(df) * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
            with col3:
                avg_score = df['Accuracy'].mean()
                st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.info("No history available yet.")
    else:
        st.info("No evaluation history found.")