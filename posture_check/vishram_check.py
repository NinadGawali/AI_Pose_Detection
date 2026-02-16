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

    shoulder_width = abs(LS[0] - RS[0])
    feet_dist = abs(LA[0] - RA[0])

    left_knee_ang = angle(LH, LK, LA)
    right_knee_ang = angle(RH, RK, RA)

    mid_shoulder = (LS + RS) / 2
    mid_hip = (LH + RH) / 2
    vertical_ref = mid_shoulder + np.array([0, 1])
    spine_angle = angle(vertical_ref, mid_shoulder, mid_hip)

    ideal_width = shoulder_width * WIDTH_MULTIPLIER

    hands_inside_torso = (
        LW[0] > LS[0] and LW[0] < RS[0] and
        RW[0] > LS[0] and RW[0] < RS[0]
    )

    details = {}

    details["Feet shoulder-width apart"] = (
        abs(feet_dist - ideal_width) < shoulder_width * WIDTH_TOL
    )

    details["Legs straight"] = (
        left_knee_ang >= STRAIGHT_MIN and
        right_knee_ang >= STRAIGHT_MIN
    )

    details["Body vertical"] = spine_angle < ANGLE_TOL

    details["Hands behind (approx)"] = hands_inside_torso

    details["Shoulders level"] = abs(LS[1] - RS[1]) < LEVEL_TOL

    score = sum(details.values())
    total = len(details)

    suggestions = [k for k, v in details.items() if not v]

    return image, (score / total) * 100, details, suggestions, {}
