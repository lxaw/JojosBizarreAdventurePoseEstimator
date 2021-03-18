import cv2 as cv
import time 
from pose_estimator import PoseEstimator
   
  
# SET THE COUNTDOWN TIMER 
# for simplicity we set it to 3 
# We can also take this as input 
TIMER = int(20) 
   
# Open the camera 
cap = cv.VideoCapture(0) 

P_E = PoseEstimator(thr=0.07)
   
  
while True: 
      
    # Read and display each frame 
    ret, img = cap.read() 

    img = cv.flip(img,1)

    copy = img

    cv.imshow('a', img) 


  
    # check for the key pressed 
    k = cv.waitKey(125) 
  
    # set the key for the countdown 
    # to begin. Here we set q 
    # if key pressed is q 
    if k == ord('f'): 
        prev = time.time() 
  
        while TIMER >= 0: 
            ret, img = cap.read() 

            img = cv.flip(img,1)

            copy = img
            found,key_angles = P_E.get_pose_key_angles(img)
  
            # Display countdown on each frame 
            # specify the font and draw the 
            # countdown using puttext 
            font = cv.FONT_HERSHEY_SIMPLEX 
            cv.putText(img, str(TIMER),  
                        (200, 250), font, 
                        7, (0, 255, 255), 
                        4, cv.LINE_AA) 
            cv.imshow('a', img) 
            cv.waitKey(125) 
  
            # current time 
            cur = time.time() 
  
            # Update and keep track of Countdown 
            # if time elapsed is one second  
            # than decrese the counter 
            if cur-prev >= 1: 
                prev = cur 
                TIMER = TIMER-1
  
        else: 
            ret, img = cap.read() 

            img = cv.flip(img,1)

            copy = img.copy()

            found,key_angles = P_E.get_pose_key_angles(img)

            # Display the clicked frame for 2  
            # sec.You can increase time in  
            # waitKey also 
            cv.imshow('a', img) 
  
            # time for which image displayed 
            cv.waitKey(2000) 
  
            # Save the frame 
            cv.imwrite('camera.png', copy) 
            cv.imwrite('camera_angles.png', img) 
  
            # HERE we can reset the Countdown timer 
            # if we want more Capture without closing 
            # the camera 
  
    # Press Esc to exit 
    elif k == ord("q"): 
        break
  
# close the camera 
cap.release() 
   
# close all the opened windows 
cv.destroyAllWindows()