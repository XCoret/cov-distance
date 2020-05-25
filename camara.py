import cv2 as cv
import visio as v
import numpy as np
import visio


class Camara(object):
    def __init__(self,src=None):
        self.video = cv.VideoCapture(src)
        
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
            self.matriuH = cv.getPerspectiveTransform(punts_in,punts_out)

            homografia = cv.warpPerspective(frame,self.matriuH,(width,height))


        frame = self.frame.copy()
        persons = visio.getPersons(frame)
        for person in persons:
            frame = visio.drawBorders(frame, person.bounding_poly, (0,127,255),score = person.score*100)

        return [frame, homografia]
