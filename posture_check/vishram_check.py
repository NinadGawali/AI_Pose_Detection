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

    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    ANGLE_TOL = 15          # Vishram is relaxed
    KNEE_TARGET = 180

    def P(i):
        return np.array([lm[i].x, lm[i].y])

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

    shoulder_width = abs(LS[0] - RS[0])

    ankle_norm = abs(LA[0] - RA[0]) / shoulder_width

    left_elbow = angle(LS, LE, LW)
    right_elbow = angle(RS, RE, RW)

    left_knee = angle(LH, LK, LA)
    right_knee = angle(RH, RK, RA)

    wrist_gap = abs(LW[0] - RW[0]) / shoulder_width

    shoulder_level = abs(LS[1] - RS[1])

    mid_sh_x = (LS[0] + RS[0]) / 2
    mid_hip_x = (LH[0] + RH[0]) / 2
    torso_shift = abs(mid_sh_x - mid_hip_x)

    mid_hip_y = (LH[1] + RH[1]) / 2

    # ---------- rules ----------
    details = {}
    total = 6
    score = 0

    # feet apart ~ shoulder width
    details["Feet apart"] = (ankle_norm >= 0.7 and ankle_norm <= 1.3)

    # elbows bent (hands behind back)
    details["Elbows bent"] = (
        80 - ANGLE_TOL <= left_elbow <= 120 + ANGLE_TOL and
        80 - ANGLE_TOL <= right_elbow <= 120 + ANGLE_TOL
    )

    # knees straight (relaxed)
    details["Knees straight"] = (
        abs(left_knee - KNEE_TARGET) <= 10 and
        abs(right_knee - KNEE_TARGET) <= 10
    )

    # wrists near centre (hands behind back)
    details["Wrists near centre"] = wrist_gap < 0.25

    # shoulders level
    details["Shoulders level"] = shoulder_level < 0.03

    # body centered
    details["Torso centered"] = torso_shift < 0.03

    for k in details:
        if details[k]:
            score += 1

    # ---------- suggestions ----------
    suggestions = []

    if not details["Feet apart"]:
        suggestions.append("Keep your feet about shoulder width apart.")

    if not details["Elbows bent"]:
        suggestions.append("Relax and bend your elbows while keeping hands behind your back.")

    if not details["Knees straight"]:
        suggestions.append("Keep your legs straight and balanced.")

    if not details["Wrists near centre"]:
        suggestions.append("Bring both hands together behind your back.")

    if not details["Shoulders level"]:
        suggestions.append("Relax and level your shoulders.")

    if not details["Torso centered"]:
        suggestions.append("Avoid leaning sideways. Keep your body centred.")

    # ---------- draw angles ----------
    h, w, _ = image.shape

    def draw_text(pt, text):
        x = int(pt[0] * w)
        y = int(pt[1] * h)
        cv2.putText(image, text, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

    draw_text(LE, f"E:{left_elbow:.1f}")
    draw_text(RE, f"E:{right_elbow:.1f}")
    draw_text(LK, f"K:{left_knee:.1f}")
    draw_text(RK, f"K:{right_knee:.1f}")

    return image, (score / total) * 100, details, suggestions, {
        "ankle_norm": ankle_norm,
        "left_elbow": left_elbow,
        "right_elbow": right_elbow,
        "left_knee": left_knee,
        "right_knee": right_knee,
        "wrist_gap": wrist_gap
    }
