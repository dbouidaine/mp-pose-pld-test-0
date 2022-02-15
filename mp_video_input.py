import os
import sys

import cv2
import mediapipe as mp
from moviepy.editor import *
from sys import argv
from os import listdir
from mediapipe.framework.formats import landmark_pb2


if argv[1] is None :
    sys.exit(-1)

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
)

landmarks_to_exclude = [1,2,3,4,5,6,7,8,9,10,17,18,19,20,21,22,29,30,31,32]

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
    h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    f = int(cap.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(output_path+'/videos/'+link, cv2.VideoWriter_fourcc('m','p','4','v'), f,(h,w))
    file_landmarks = open(output_path+'/landmarks/'+link+'.txt', 'w+')
    i = 1
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
        # print(landmarks.landmark) maybe the solution to the problem of exporting landmarks
        # is to export the sequence of landmarks for each point like this :
        # {
        #   0 => [0.1,0.2,...etc],
        #   1 => [...],
        #   ...,
        #   32 => [...]
        # }
        # because animation in threejs takes into consideration each points seperately from the other
        for index in landmarks_to_exclude:
            landmarks.landmark[index].visibility = 0.0

        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image[0:1000, 0:1000] = (0, 0, 0)
        if landmarks:
            #num_array[2:7] = array('i', range(22, 27))
            mpDraw.draw_landmarks(image, landmarks, None,
                                  mpDraw.DrawingSpec(color=(224, 224, 224), thickness=2, circle_radius=1),
                                  )
            file_landmarks.write(str(landmarks))

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
