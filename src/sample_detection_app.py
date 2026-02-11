import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

from posture_check.savdhan_check import check_savdhan
from posture_check.vishram_check import check_vishram


if __name__ == "__main__":

    st.set_page_config(page_title="Pose Detection", layout="centered")

    st.title("Simple Pose Detection App")

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )

    os.makedirs("sample_images", exist_ok=True)

    if uploaded_file is not None:

        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            st.error("Could not read image")

        else:

            mp_pose = mp.solutions.pose
            mp_drawing = mp.solutions.drawing_utils

            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5
            ) as pose:

                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)

                if results.pose_landmarks:

                    mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Check Savdhan (Attention)"):

                            img2, acc, details, suggestions, values = check_savdhan(
                                image.copy(),
                                results.pose_landmarks
                            )

                            st.image(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB),
                                     use_container_width=True)

                            st.subheader("Savdhan score")
                            st.write("Accuracy :", round(acc, 2), "%")

                            st.subheader("Rule wise")
                            for k in details:
                                st.write(k, ":", "✅" if details[k] else "❌")

                            st.subheader("Suggestions")
                            if len(suggestions) == 0:
                                st.write("Perfect Savdhan posture.")
                            else:
                                for s in suggestions:
                                    st.write("•", s)

                    with col2:
                        if st.button("Check Vishram (Stand at ease)"):

                            img3, acc2, details2, suggestions2, values2 = check_vishram(
                                image.copy(),
                                results.pose_landmarks
                            )

                            st.image(cv2.cvtColor(img3, cv2.COLOR_BGR2RGB),
                                     use_container_width=True)

                            st.subheader("Vishram score")
                            st.write("Accuracy :", round(acc2, 2), "%")

                            st.subheader("Rule wise")
                            for k in details2:
                                st.write(k, ":", "✅" if details2[k] else "❌")

                            st.subheader("Suggestions")
                            if len(suggestions2) == 0:
                                st.write("Correct Vishram posture.")
                            else:
                                for s in suggestions2:
                                    st.write("•", s)

                else:
                    st.warning("No body detected")

            original_name = uploaded_file.name
            save_name = "pose_detection_" + original_name
            save_path = os.path.join("sample_images", save_name)

            cv2.imwrite(save_path, image)

            st.success("Saved as : " + save_path)

            st.image(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                caption=save_name,
                use_container_width=True
            )
