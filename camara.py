'''Modul de video'''
# Aquest es l'encarregat de capturar els frames del video


import cv2 as cv
import visio as v
import numpy as np
from google.cloud import vision
ORANGE = (0, 127, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

''' 
Classe VideoCamera()
    Aquesta classe representa l'objecte que anira capturant els frames del video a tractar, tambe de realitzar alguna 
    operacio relacionada amb la part de Visio per temes de agilitzar el fluxe del programa, com ara calcular la homografia
    Tambe fara crides a les funcions del modul de Visio per poder processar i tractar els frames que captura.
'''
class VideoCamera(object):
    def __init__(self, src):
        self.video = cv.VideoCapture(src)

        ''' ---- CLOUD VISION ----
            Definim el client per utilitzar els serveis de Cloud Vision '''
        self.client = vision.ImageAnnotatorClient()

    def __del__(self):
        self.video.release()
        

    ''' 
    get_frame() Llegeix un frame de video, en crea la seva homografia i crida a les funcions de visio per calcular la distancia entre els vianants i dibuixar els resultats
           
        retorna: 
            Els dos frames, l'original amb els requadres i l'homografia amb els cercles
    '''
    def get_frame(self):
        ret, frame = self.video.read()
        # punts_in: punts d'entrada utilitzats per realitzar la homografia
        # punts_out: punts de sortida utilitzats per realitzar la homografia
        punts_in = np.float32([ [1165,171], [1614,222], [250,725], [984,900]])
        punts_out = np.float32([[1165, 171], [1165+451.887154, 171], [1165, 275+1069.645268], [1165+451.887154, 275+1069.645268]])
        # resize
        scale_percent =50 
        h,w,_ = frame.shape
        w = int(frame.shape[1] * scale_percent / 100)
        h = int(frame.shape[0] * scale_percent / 100)
        dim=(w,h)
        # Redimensionem el frame per un tractament mes rapid ja que la imatge de video es de 1920x1080 pixels
        punts_in = punts_in*(scale_percent/100)
        punts_out = punts_out*(scale_percent/100)        
        resized = frame.copy()
        resized = cv.resize(resized,dim, interpolation=cv.INTER_AREA)
        h,w,_ = resized.shape
        
        # Readaptem els punts_out per que capiguen en la mida del frame
        for i in range(len(punts_out)):
            punts_out[i][0] = punts_out[i][0]/3+(punts_out[i][0]/3)
            punts_out[i][1] = punts_out[i][1]/3+(punts_out[i][1]/3)
        
        # Generem la matriu per la Homografia
        perspectiveMatrix = cv.getPerspectiveTransform(punts_in,punts_out)

        # Buscar persones en el frame
        pedestrians = v.findPedestrians(resized,self.client)

        # Generem la homografia (vista d'ocell)
        be_width = int(punts_out[1][0]-punts_out[0][0])
        be_height = int(punts_out[2][1]-punts_out[0][1])

        bird_eye = cv.warpPerspective(resized, perspectiveMatrix, (frame.shape[1], frame.shape[0]), cv.INTER_CUBIC | cv.WARP_INVERSE_MAP)

        amplada_punts = abs(punts_out[3][0]-punts_out[2][0])
        
        # Trobem les parelles de vianants propers
        closeOnes = v.calcDistances(resized,pedestrians,perspectiveMatrix,punts_in,punts_out)
        for p in pedestrians:
            # Dibuixem tots els vianants en verd en els dos frames
            frame = v.drawBox(image=frame, bounding=p.bounding_poly, color=GREEN, caption='', score=0)
            bird_eye = v.drawBirdEye(
                bird_eye, p.bounding_poly, GREEN, punts_in, punts_out, perspectiveMatrix)

        for c in closeOnes:
            if c[2] < 1.5:
                color=RED
            else:
                color=ORANGE
            # Depenent de a quina distancia es trobin dibuixem els vianants propers en taronja o en vermell en els dos frames
            frame = v.drawBox(image=frame, bounding=c[0].bounding_poly,color=color,caption='',score=0)
            frame = v.drawBox(image=frame, bounding=c[1].bounding_poly,color=color,caption='',score=0)

            bird_eye = v.drawBirdEye(bird_eye, c[0].bounding_poly, color, punts_in, punts_out,perspectiveMatrix)
            bird_eye = v.drawBirdEye(bird_eye, c[1].bounding_poly, color, punts_in, punts_out, perspectiveMatrix)



            # Dibuixem una linia entre els punts dels vianants propers a la homografia
            x1 = int((c[0].bounding_poly.normalized_vertices[2].x - (abs(c[0].bounding_poly.normalized_vertices[2].x-c[0].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y1 = int((c[0].bounding_poly.normalized_vertices[2].y ) * frame.shape[0])

            x2 = int((c[1].bounding_poly.normalized_vertices[2].x - (abs(c[1].bounding_poly.normalized_vertices[2].x-c[1].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y2 = int((c[1].bounding_poly.normalized_vertices[2].y ) * frame.shape[0])
            
            p1 = (x1,y1)
            p2 = (x2,y2)            
            bird_eye = cv.line(bird_eye, v.getPerspectiveCoords(perspectiveMatrix, p1), v.getPerspectiveCoords(perspectiveMatrix, p2), color, 2)


            # Dibuixem una linia entre els vianants propers al frame original i escribim la distancia en metres
            x1 = int((c[0].bounding_poly.normalized_vertices[2].x - (abs(c[0].bounding_poly.normalized_vertices[2].x-c[0].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y1 = int((c[0].bounding_poly.normalized_vertices[2].y - (abs(c[0].bounding_poly.normalized_vertices[2].y-c[0].bounding_poly.normalized_vertices[1].y)/2)) * frame.shape[0])
            
            x2 = int((c[1].bounding_poly.normalized_vertices[2].x - (abs(c[1].bounding_poly.normalized_vertices[2].x-c[1].bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y2 = int((c[1].bounding_poly.normalized_vertices[2].y - (abs(c[1].bounding_poly.normalized_vertices[2].y-c[1].bounding_poly.normalized_vertices[1].y)/2)) * frame.shape[0])      

            p1 = (x1,y1)
            p2 = (x2,y2)
            frame = cv.line(frame, p1, p2, color, 2)
            center = (int((x1 + x2)/2), int((y1 + y2)/2))
            frame = cv.putText(frame, '{0:.2f}m'.format( c[2]), center, cv.FONT_HERSHEY_SIMPLEX, 1.5, color, 2, cv.LINE_AA)
        
        return [frame, bird_eye]       




