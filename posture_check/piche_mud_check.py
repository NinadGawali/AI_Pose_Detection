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

def check_pichhe_mud(image, pose_landmarks):

    ANGLE_TOL = 20
    LEVEL_TOL = 0.05

    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i):
        return np.array([lm[i].x, lm[i].y])

    LS = P(mp_pose.PoseLandmark.LEFT_SHOULDER)
    RS = P(mp_pose.PoseLandmark.RIGHT_SHOULDER)
    LH = P(mp_pose.PoseLandmark.LEFT_HIP)
    RH = P(mp_pose.PoseLandmark.RIGHT_HIP)

    shoulder_width = abs(LS[0] - RS[0])

    nose_visibility = lm[mp_pose.PoseLandmark.NOSE].visibility

    mid_shoulder = (LS + RS) / 2
    mid_hip = (LH + RH) / 2
    vertical_ref = mid_shoulder + np.array([0, 1])
    spine_angle = angle(vertical_ref, mid_shoulder, mid_hip)

    details = {}

    details["Facing away (180°)"] = nose_visibility < 0.3
    details["Shoulders aligned (back view)"] = shoulder_width < 0.12
    details["Body vertical"] = spine_angle < ANGLE_TOL

    score = sum(details.values())
    total = len(details)

    suggestions = [k for k, v in details.items() if not v]

    return image, (score / total) * 100, details, suggestions, {}
