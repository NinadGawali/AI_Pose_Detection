import cv2
import mediapipe as mp
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

img_path = os.getenv("img1")

# create output folder
os.makedirs("sample_images", exist_ok=True)

# read image
image = cv2.imread(img_path)
image = cv2.imread("sample_images\\img2.png")
if image is None:
    print("Image not found. Check img1 path in .env")
    exit()

# mediapipe pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=False,
        min_detection_confidence=0.5) as pose:

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
    else:
        print("No body detected")

# save output
out_path = os.path.join("sample_images", "pose_exoskeleton2.png")
cv2.imwrite(out_path, image)

print("Saved at:", out_path)
