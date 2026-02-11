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

    ANGLE_TOL = 10
    ELBOW_TARGET = 180
    KNEE_TARGET = 180

    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

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

    ankle_dist_norm = abs(LA[0] - RA[0]) / shoulder_width

    left_elbow_ang = angle(LS, LE, LW)
    right_elbow_ang = angle(RS, RE, RW)

    left_knee_ang = angle(LH, LK, LA)
    right_knee_ang = angle(RH, RK, RA)

    left_wrist_hip_x = abs(LW[0] - LH[0]) / shoulder_width
    right_wrist_hip_x = abs(RW[0] - RH[0]) / shoulder_width

    shoulder_level = abs(LS[1] - RS[1])

    mid_shoulder_x = (LS[0] + RS[0]) / 2
    mid_hip_x = (LH[0] + RH[0]) / 2
    torso_shift = abs(mid_shoulder_x - mid_hip_x)

    score = 0
    total = 6
    details = {}

    details["Feet together"] = ankle_dist_norm < 0.15

    elbow_ok = (abs(left_elbow_ang - ELBOW_TARGET) <= ANGLE_TOL and
                abs(right_elbow_ang - ELBOW_TARGET) <= ANGLE_TOL)

    knee_ok = (abs(left_knee_ang - KNEE_TARGET) <= ANGLE_TOL and
               abs(right_knee_ang - KNEE_TARGET) <= ANGLE_TOL)

    details["Elbows straight"] = elbow_ok
    details["Knees straight"] = knee_ok
    details["Wrists beside thighs"] = left_wrist_hip_x < 0.15 and right_wrist_hip_x < 0.15
    details["Shoulders level"] = shoulder_level < 0.03
    details["Torso centered"] = torso_shift < 0.03

    for k in details:
        if details[k]:
            score += 1

    suggestions = []

    if not details["Feet together"]:
        suggestions.append("Bring your heels closer together.")

    if not details["Elbows straight"]:
        suggestions.append("Straighten your arms and keep them close to your body.")

    if not details["Knees straight"]:
        suggestions.append("Straighten your knees and stand tall.")

    if not details["Wrists beside thighs"]:
        suggestions.append("Keep your hands straight beside your thighs.")

    if not details["Shoulders level"]:
        suggestions.append("Level your shoulders and avoid tilting.")

    if not details["Torso centered"]:
        suggestions.append("Avoid leaning sideways. Keep your body centered.")

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
        "right_knee": right_knee_ang
    }
