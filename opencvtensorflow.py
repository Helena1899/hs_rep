
'''
import cv2
import time
import numpy as np
import argparse
import logging
import pupil_apriltags as atgs

# load class getUnconnectedOutLayersNames
with open('object_detection_classes_coco.txt', 'r') as f:
    class_names = f.read().split('\n')

model = cv2.dnn.readNet(model = 'frozen_inference_graph.pb', config='ssd_mobilenet_v2_coco_2018_03_29.pbtxt.txt', framework='Tensorflow')

#capture = cv2.VideoCapture( 1 ) # retrieve live feed form webcam
#capture = cv2.imread( 'arpiltag.png' ) # retrieve live feed form webcam
#capture = cv2.VideoCapture( 'https://s.evodyne.co/arl/video_1.mp4' ) # video in SF
#capture = cv2.VideoCapture('https://s.evodyne.co/arl/stream.mp4') # evodyne video
#capture = cv2.VideoCapture( 'https://192.168.200.149/:8000' ) # dog video

while True:
    ret, img = capture.imread('arpiltag.png')

    height, width, channels = img.shape
    print("width:", width, "height:", height)
    blob = cv2.dnn.blobFromImage(image=img, size=(300,300), mean=(104,117,123), swapRB=True)
    model.setInput(blob)
    output = model.forward()
    for detection in output[0,0,:,:]:
        confidence = detection[2]
        if ( confidence > 0.4 ):
            class_id = detection[1]
            class_name = class_names[int(class_id)-1]
            color = (0,255,255)
            box_x      = detection[3] * width
            box_y      = detection[4] * height
            box_width  = detection[5] * width
            box_height = detection[6] * height
            cv2.rectangle( img, (int(box_x), int(box_y)), (int(box_width), int(box_height)), color, thickness = 2 )
            cv2.putText( img, class_name, (int(box_x), int(box_y-5)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    #gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY ) # changes the color image to gray
    #cv2.imwrite("grayscale.jpg", gray)
    # show the image

    cv2.imshow( "Image", img )
    if (cv2.waitKey( 1 ) == 27 ): # wait for 1 ms
        break

capture.release() # release camera screen
cv2.destroyAllWindows() # closes the windows
'''

import cv2

img = cv2.imread( "apriltag.png" ) # use own filename ...
height, width, channels = img.shape

print("width:", width, "height:", height) # prints the width and height of file

gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY ) # changes the color image to gray

cv2.imwrite("grayscale.jpg", gray)

# show the image
cv2.imshow( "Image", gray )
cv2.waitKey( 0 ) # wait indefinately
cv2.destroyAllWindows()
