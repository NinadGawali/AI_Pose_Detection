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
    LEVEL_TOL = 0.04              # Vertical level tolerance
    CENTER_TOL = 0.04             # Mid alignment tolerance
    ARM_BODY_TOL = 0.20           # Relaxed arm-body closeness

    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i):
        return np.array([lm[i].x, lm[i].y])

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

    # ----------- RULES -----------
    score = 0
    details = {}

    details["Feet together"] = (
        ankle_dist_norm < FEET_TOL and
        ankle_level < LEVEL_TOL
    )

    details["Elbows straight"] = (
        left_elbow_ang >= STRAIGHT_MIN and
        right_elbow_ang >= STRAIGHT_MIN
    )

    details["Knees straight"] = (
        left_knee_ang >= STRAIGHT_MIN and
        right_knee_ang >= STRAIGHT_MIN
    )

    details["Arms close to body"] = left_arm_close and right_arm_close

    details["Shoulders level"] = shoulder_level < LEVEL_TOL

    details["Torso vertical"] = spine_angle < ANGLE_TOL

    details["Head centered"] = head_centered

    total = len(details)

    for k in details:
        if details[k]:
            score += 1

    # ----------- SUGGESTIONS -----------
    suggestions = []

    if not details["Feet together"]:
        suggestions.append("Bring your heels together and balance weight equally.")

    if not details["Elbows straight"]:
        suggestions.append("Straighten your arms fully.")

    if not details["Knees straight"]:
        suggestions.append("Lock your knees and stand tall.")

    if not details["Arms close to body"]:
        suggestions.append("Keep your arms naturally close to your thighs.")

    if not details["Shoulders level"]:
        suggestions.append("Level your shoulders and avoid tilting.")

    if not details["Torso vertical"]:
        suggestions.append("Keep your back straight and avoid leaning.")

    if not details["Head centered"]:
        suggestions.append("Keep your head straight and look forward.")

    # ----------- DEBUG TEXT -----------
    h, w, _ = image.shape

    def draw_text(pt, text):
        x = int(pt[0] * w)
        y = int(pt[1] * h)
        cv2.putText(image, text, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    draw_text(LE, f"E:{left_elbow_ang:.1f}")
    draw_text(RE, f"E:{right_elbow_ang:.1f}")
    draw_text(LK, f"K:{left_knee_ang:.1f}")
    draw_text(RK, f"K:{right_knee_ang:.1f}")

    return image, (score / total) * 100, details, suggestions, {
        "ankle_norm": ankle_dist_norm,
        "left_elbow": left_elbow_ang,
        "right_elbow": right_elbow_ang,
        "left_knee": left_knee_ang,
        "right_knee": right_knee_ang,
        "spine_angle": spine_angle
    }



