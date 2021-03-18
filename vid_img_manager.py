# written by Lexington Whalen

import sys
import os
import cv2 as cv
import numpy as np
from pygame.locals import KEYDOWN, K_ESCAPE, K_q
import pygame as pg

from compare_pose import AngleComparor
from frame_operations import FrameOperations


# manages all vid/img comparisons


class VideoImgManager():

    def __init__(self):
        # inits pygame
        pg.mixer.init()
        pg.font.init()
        pg.init()

        self.CWD = os.getcwd()
        self.RES_F = os.path.join(self.CWD,'resources')
        self.REF_F = os.path.join(self.RES_F,'REFERENCE_POSES')
        self.PERSON_POSES_F = os.path.join(self.RES_F,'PERSON_POSES')
        self.CONNECT_POSES_F = os.path.join(self.RES_F,'CONNECT_POSES')
        self.SNDS = os.path.join(self.RES_F,"SOUNDS")

        # sounds
        self.CONT_SND_PATH = os.path.join(self.SNDS,"continue_song.mp3")
        self.CONT_SND = pg.mixer.Sound(self.CONT_SND_PATH)

        # mixer
        pg.mixer.set_num_channels(8)
        self.SND_CHANNEL = pg.mixer.Channel(5)

        # required classes
        self.ANGLE_COMP = AngleComparor()
        self.FRAME_OPS = FrameOperations()

        # monitor dimensions
        self.W,self.H = pg.display.Info().current_w,pg.display.Info().current_h

        # window stuff, fullscreen window
        pg.display.set_caption("Pose recognition w/ OpenCV")
        #self.WIN = pg.display.set_mode((0,0),pg.FULLSCREEN)
        self.WIN = pg.display.set_mode((self.W,self.H))

        #pg fonts
        self.BEGIN_FONT = pg.font.SysFont('Comic Sans MS',500)
        self.TITLE_FONT = pg.font.SysFont('Comic Sans MS',50)

        # last found stuff
        self.LAST_FOUND_COUNTER = 5
        self.LAST_FOUND_CHAR_IMG = None
        self.LAST_FOUND_TITLE = None
        self.LAST_FOUND_CHAR_IMG = None
        self.FOUND_IN_LAST_FRAMES = [None]*self.LAST_FOUND_COUNTER

        self.CONNECT_POSE_PATHS = []

        for fn in os.listdir(self.CONNECT_POSES_F):
            self.CONNECT_POSE_PATHS.append(fn)


    def get_vid_comparison(self,THR,apply_effects = False, webcam_id=0):
        
        cap = cv.VideoCapture(webcam_id)
        # modify angle threshold for better accuracy

        # for "ticking" through the frames
        i = 0
        
        while True:
            # get the frame, copy it so we don't see all the lines found

            BORDER_SIZE = 20

            ret,frame = cap.read()

            # flip so it looks correct
            frame = cv.flip(frame,1)

            copy = frame.copy()

            in_h,in_w = copy.shape[:2]

            # blit to pg, needs to match the surface dimensions
            # note we swap w and h compared to cv
            self.WIN.fill((0,0,0))

            RIGHT_SIDE_COORDS = (int((self.W * 0.75)-in_w/2),int((self.H * 0.5)-in_h/2))

            LEFT_SIDE_COORDS =(int((self.W * 0.25)-in_w/2),int((self.H * 0.5)-in_h/2))

            IN_SURF = pg.Surface((in_w,in_h))
            BORDER_SURF_IN = pg.Surface((in_w+BORDER_SIZE,in_h+BORDER_SIZE))
            BORDER_SURF_IN.fill((255,255,0))

            self.WIN.blit(BORDER_SURF_IN,((RIGHT_SIDE_COORDS[0] + BORDER_SIZE),RIGHT_SIDE_COORDS[1] + BORDER_SIZE))

            # ref_img is a list of [img, key_angles, full path]
            ref_data, caught_frame = self.ANGLE_COMP.compare_frames(frame,THR)
            
            self.FOUND_IN_LAST_FRAMES[i] = ref_data

            if ref_data is not None:
                #self.LAST_FOUND_CHAR_IMG = ref_data[0]
                self.LAST_FOUND_TITLE = ref_data[2].split("\\")[-1]
                self.LAST_FOUND_CHARACTER_PATH = os.path.join(self.CONNECT_POSES_F,self.LAST_FOUND_TITLE)
                self.LAST_FOUND_CHAR_IMG = cv.imread(self.LAST_FOUND_CHARACTER_PATH)
                

            if any(elem is not None for elem in self.FOUND_IN_LAST_FRAMES):

                # apply the filters on our input frame
                copy = self.FRAME_OPS.apply_filters(copy)

                # now we put the ref_img in pg
                ref_h,ref_w = self.LAST_FOUND_CHAR_IMG.shape[:2]
                REF_SURF = pg.Surface((ref_w,ref_h))
                BORDER_SURF_REF = pg.Surface((ref_w + BORDER_SIZE, ref_h + BORDER_SIZE))
                BORDER_SURF_REF.fill((250,0,0))

                pg_ref_frame = cv.cvtColor(self.LAST_FOUND_CHAR_IMG,cv.COLOR_BGR2RGB).swapaxes(0,1)
                self.WIN.blit(BORDER_SURF_REF, (LEFT_SIDE_COORDS[0] + BORDER_SIZE,LEFT_SIDE_COORDS[1] + BORDER_SIZE))


                pg.surfarray.blit_array(REF_SURF,pg_ref_frame)
                self.WIN.blit(REF_SURF,LEFT_SIDE_COORDS)

                found_webcam_surf = self.TITLE_FONT.render("Nice moves!",False,(255,255,0))
                found_webcam_rect = found_webcam_surf.get_rect(center=(RIGHT_SIDE_COORDS[0] + 100,RIGHT_SIDE_COORDS[1] - 30))

                found_text_surf = self.TITLE_FONT.render("{}".format(self.LAST_FOUND_TITLE),False,(255,0,0))
                found_text_rect = found_text_surf.get_rect(center=(LEFT_SIDE_COORDS[0] + 100 ,LEFT_SIDE_COORDS[1] - 30))


                self.WIN.blit(found_webcam_surf,found_webcam_rect)
                self.WIN.blit(found_text_surf,found_text_rect)

                # play music as long as there is a found ref
                if not self.SND_CHANNEL.get_busy():
                    self.SND_CHANNEL.play(self.CONT_SND)

            else:
                # for the yet unknown reference pose
                # since initially is assumed same dimension as our webcam, resuse the frame dim
                IN_SURF.fill((255,255,255)) #fill white
                BORDER_SURF_IN.fill((255,0,0))
                text_surf = self.BEGIN_FONT.render("?",True,(0,0,0))
                text_rect = text_surf.get_rect(center=(int(in_w/2),int(in_h/2)))

                IN_SURF.blit(text_surf,text_rect)
                self.WIN.blit(BORDER_SURF_IN,((LEFT_SIDE_COORDS[0] + BORDER_SIZE),LEFT_SIDE_COORDS[1] + BORDER_SIZE))

                self.WIN.blit(IN_SURF,LEFT_SIDE_COORDS)


                # not found, thus stop the music
                self.CONT_SND.stop()

            if i < self.LAST_FOUND_COUNTER-1:
                i+=1
            else:
                i = 0

            pg_frame = cv.cvtColor(copy,cv.COLOR_BGR2RGB).swapaxes(0,1)

            # for debugging:
            # pg_frame = cv.cvtColor(frame,cv.COLOR_BGR2RGB).swapaxes(0,1)

            pg.surfarray.blit_array(IN_SURF,pg_frame)
            self.WIN.blit(IN_SURF,RIGHT_SIDE_COORDS)
            

            # put at end of pygame screen operations
            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_q:
                        sys.exit(0)

            


