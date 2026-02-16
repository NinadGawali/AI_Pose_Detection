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

def check_salute(image, pose_landmarks):

    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i):
        return np.array([lm[i].x, lm[i].y])

    def V(i):
        return lm[i].visibility
    
    required_landmarks = [
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE,
        mp_pose.PoseLandmark.LEFT_HEEL,
        mp_pose.PoseLandmark.RIGHT_HEEL,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER
    ]

    if any(V(i) < 0.5 for i in required_landmarks):
        return image, 0, {}, ["ERROR: Entire body not visible. Please step back to show your feet."], {"status": "INCOMPLETE_VIEW"}
    
    # -------- Landmarks --------
    LS = P(mp_pose.PoseLandmark.LEFT_SHOULDER)
    RS = P(mp_pose.PoseLandmark.RIGHT_SHOULDER)

    LE = P(mp_pose.PoseLandmark.LEFT_ELBOW)
    RE = P(mp_pose.PoseLandmark.RIGHT_ELBOW)

    LW = P(mp_pose.PoseLandmark.LEFT_WRIST)
    RW = P(mp_pose.PoseLandmark.RIGHT_WRIST)

    LH = P(mp_pose.PoseLandmark.LEFT_HIP)
    RH = P(mp_pose.PoseLandmark.RIGHT_HIP)

    LA = P(mp_pose.PoseLandmark.LEFT_ANKLE)
    RA = P(mp_pose.PoseLandmark.RIGHT_ANKLE)

    LK = P(mp_pose.PoseLandmark.LEFT_KNEE)
    RK = P(mp_pose.PoseLandmark.RIGHT_KNEE)
    
    REYE = P(mp_pose.PoseLandmark.RIGHT_EYE)

    # -------- Body Proportions --------
    shoulder_width = abs(LS[0] - RS[0]) + 1e-6
    torso_length = abs(((LS[1] + RS[1]) / 2) - ((LH[1] + RH[1]) / 2)) + 1e-6

    # ====================================================
    #                BODY-AWARE RULES
    # ====================================================

    # 1️⃣ Wrist near eyebrow (tolerant & proportional)
    wrist_eye_vertical = abs(RW[1] - REYE[1]) / torso_length
    wrist_correct_side = RW[0] > RS[0] - 0.25 * shoulder_width

    wrist_near_eye = wrist_eye_vertical < 0.45 and wrist_correct_side

    # 2️⃣ Wrist lifted relative to shoulder
    wrist_lift = (RS[1] - RW[1]) / torso_length
    wrist_lifted = wrist_lift > -0.1

    # 3️⃣ Elbow raised relative to shoulder
    elbow_lift = (RS[1] - RE[1]) / torso_length
    elbow_raised = elbow_lift > -0.1

    # 4️⃣ Left arm straight (hierarchy-based, bulky safe)
    wrist_below_elbow = LW[1] > LE[1]
    elbow_below_shoulder = LE[1] > LS[1]

    horizontal_offset = abs(LW[0] - LS[0]) / shoulder_width

    left_arm_straight = (
        wrist_below_elbow and
        elbow_below_shoulder and
        horizontal_offset < 0.8   # relaxed for bulky bodies
    )

    # 5️⃣ Body erect
    shoulder_level = abs(LS[1] - RS[1]) / torso_length
    mid_sh_x = (LS[0] + RS[0]) / 2
    mid_hip_x = (LH[0] + RH[0]) / 2
    torso_shift = abs(mid_sh_x - mid_hip_x) / shoulder_width

    body_erect = shoulder_level < 0.3 and torso_shift < 0.3

    # 6️⃣ Forearm lifted
    forearm_vertical = abs(RW[1] - RE[1]) / torso_length
    forearm_lifted = forearm_vertical < 0.7

    ankle_gap = abs(LA[0] - RA[0]) / shoulder_width
    heels_together = ankle_gap < 0.30  

    knee_gap = abs(LK[0] - RK[0]) / shoulder_width
    knees_together = knee_gap < 0.30

    left_leg_angle = angle(LH, LK, LA)
    right_leg_angle = angle(RH, RK, RA)
    legs_straight = left_leg_angle > 160 and right_leg_angle > 160

    # 4. Left Arm Pinned (The 'Savdhan' Arm)
    left_arm_pinned = abs(LW[0] - LH[0]) / shoulder_width < 0.2
    legs_together = heels_together and knees_together and legs_straight
    
    # ====================================================
    #                      SCORING
    # ====================================================
    weights = {
        "Heels Together": 15,
        "Knees Together": 15,
        "Legs Straight": 10,
        "Left Arm Pinned": 10,
        "Wrist Positioning": 25,
        "Elbow Height": 15,
        "Body Posture": 10
    }
    # details = {}
    # total = 7
    # score = 0


    checks = {
        "Heels Together": heels_together,
        "Knees Together": knees_together,
        "Legs Straight": legs_straight,
        "Left Arm Pinned": left_arm_pinned,
        "Wrist Positioning": wrist_near_eye,
        "Elbow Height": elbow_raised,
        "Body Posture": body_erect
    }
    final_score = 0
    suggestions = []

    for feature, passed in checks.items():
        if passed:
            final_score += weights[feature]
        else:
            suggestions.append(f"Fix {feature}")

    # CRITICAL PENALTY: If legs are wide apart, cap the score at 50%
    if not heels_together and final_score > 50:
        final_score = 50
        suggestions.append("CRITICAL: Heels must touch for a valid salute.")

    return image, final_score, checks, suggestions, {}