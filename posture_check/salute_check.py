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

    # 7️⃣ Feet together (Salute must be from Savdhan)
    ankle_distance = abs(LA[0] - RA[0]) / shoulder_width
    feet_together = ankle_distance < 0.3

    # ====================================================
    #                      SCORING
    # ====================================================

    details = {}
    total = 7
    score = 0

    details["Wrist near eyebrow"] = wrist_near_eye
    details["Wrist lifted"] = wrist_lifted
    details["Elbow raised"] = elbow_raised
    details["Left arm straight"] = left_arm_straight
    details["Body erect"] = body_erect
    details["Forearm lifted"] = forearm_lifted
    details["Feet together"] = feet_together

    for k in details:
        if details[k]:
            score += 1

    # ====================================================
    #                   SUGGESTIONS
    # ====================================================

    suggestions = []

    if not wrist_near_eye:
        suggestions.append("Align your right hand closer to eyebrow level.")

    if not wrist_lifted:
        suggestions.append("Raise your right wrist slightly.")

    if not elbow_raised:
        suggestions.append("Lift your elbow to proper salute height.")

    if not left_arm_straight:
        suggestions.append("Keep your left arm straight beside your thigh.")

    if not body_erect:
        suggestions.append("Stand upright without leaning.")

    if not forearm_lifted:
        suggestions.append("Ensure your forearm is properly lifted.")

    if not feet_together:
        suggestions.append("Bring your heels together in attention position.")

    return image, (score / total) * 100, details, suggestions, {}
