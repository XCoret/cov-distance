import cv2 as cv
import visio as v
import numpy as np

RED = [255,0,0]
GREEN = [0,255,0]

class Camara(object):
    def __init__(self):
        self.video = cv.VideoCapture('TownCentreXVID.avi')
        
        self.frame = None
        self.homografia = None
        self.matriuH=None


    def get_frame(self):
        ret,frame = self.video.read()
        # Operacions
        self.frame = frame.copy()
        if self.homografia is None:
            
            punts_in=np.float32([[1023,268],[1504,351],[261,731],[961,941]])        
            punts_out = np.float32([[1023,268],[1511,238],[1023,1160],[1511,1160]])

            height,width,_ = frame.shape
            limits = np.float32([[width,width,0],[0,height,height],[0,0,0]])
            self.matriuH,status = cv.findHomography(punts_in,punts_out)

            homografia = cv.warpPerspective(frame,self.matriuH,(width,height))


        #codifiquem en jpeg 
        ret,jpeg = cv.imencode('.jpg',frame)
        ret,out = cv.imencode('.jpg',homografia)

        return [jpeg.tobytes(),out.tobytes()]