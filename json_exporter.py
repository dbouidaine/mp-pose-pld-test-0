import os
import sys
import json
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
body_parts_mp = ['nose','nose']
body_parts = ["Marker_1","Marker_2","Marker_3","Marker_4","Marker_5","Marker_6"
,"Marker_7","Marker_8","Marker_9","Marker_10","Marker_11"
,"Marker_12","Marker_13","Marker_14","Marker_15","Marker_16"
,"Marker_17","Marker_18","Marker_19","Marker_20","Marker_21"
,"Marker_22","Marker_23","Marker_24","Marker_25","Marker_26"
,"Marker_27","Marker_28","Marker_29"]
"""
body_parts = ['root','lowerback','upperback','thorax','lowerneck','upperneck','head','rclavicle','rhumerus',
              'rradius','rwrist','rhand','rfingers','rthumb','lclavicle','lhumerus','lradius','lwrist',
              'lhand','lfingers','lthumb','rfemur','rtibia','rfoot','rtoes','lfemur','ltibia','lfoot',
              'ltoes']"""
body_parts_csv = [  "LBWT","RBWT","LFWT" ,
 	                "LTHI" ,"RFRM" ,
                    "RTHI" ,"RWRB" ,"RWRA","STRN" ,"T10" ,
                    "RFIN","RUPA","LKNE" ,"RKNE","LUPA","CLAV",
                    "LELB","RSHO","LFRM" ,"LSHN","RSHN","LBHD" ,
                    "LFHD","RBHD" ,"RFHD" ,"RANK" ,"LANK" ,"RHEE" ,
                    "LHEE" ,"LTOE" ,"RTOE" ,"LMT5" ,"RMT5" ,"RFWT" ,"RELB" ,
                    "RBAC" ,"LSHO" ,"C7" ,"LWRA" ,"LFIN" ,"LWRB" ,
                    "RBAC_1" 
]

input_path = './'+argv[1]
output_path = './'+argv[2]
print(output_path+'/landmarks')
separator = ","
files = os.listdir(input_path)
try:
    os.makedirs(output_path + '/landmarks')
except OSError as error:
    print(error)

del argv[0]

for link in files:
    print(link)
    cap = cv2.VideoCapture(input_path+'/'+link)
    h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    f = int(cap.get(cv2.CAP_PROP_FPS))
    # frames timestamp

    out = cv2.VideoWriter(output_path+'/videos/'+link, cv2.VideoWriter_fourcc('m','p','4','v'), f,(h,w))
    file_landmarks = open(output_path+'/landmarks/'+link+'.json', 'w+')
    data_to_print = {
        'frequency': f,
        'landmarks':[]
    }
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
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

            # Recolor Feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image[0:1000, 0:1000] = (0, 0, 0)
            if landmarks:
                for index in landmarks_to_exclude:
                    landmarks.landmark[index].visibility = 0.0
                # num_array[2:7] = array('i', range(22, 27))
                mpDraw.draw_landmarks(image, landmarks, None,
                                      mpDraw.DrawingSpec(color=(224, 224, 224), thickness=2, circle_radius=1),
                                      )
                cv2.imshow("Video Feed", image)
                frame_time = i / f
                # yzx
                landmarks_all_frames=[]
                for index in range(29):
                    landmarks_frame={}
                    landmarks_frame['x'] = landmarks.landmark[index].x
                    landmarks_frame['y'] = landmarks.landmark[index].y
                    landmarks_frame['z'] = landmarks.landmark[index].z
                    landmarks_frame['visibility'] = landmarks.landmark[index].visibility
                    landmarks_all_frames.append(landmarks_frame)
                    if i == 1:
                        print (data_to_print)
                data_to_print['landmarks'].append(landmarks_all_frames)
                i += 1

            out.write(image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        else:
            break


    file_landmarks.write(json.dumps(data_to_print))
    cap.release()
    out.release()

    file_landmarks.close()
    cv2.destroyAllWindows()
