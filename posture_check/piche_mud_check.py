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
    mp_pose = mp.solutions.pose
    lm = pose_landmarks.landmark

    def P(i): return np.array([lm[i].x, lm[i].y])
    def V(i): return lm[i].visibility
    def Z(i): return lm[i].z

    # -------- 1. ROTATION LOGIC (SWAP-CENTRIC) --------
    
    # X-Swap Logic (PRIMARY WEIGHT)
    # Facing Camera: Left Shoulder (11).x > Right Shoulder (12).x 
    # Facing Away: Left Shoulder (11).x < Right Shoulder (12).x
    ls_x = lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x
    rs_x = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x
    is_swapped = ls_x < rs_x

    # -------- 2. OTHER PARAMETERS --------
    LS, RS = P(11), P(12)
    LH, RH = P(23), P(24)
    LW, RW = P(15), P(16)
    
    # Pinned Arms check
    shoulder_width = abs(LS[0] - RS[0]) + 1e-6
    arms_pinned = (np.linalg.norm(LW - LH) / shoulder_width < 0.75 and 
                   np.linalg.norm(RW - RH) / shoulder_width < 0.75)
    
    # Posture checks
    shoulders_level = abs(LS[1] - RS[1]) < 0.07
    head_steady = abs(lm[0].y - (LS[1] + RS[1])/2) < 0.15

    # ====================================================
    #           REDISTRIBUTED WEIGHTED SCORING
    # ====================================================
    # Total 100
    score = 0
    if is_swapped: score += 55       # Increased from 30
    if arms_pinned: score += 20      # Increased from 10
    if shoulders_level: score += 15  # Increased from 10
    if head_steady: score += 10
    
    # Logic results for UI
    checks = {
        "180 Rotation (Swap)": is_swapped,
        "Arms Pinned": arms_pinned,
        "Shoulders Level": shoulders_level,
        "Head Steady": head_steady
    }

    suggestions = []
    if not is_swapped:
        suggestions.append("Turn fully until shoulders are swapped from camera view.")
    if not arms_pinned:
        suggestions.append("Keep your hands locked at your sides.")
    if not shoulders_level:
        suggestions.append("Don't tilt your shoulders during the turn.")

    return image, score, checks, suggestions, {"ls_x": ls_x, "rs_x": rs_x}