import cv2 as cv
import visio as v
import numpy as np
from google.cloud import vision
ORANGE = (0, 127, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

class VideoCamera(object):
    def __init__(self, src):
        self.video = cv.VideoCapture(src)
        self.client = vision.ImageAnnotatorClient()

    def __del__(self):
        self.video.release()
        

    def get_frame(self):
        ret, frame = self.video.read()

        punts_in = np.float32([ [1165,171], [1614,222], [250,725], [984,900]])
        punts_out = np.float32([[1165, 171], [1165+451.887154, 171], [1165, 275+1069.645268], [1165+451.887154, 275+1069.645268]])
        # resize
        h,w,_ = frame.shape
        dim=(w,h)
        resized = frame.copy()
        resized = cv.resize(resized,dim, interpolation=cv.INTER_AREA)
        h,w,_ = resized.shape
        
        for i in range(len(punts_out)):
            punts_out[i][0] = punts_out[i][0]/3+(punts_out[i][0]/3)
            punts_out[i][1] = punts_out[i][1]/3+(punts_out[i][1]/3)
        
        # Generem la matriu per la Homografia
        perspectiveMatrix = cv.getPerspectiveTransform(punts_in,punts_out)

        # Buscar persones en el frame
        pedestrians = v.findPedestrians(resized,self.client)

        be_width = int(punts_out[1][0]-punts_out[0][0])
        be_height = int(punts_out[2][1]-punts_out[0][1])

        bird_eye = cv.warpPerspective(resized, perspectiveMatrix, (frame.shape[1], frame.shape[0]), cv.INTER_CUBIC | cv.WARP_INVERSE_MAP)

        amplada_punts = abs(punts_out[3][0]-punts_out[2][0])
        closeOnes = v.calcDistances(resized,pedestrians,perspectiveMatrix,punts_in,punts_out)
        for p in pedestrians:
            frame = v.drawBox(image=frame, bounding=p.bounding_poly, color=GREEN, caption='', score=0)
            bird_eye = v.drawBirdEye(
                bird_eye, p.bounding_poly, GREEN, punts_in, punts_out, perspectiveMatrix)
        for c in closeOnes:
            if c[2] < 1.5:
                color=RED
            else:
                color=ORANGE
            frame = v.drawBox(image=frame, bounding=c[0].bounding_poly,color=color,caption='',score=0)
            frame = v.drawBox(image=frame, bounding=c[1].bounding_poly,color=color,caption='',score=0)

            bird_eye = v.drawBirdEye(bird_eye, c[0].bounding_poly, color, punts_in, punts_out,perspectiveMatrix)
            bird_eye = v.drawBirdEye(
                bird_eye, c[1].bounding_poly, color, punts_in, punts_out, perspectiveMatrix)

            x1 = int((c[0].bounding_poly.normalized_vertices[2].x - (abs(c[0].bounding_poly.normalized_vertices[2].x-c[0].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y1 = int((c[0].bounding_poly.normalized_vertices[2].y - (abs(c[0].bounding_poly.normalized_vertices[2].y-c[0].bounding_poly.normalized_vertices[1].y)/2)) * frame.shape[0])
            
            x2 = int((c[1].bounding_poly.normalized_vertices[2].x - (abs(c[1].bounding_poly.normalized_vertices[2].x-c[1].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y2 = int((c[1].bounding_poly.normalized_vertices[2].y - (abs(c[1].bounding_poly.normalized_vertices[2].y-c[1].bounding_poly.normalized_vertices[1].y)/2)) * frame.shape[0])      

            p1 = (x1,y1)
            p2 = (x2,y2)
            frame = cv.line(frame, p1, p2, color, 1)
            center = (int((x1 + x2)/2), int((y1 + y2)/2))
            frame = cv.putText(frame, '{0:.2f}m'.format( c[2]), center, cv.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv.LINE_AA)
        
        return [frame, bird_eye]       




