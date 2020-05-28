import numpy as np
import cv2 as cv

import math
from google.cloud import vision

class covDistance():
    def __init__(self, src, punts_in, punts_out):
        self.src = src
        self.client = vision.ImageAnnotatorClient()
        self.cap = cv.VideoCapture(src)
        self.perspectiveMatrix = None

        self.metres = 5.0
        
        self.punts_in = punts_in
        self.punts_out = punts_out
        self.rescaled = False

        self.frame = None


    #funcio per trobar els punts de la imatge original a la homografia
    def getPerspectiveCoords(self, p):
        px = (self.perspectiveMatrix[0][0]*p[0] + self.perspectiveMatrix[0][1]*p[1] + self.perspectiveMatrix[0][2]) / ((self.perspectiveMatrix[2][0]*p[0] + self.perspectiveMatrix[2][1]*p[1] + self.perspectiveMatrix[2][2]))
        py = (self.perspectiveMatrix[1][0]*p[0] + self.perspectiveMatrix[1][1]*p[1] + self.perspectiveMatrix[1][2]) / ((self.perspectiveMatrix[2][0]*p[0] + self.perspectiveMatrix[2][1]*p[1] + self.perspectiveMatrix[2][2]))
        return int(px),int(py)   

    def resizeFrame(self, scale_percent):
        width = int(self.frame.shape[1] * scale_percent / 100)
        height = int(self.frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        self.frame = cv.resize(self.frame, dim, interpolation=cv.INTER_AREA)
        if self.rescaled == False:
            self.punts_in = self.punts_in*(scale_percent/100)
            self.punts_out = self.punts_out*(scale_percent/100)
            self.rescaled = True
            for i in range(len(self.punts_out)):
                self.punts_out[i][0] = self.punts_out[i][0]/3+(self.punts_out[i][0]/3)
                self.punts_out[i][1] = self.punts_out[i][1]/3+(self.punts_out[i][1]/3)

    def findPedestrians(self):
        height,width, _ = self.frame.shape
        image = vision.types.Image(content = cv.imencode('.jpg',self.frame)[1].tobytes())
        objects = self.client.object_localization(image = image).localized_object_annotations

        pedestrians = []
        for obj in objects:
            if obj.name == 'Person':
                pedestrians.append(obj)
        return pedestrians

    def drawBox(self,image, bounding, color, caption='', score =0):
        height,width,_ = image.shape
        p1 = [int(bounding.normalized_vertices[0].x * width), int(bounding.normalized_vertices[0].y * height)]
        p2 = [int(bounding.normalized_vertices[2].x * width), int(bounding.normalized_vertices[2].y * height)]
        
        image = cv.rectangle(image,(p1[0],p1[1]),(p2[0],p2[1]),color,2)

        fontScale = 0.35
        thickness = 1
        fontColor = (0,0,0)
        if score!=0:
            image = cv.putText(image,caption+'{0:.2f}m'.format(score),(int((bounding.normalized_vertices[0].x -((bounding.normalized_vertices[1].x-bounding.normalized_vertices[0].x)/2) )* width), int(bounding.normalized_vertices[0].y * height)),cv.FONT_HERSHEY_SIMPLEX,fontScale,fontColor,thickness,cv.LINE_AA)

        #image =cv.putText(image,'Confidence Score:{0:.2f}%'.format(score),(p1[0],p1[1]+20),cv.FONT_HERSHEY_SIMPLEX,fontScale,color,thickness,cv.LINE_AA)
        return image
    
    def drawBirdEye(self, image, bounding, color):
        height, width, _ = self.frame.shape
        x1 = int( (bounding.normalized_vertices[2].x - (abs(bounding.normalized_vertices[2].x-bounding.normalized_vertices[3].x)/2)) * width)
        y1 = int((bounding.normalized_vertices[2].y ) * height)
        p = [x1, y1]
        p = self.getPerspectiveCoords(p)
        p2 = self.getPerspectiveCoords((self.punts_in[0][0],self.punts_in[0][1]))
        image = cv.circle(image, (int(p[0]), int(p[1])), 2, color, thickness=2)
        return image

    def calcDistancies(self,pedestrians):
        resta = abs(self.punts_out[3][0]-self.punts_out[2][0])
        res = []
        for p in pedestrians:
            x1 = int((p.bounding_poly.normalized_vertices[2].x - (abs(p.bounding_poly.normalized_vertices[2].x-p.bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
            y1 = int((p.bounding_poly.normalized_vertices[2].y) * self.frame.shape[0])
            c1 = self.getPerspectiveCoords((x1,y1))
            for p2 in pedestrians:
                x2 = int((p2.bounding_poly.normalized_vertices[2].x - (abs(p2.bounding_poly.normalized_vertices[2].x-p2.bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
                y2 = int((p2.bounding_poly.normalized_vertices[2].y ) * self.frame.shape[0])
                c2 = self.getPerspectiveCoords((x2,y2))
                if(c1[0]!=c2[0] and c1[1]!=c2[1]):
                    x = c1[0]-c2[0]
                    y = c1[1]-c2[1]
                    distanciaPixels = math.sqrt((x)**2 + (y)**2)
                    distanciaMetres = ((distanciaPixels * self.metres) / resta)
                    
                    if distanciaMetres < 2:
                        res.append([p,p2,distanciaMetres])
        return res

    def run(self):
        while True:
            # Llegim un nou frame
            ret,self.frame = self.cap.read()
            # Reescalem el frame
            self.resizeFrame(50)
            if self.perspectiveMatrix is None:
                self.perspectiveMatrix = cv.getPerspectiveTransform(self.punts_in,self.punts_out)
            
            # Buscar persones en el frame
            pedestrians = self.findPedestrians()
            
            # Disenyar el bird-eye
            be_width = int(self.punts_out[1][0]-self.punts_out[0][0])
            be_height = int(self.punts_out[2][1]-self.punts_out[0][1])
            # bird_eye = np.zeros((be_height, be_width, 3), dtype=np.uint8)
            bird_eye = cv.warpPerspective(self.frame, self.perspectiveMatrix, (self.frame.shape[1], self.frame.shape[0]), cv.INTER_CUBIC | cv.WARP_INVERSE_MAP)
            
            # for p in pedestrians:
            #     bird_eye = self.drawBirdEye(bird_eye, p.bounding_poly, GREEN)
            # Calcular distancies
            closeOnes = self.calcDistancies(pedestrians) 
            input_frame=self.frame.copy()
            for p in pedestrians:
                input_frame = self.drawBox(image=input_frame, bounding=p.bounding_poly, color=GREEN, caption='', score=0)
                bird_eye = self.drawBirdEye(bird_eye, p.bounding_poly, GREEN)
            for c in closeOnes:

                if c[2] < 1.5:
                    color=RED
                else:
                    color=ORANGE
                input_frame = self.drawBox(image=input_frame, bounding=c[0].bounding_poly, color=color, caption='', score=0)
                input_frame = self.drawBox(image=input_frame, bounding=c[1].bounding_poly, color=color, caption='', score=0)
                bird_eye = self.drawBirdEye(bird_eye, c[0].bounding_poly, color)
                bird_eye = self.drawBirdEye(bird_eye, c[1].bounding_poly, color)

                x1 = int((c[0].bounding_poly.normalized_vertices[2].x - (abs(c[0].bounding_poly.normalized_vertices[2].x-c[0].bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
                y1 = int((c[0].bounding_poly.normalized_vertices[2].y ) * self.frame.shape[0])

                x2 = int((c[1].bounding_poly.normalized_vertices[2].x - (abs(c[1].bounding_poly.normalized_vertices[2].x-c[1].bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
                y2 = int((c[1].bounding_poly.normalized_vertices[2].y ) * self.frame.shape[0])
                
                p1 = (x1,y1)
                p2 = (x2,y2)            
                bird_eye = cv.line(bird_eye, self.getPerspectiveCoords(p1), self.getPerspectiveCoords(p2), color, 1)

                x1 = int((c[0].bounding_poly.normalized_vertices[2].x - (abs(c[0].bounding_poly.normalized_vertices[2].x-c[0].bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
                y1 = int((c[0].bounding_poly.normalized_vertices[2].y - (abs(c[0].bounding_poly.normalized_vertices[2].y-c[0].bounding_poly.normalized_vertices[1].y)/2)) * self.frame.shape[0])
                
                x2 = int((c[1].bounding_poly.normalized_vertices[2].x - (abs(c[1].bounding_poly.normalized_vertices[2].x-c[1].bounding_poly.normalized_vertices[3].x)/2)) * self.frame.shape[1])
                y2 = int((c[1].bounding_poly.normalized_vertices[2].y - (abs(c[1].bounding_poly.normalized_vertices[2].y-c[1].bounding_poly.normalized_vertices[1].y)/2)) * self.frame.shape[0])
                
                p1 = (x1,y1)
                p2 = (x2,y2)
                input_frame = cv.line(input_frame, p1, p2, color, 1)
                center = (int((x1 + x2)/2), int((y1 + y2)/2))
                input_frame = cv.putText(input_frame, '{0:.2f}m'.format( c[2]), center, cv.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv.LINE_AA)
                

            # Requadrar [ i dibuixar linia entre els propers] les persones en diferents colors segons la distancia
            # Requadrar persones en el frame original
            # input_frame = self.frame.copy()
            # for p in pedestrians:
            #     input_frame = self.drawBox(image=input_frame, bounding=p.bounding_poly, color=ORANGE, caption='', score=0)

            cv.imshow('cov-distance',input_frame)
            cv.imshow('cov-distance: bird eye',bird_eye)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv.destroyAllWindows()

ORANGE = (0,127,255)
GREEN = (0,255,0)
RED = (0,0,255)

if __name__ == '__main__':
    # punts_in = np.float32([[1023, 268], [1504, 351], [261, 731], [961, 941]])
    # punts_out = np.float32([[1023, 268], [1511, 268], [1023, 1160], [1511, 1160]])
    # punts_in=np.float32([     [1475, 0],   [1813, 0], [0,943],    [761,1077]])            
    # punts_out = np.float32([  [1475, 0],   [1333, 0], [1475, 1200],[1813, 1200]])
    punts_in = np.float32([ [1165,171], [1614,222], [250,725], [984,900]])
    punts_out = np.float32([[1165, 171], [1165+451.887154, 171], [1165, 275+1069.645268], [1165+451.887154, 275+1069.645268]])
    
    # punts_out = np.float32([[],[],[],[]])
    cov = covDistance('TownCentreXVID_short.mp4',punts_in,punts_out)
    cov.run()
