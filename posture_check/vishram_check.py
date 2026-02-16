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

def check_vishram(image, pose_landmarks):

    ANGLE_TOL = 15
    STRAIGHT_MIN = 165
    LEVEL_TOL = 0.05
    WIDTH_MULTIPLIER = 1.2
    WIDTH_TOL = 0.4

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
    
    LS = P(mp_pose.PoseLandmark.LEFT_SHOULDER)
    RS = P(mp_pose.PoseLandmark.RIGHT_SHOULDER)
    LH = P(mp_pose.PoseLandmark.LEFT_HIP)
    RH = P(mp_pose.PoseLandmark.RIGHT_HIP)
    LK = P(mp_pose.PoseLandmark.LEFT_KNEE)
    RK = P(mp_pose.PoseLandmark.RIGHT_KNEE)
    LA = P(mp_pose.PoseLandmark.LEFT_ANKLE)
    RA = P(mp_pose.PoseLandmark.RIGHT_ANKLE)
    LW = P(mp_pose.PoseLandmark.LEFT_WRIST)
    RW = P(mp_pose.PoseLandmark.RIGHT_WRIST)

    shoulder_width = abs(LS[0] - RS[0]) + 1e-6
    feet_dist = abs(LA[0] - RA[0])

    # 1. Feet Width Check (Target: ~12 inches or shoulder width)
    # Ideally, feet_dist should be between 1.0 to 1.3 times shoulder width
    correct_width = 0.9 * shoulder_width < feet_dist < 1.4 * shoulder_width

    # 2. Legs Straight (Knee Angles)
    left_leg_straight = angle(LH, LK, LA) > 165
    right_leg_straight = angle(RH, RK, RA) > 165
    legs_straight = left_leg_straight and right_leg_straight

    # 3. Knee Alignment (Parallel legs)
    knee_dist = abs(LK[0] - RK[0])
    knees_parallel = abs(knee_dist - feet_dist) < (0.2 * shoulder_width)

    left_hand_hidden = V(mp_pose.PoseLandmark.LEFT_WRIST) < 0.5
    right_hand_hidden = V(mp_pose.PoseLandmark.RIGHT_WRIST) < 0.5
    hands_behind = (left_hand_hidden and right_hand_hidden) or (
        (LS[0] < LW[0] < RS[0]) and (LW[1] > LH[1] - 0.05)
    )
    # 5. Torso Alignment
    shoulders_level = abs(LS[1] - RS[1]) < 0.05
    body_upright = abs(((LS[0] + RS[0])/2) - ((LH[0] + RH[0])/2)) < (0.1 * shoulder_width)

    weights = {
        "Feet Width": 30,        # Critical for Vishram
        "Legs Straight": 20,     # No slouching
        "Knee Alignment": 10,    # Legs should be parallel
        "Hands Position": 25,    # Hands locked behind
        "Body Upright": 15       # Shoulders level and spine straight
    }

    checks = {
        "Feet Width": correct_width,
        "Legs Straight": legs_straight,
        "Knee Alignment": knees_parallel,
        "Hands Position": hands_behind,
        "Body Upright": (shoulders_level and body_upright)
    }

    final_score = 0
    suggestions = []

    for feature, passed in checks.items():
        if passed:
            final_score += weights[feature]
        else:
            if feature == "Feet Width":
                msg = "Widen feet" if feet_dist < shoulder_width else "Narrow your stance"
                suggestions.append(msg)
            else:
                suggestions.append(f"Adjust {feature}")

    # CRITICAL PENALTY: If legs are bent, cap the score
    if not legs_straight and final_score > 40:
        final_score = 40
        suggestions.append("CRITICAL: Keep your knees locked/straight.")

    return image, final_score, checks, suggestions, {}