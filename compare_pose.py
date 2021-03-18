# written by Lexington Whalen

# Compares two poses
# holds a dictionary of pose images and their points
# use this to compare live poses w/in a threshold


# NOTE: WE DO NOT HAVE TO FLIP IMAGE FILES HERE.

import os
import numpy as np
import cv2 as cv

from pose_estimator import PoseEstimator

class AngleComparor():

    def __init__(self):
        self.P_E = PoseEstimator(thr=0.07)

        self.CWD = os.getcwd()
        self.RES_F = os.path.join(self.CWD,'resources')
        self.REF_F = os.path.join(self.RES_F,'REFERENCE_POSES')

        # REFS and INS hold lists of lists of form [[img_path,KEY_ANGLES],...]
        self.REFS = []
        self.INS = []

        self.CONNECT_POSES = []

        # get the key angles for the reference images
        for fn in os.listdir(self.REF_F):
            full_path = os.path.join(self.REF_F,fn)
            img = cv.imread(full_path)
            # use a copy so we don't see the angles and such on the reference, can change remove if you want to 
            copy = img.copy()
            img, key_angles = self.P_E.get_pose_key_angles(img)

            #cv.imshow(fn,img)
            #cv.waitKey(0)

            self.REFS.append([copy,key_angles,full_path])
    

    def compare_frames(self,frame,THR):
        
        found, key_angles = self.P_E.get_pose_key_angles(frame)

        frame_data = [found,key_angles]


        for ref_n, ref in enumerate(self.REFS):

            # note again that I am only checking the upper half of body angles
            try:
                if len(frame_data)==2 and not None in frame_data[1]["RArm"] and not None in frame_data[1]["LArm"] and (len(frame_data[1]["RArm"]) == 2) and (len(frame_data[1]["LArm"])==2) and (ref[1]["RArm"][0]- THR<= frame_data[1]["RArm"][0] <= ref[1]["RArm"][0]+THR) and ((ref[1]["RArm"][1]- THR<= frame_data[1]["RArm"][1] <= ref[1]["RArm"][1]+THR)
                        and (ref[1]["LArm"][0]- THR<= frame_data[1]["LArm"][0] <= ref[1]["LArm"][0]+THR) and (ref[1]["LArm"][1]- THR<= frame_data[1]["LArm"][1] <= ref[1]["LArm"][1]+THR)):

                        return ref,frame
            except IndexError:
                return None, frame
        
        
            if ref_n == len(self.REFS)-1:
                # if looped thru all and found nothing, just return None
                return None, frame

        