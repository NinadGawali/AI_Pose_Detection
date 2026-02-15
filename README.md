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


### 2. Update in sample_detection_app2.py
The script now includes functionality to check accuracy of the chosen pose for practise with live feedback.It makes use of the inbuilt webcam to capture live video feed and analyze the poses in real-time. The user can select the posture they want to check (Savdhan or Vishram or Salute etc) and the script will provide feedback on the accuracy of the posture based on the detected landmarks. Posture checking logic is implemented in the code files in the `posture_check` folder.
1. Run the sample detection app:
   ```bash
   streamlit run src/sample_detection_app2.py
   ```
2. Select the posture you want to check 
3. The app will use the webcam to capture live video feed and analyze the poses in real-time, providing feedback on the accuracy of the posture.

