import os
import sys

import cv2
import mediapipe as mp
from moviepy.editor import *
from sys import argv
from os import listdir

if argv[1] is None :
    sys.exit(-1)

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
)

input_path = './'+argv[1]
output_path = './'+argv[2]
print(output_path+'/landmarks')
files = os.listdir(input_path)
try:
    os.makedirs(output_path + '/landmarks')
except OSError as error:
    print(error)

try:
    os.makedirs(output_path + '/videos')
except OSError as error:
    print(error)

try:
    os.makedirs(output_path + '/black_videos')
except OSError as error:
    print(error)


del argv[0]

for link in files:
    print(link)
    cap = cv2.VideoCapture(input_path+'/'+link)
    out = cv2.VideoWriter(output_path+'/videos/'+link, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 20,(640,480))
    file_landmarks = open(output_path+'/landmarks/'+link, 'w+')

    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor Feed
        if frame is not None:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            break

        # Make Predictions
        results = pose.process(image)
        landmarks = results.pose_landmarks

        # Recolor Feed
        image[0:1000, 0:1000] = (0, 0, 0)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(image, results.pose_landmarks, None,
                                  mpDraw.DrawingSpec(color=(224, 224, 224), thickness=1, circle_radius=1),
                                  )
            file_landmarks.write(str(results.pose_landmarks))

        cv2.imshow("Video Feed", image)
        out.write(image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()

    # Concatenate 2 videos
    clip_1 = VideoFileClip(input_path+'/'+link)
    clip_2 = VideoFileClip(output_path+'/videos/'+link)
    final_clip = clips_array([[clip_1, clip_2]])
    final_clip.write_videofile(output_path+'/black_videos/'+link, codec="libx264")
    cv2.destroyAllWindows()
