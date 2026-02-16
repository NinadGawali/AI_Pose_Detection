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

def check_bahine_mud(image, pose_landmarks):
    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i): return np.array([lm[i].x, lm[i].y])
    def V(i): return lm[i].visibility
    def Z(i): return lm[i].z # Depth

    # ----------- LANDMARKS -----------
    LS_raw = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
    RS_raw = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    
    LS = P(mp_pose.PoseLandmark.LEFT_SHOULDER)
    RS = P(mp_pose.PoseLandmark.RIGHT_SHOULDER)
    LA = P(mp_pose.PoseLandmark.LEFT_ANKLE)
    RA = P(mp_pose.PoseLandmark.RIGHT_ANKLE)

    # 1. THE STACKING CHECK (X-axis)
    # At 90 degrees, the distance between shoulder X-coords should be almost zero.
    shoulder_x_gap = abs(LS[0] - RS[0])
    # 0.08 is a very strict threshold (about 8% of frame width)
    is_rotated_x = shoulder_x_gap < 0.08 

    # 2. THE DIRECTION CHECK (Z-axis)
    # For a LEFT turn (Bahine Mud), the Right Shoulder MUST be closer to the camera.
    # In MediaPipe, smaller Z means closer to camera.
    turned_left_correctly = RS_raw.z < LS_raw.z - 0.1 

    # 3. FEET ALIGNMENT
    feet_stacked = abs(LA[0] - RA[0]) < 0.08

    # ----------- WEIGHTED SCORING -----------
    details = {
        "Shoulders Stacked": is_rotated_x,
        "Turned Left (Not Right)": turned_left_correctly,
        "Feet Aligned": feet_stacked
    }

    # Weightage: 40% for stacking, 40% for correct direction, 20% for feet.
    score = 0
    if is_rotated_x: score += 40
    if turned_left_correctly: score += 40
    if feet_stacked: score += 20

    suggestions = []
    if not is_rotated_x:
        suggestions.append("Turn your shoulders fully 90 degrees.")
    if not turned_left_correctly:
        suggestions.append("Ensure you turned LEFT (Right shoulder should face camera).")
    if not feet_stacked:
        suggestions.append("Align your heels in a single line.")

    return image, score, details, suggestions, {"x_gap": shoulder_x_gap, "z_diff": RS_raw.z - LS_raw.z}