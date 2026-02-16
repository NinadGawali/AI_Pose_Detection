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

def check_savdhan(image, pose_landmarks):

    # ----------- TOLERANCES -----------
    ANGLE_TOL = 15                # General angle tolerance
    STRAIGHT_MIN = 165            # Acceptable straight joint lower bound
    FEET_TOL = 0.18               # Feet horizontal distance tolerance
    LEVEL_TOL = 0.08              # Vertical level tolerance
    CENTER_TOL = 0.04             # Mid alignment tolerance
    ARM_BODY_TOL = 0.20           # Relaxed arm-body closeness

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
    
    # ----------- LANDMARKS -----------
    LS = P(mp_pose.PoseLandmark.LEFT_SHOULDER)
    RS = P(mp_pose.PoseLandmark.RIGHT_SHOULDER)

    LH = P(mp_pose.PoseLandmark.LEFT_HIP)
    RH = P(mp_pose.PoseLandmark.RIGHT_HIP)

    LE = P(mp_pose.PoseLandmark.LEFT_ELBOW)
    RE = P(mp_pose.PoseLandmark.RIGHT_ELBOW)

    LW = P(mp_pose.PoseLandmark.LEFT_WRIST)
    RW = P(mp_pose.PoseLandmark.RIGHT_WRIST)

    LA = P(mp_pose.PoseLandmark.LEFT_ANKLE)
    RA = P(mp_pose.PoseLandmark.RIGHT_ANKLE)

    LK = P(mp_pose.PoseLandmark.LEFT_KNEE)
    RK = P(mp_pose.PoseLandmark.RIGHT_KNEE)

    NOSE = P(mp_pose.PoseLandmark.NOSE)

    shoulder_width = abs(LS[0] - RS[0])

    # ----------- ANGLES -----------
    left_elbow_ang = angle(LS, LE, LW)
    right_elbow_ang = angle(RS, RE, RW)

    left_knee_ang = angle(LH, LK, LA)
    right_knee_ang = angle(RH, RK, RA)

    # Spine vertical check
    mid_shoulder = (LS + RS) / 2
    mid_hip = (LH + RH) / 2
    vertical_ref = mid_shoulder + np.array([0, 1])
    spine_angle = angle(vertical_ref, mid_shoulder, mid_hip)

    # ----------- DISTANCES -----------
    ankle_dist_norm = abs(LA[0] - RA[0]) / shoulder_width
    ankle_level = abs(LA[1] - RA[1])

    shoulder_level = abs(LS[1] - RS[1])

    mid_shoulder_x = mid_shoulder[0]
    mid_hip_x = mid_hip[0]
    torso_shift = abs(mid_shoulder_x - mid_hip_x)

    # Relaxed arm rule
    left_arm_close = abs(LW[0] - LH[0]) / shoulder_width < ARM_BODY_TOL
    right_arm_close = abs(RW[0] - RH[0]) / shoulder_width < ARM_BODY_TOL

    # Head alignment
    head_centered = abs(NOSE[0] - mid_shoulder_x) < CENTER_TOL

    weights = {
        "Feet Together": 30,      # Foundation of Savdhan
        "Knees Locked": 20,       # Military stiffness
        "Arms Pinned": 15,        # Arms must be at the side seams
        "Elbows Straight": 10,    # No "soft" arms
        "Torso/Shoulders": 15,    # Erect posture
        "Head Alignment": 10      # Looking forward
    }

    feet_together = (ankle_dist_norm < 0.25) and (ankle_level < LEVEL_TOL)
    knees_straight = (left_knee_ang >= STRAIGHT_MIN and right_knee_ang >= STRAIGHT_MIN)
    arms_pinned = (abs(LW[0] - LH[0]) / shoulder_width < 0.25 and 
                   abs(RW[0] - RH[0]) / shoulder_width < 0.25)
    posture_ok = (spine_angle < ANGLE_TOL and shoulder_level < LEVEL_TOL)
    
    checks = {
        "Feet Together": feet_together,
        "Knees Locked": knees_straight,
        "Arms Pinned": arms_pinned,
        "Elbows Straight": (left_elbow_ang >= STRAIGHT_MIN and right_elbow_ang >= STRAIGHT_MIN),
        "Torso/Shoulders": posture_ok,
        "Head Alignment": head_centered
    }

    final_score = 0
    suggestions = []

    for feature, passed in checks.items():
        if passed:
            final_score += weights[feature]
        else:
            # Map specific suggestions
            if feature == "Feet Together":
                suggestions.append("Heels must be touching.")
            elif feature == "Arms Pinned":
                suggestions.append("Pin your arms tightly to your side seams.")
            else:
                suggestions.append(f"Adjust: {feature}")

    # ====================================================
    #           CRITICAL FAILURE PENALTIES
    # ====================================================
    # If the feet are wide apart, the posture is NOT Savdhan. 
    # Cap the score at 40% regardless of how perfect the upper body is.
    if not feet_together and final_score > 40:
        final_score = 40
        suggestions.append("CRITICAL: Feet must touch for Savdhan.")

    # ... [Keep your Debug Text drawing code] ...

    return image, final_score, checks, suggestions, {"status": "OK"}