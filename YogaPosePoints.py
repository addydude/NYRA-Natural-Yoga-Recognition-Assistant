import numpy as np
import cv2
import time 
import PoseModule as pm

cap=cv2.VideoCapture(0)

detector=pm.PoseDetector()

while True:
    # success, img= cap.read()
    # img= cv2.resize(img,(1280,728))
    img=cv2.imread("images/tadasan.jpg")
    # img=cv2.imread("images/vrksana.jpg")
    # img=cv2.imread("images/trikonasana.jpg")
    # img=cv2.imread("images/virabhadrasana.jpg")
    # img=cv2.imread("images/adho_mukha.jpeg")
    # img=cv2.imread("images/balasana.jpg")
    img=detector.findPose(img,False)
    lmlist=detector.getPosition(img,False)
    # print(lmlist)
    if len(lmlist) !=0:
        #right arm
        right_arm=detector.findAngle(img,12,14,16)
        #left arm
        left_arm=detector.findAngle(img,11,13,15)
        #right leg
        right_leg=detector.findAngle(img,24,26,28)
        #left leg
        left_leg=detector.findAngle(img,23,25,27)

     #storing the angle data of 6 yoga poses   
    AngleData = [{'Name': 'tadasan', 'right_arm': 201, 'left_arm': 162, 'right_leg':177,'left_leg':182},
    {'Name': 'vrksana', 'right_arm': 207, 'left_arm': 158, 'right_leg':180,'left_leg':329},
    {'Name': 'balasana', 'right_arm': 155, 'left_arm': 167, 'right_leg':337,'left_leg':335},
    {'Name': 'trikonasana', 'right_arm': 181, 'left_arm': 184, 'right_leg':176,'left_leg':182},
    {'Name': 'virabhadrasana', 'right_arm': 167, 'left_arm': 166, 'right_leg':273,'left_leg':178},
    {'Name': 'adhomukha', 'right_arm': 176, 'left_arm': 171, 'right_leg':177,'left_leg':179},
    # New poses added
    {'Name': 'bhujangasana', 'right_arm': 160, 'left_arm': 160, 'right_leg':175,'left_leg':175},
    {'Name': 'setubandhasana', 'right_arm': 195, 'left_arm': 195, 'right_leg':260,'left_leg':260},
    {'Name': 'uttanasana', 'right_arm': 180, 'left_arm': 180, 'right_leg':180,'left_leg':180},
    {'Name': 'shavasana', 'right_arm': 180, 'left_arm': 180, 'right_leg':180,'left_leg':180},
    {'Name': 'ardhamatsyendrasana', 'right_arm': 175, 'left_arm': 250, 'right_leg':270,'left_leg':190}]

   
    cv2.imshow("Image", img)
    cv2.waitKey(1)


