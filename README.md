# AI_Pose_Detection
This repository is dedicated for AI Pose Detection for Army drills using OpenCV and Image Processing techniques. The main goal is to detect and analyze the poses of soldiers during drills, providing insights and feedback for training purposes.

## Instructions to setup the project:
1. Clone the repository to your local machine.
2. Navigate to the project directory and create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the required dependencies using pip:
   ```bash
    pip install -r requirements.txt
    ```
4. Create a folder named `dataset` in the project directory and add your training images of soldiers in drill poses. Ensure that the images are named appropriately for easy reference.

## Usage:
### 1. Run streamlit_app_test_script.py
This script will launch a Streamlit web application where you can upload an image and see the body landmarks detected by MediaPipe.

1. Create a sample image of a soldier in a drill pose and save it in the `sample_images` folder.
2. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app_test_script.py
   ```
3. Upload your sample image through the web interface and observe the detected body landmarks.

4. The output image with detected landmarks will be saved in the `sample_images` folder with the name `pose_detection_<original_name>`.
