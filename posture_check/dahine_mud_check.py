import numpy as np
import mediapipe as mp
import cv2


def angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosang = np.clip(cosang, -1, 1)

    return np.degrees(np.arccos(cosang))

def check_dahine_mud(image, pose_landmarks):
    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i): return np.array([lm[i].x, lm[i].y])
    def V(i): return lm[i].visibility
    def Z(i): return lm[i].z # Depth (Lower is closer to camera)

    # ----------- FULL BODY GATE -----------
    required_landmarks = [
        mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE,
        mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER
    ]
    if any(V(i) < 0.5 for i in required_landmarks):
        return image, 0, {}, ["ERROR: Entire body not visible. Please step back."], {"status": "INCOMPLETE_VIEW"}

    # ----------- LANDMARKS -----------
    LS, RS = P(mp_pose.PoseLandmark.LEFT_SHOULDER), P(mp_pose.PoseLandmark.RIGHT_SHOULDER)
    LH, RH = P(mp_pose.PoseLandmark.LEFT_HIP), P(mp_pose.PoseLandmark.RIGHT_HIP)
    LA, RA = P(mp_pose.PoseLandmark.LEFT_ANKLE), P(mp_pose.PoseLandmark.RIGHT_ANKLE)

    # ----------- REFINED LOGIC -----------
    
    turned_right_correctly = Z(mp_pose.PoseLandmark.LEFT_SHOULDER) < Z(mp_pose.PoseLandmark.RIGHT_SHOULDER) - 0.1

    # 2. THE STACKING CHECK (X-axis)
    # Shoulders should "overlap" horizontally at 90 degrees
    shoulder_x_gap = abs(LS[0] - RS[0])
    is_rotated_x = shoulder_x_gap < 0.10 # Tight threshold

    # 3. FEET ALIGNMENT
    # One foot behind the other from camera perspective
    feet_stacked = abs(LA[0] - RA[0]) < 0.10
    
    # 4. VERTICALITY
    mid_sh_x = (LS[0] + RS[0]) / 2
    mid_hip_x = (LH[0] + RH[0]) / 2
    is_vertical = abs(mid_sh_x - mid_hip_x) < 0.05

    weights = {
        "Turned Right (Direction)": 40,
        "90 Degree Rotation": 30,
        "Feet Alignment": 20,
        "Postural Verticality": 10
    }

    checks = {
        "Turned Right (Direction)": turned_right_correctly,
        "90 Degree Rotation": is_rotated_x,
        "Feet Alignment": feet_stacked,
        "Postural Verticality": is_vertical
    }

    final_score = 0
    suggestions = []
    for feature, passed in checks.items():
        if passed:
            final_score += weights[feature]
        else:
            if feature == "Turned Right (Direction)":
                suggestions.append("Pivot RIGHT (Left shoulder should face camera).")
            elif feature == "90 Degree Rotation":
                suggestions.append("Turn your body fully sideways.")
            else:
                suggestions.append(f"Adjust {feature}")

    # CRITICAL PENALTY: If facing camera, cap the score
    if not turned_right_correctly and final_score > 30:
        final_score = 30

    return image, final_score, checks, suggestions, {"status": "OK"}