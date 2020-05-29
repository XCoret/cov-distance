'''Modul de visio'''
# Aquest es l'encarregat de realitzar la major part de les funcions de Visio de l'aplicacio


from google.cloud import vision
from google.cloud.vision import types
import cv2 as cv
import numpy as np
import os
import math

ORANGE = (0, 127, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

METRES = 5.4
''' 
---- CLOUD VISION ----

findPedestrians(frame, client) Cerca els vianants que apereixen en el frame rebut utilitzant l'API de CLOUD VISION

    parametres:    
        frame: frame de video (imatge) en el qual cercar els vianants
        client: objecte client de l'API de Cloud Vision (client = vision.ImageAnnotatorClient())
    
    retorna: 
        llistat de vianants trobats
'''
def findPedestrians(frame,client):
    height,width, _ = frame.shape
    # creem la imatge perque l'API de Cloud Vision la pugui processar
    image = vision.types.Image(content = cv.imencode('.jpg',frame)[1].tobytes())
    # Creem una variable objects on desarem tots els objectes que trobi l'API dins la imatge
    objects = client.object_localization(image = image).localized_object_annotations
    pedestrians = []
    for obj in objects:
        if obj.name == 'Person':
            # Filtrem els objectes per desar nomes els classificats com a persona
            pedestrians.append(obj)
    return pedestrians


''' 
getPerspectiveCoords(perspectiveMatrix, p) Calcula la correspondencia de coordenades del frame original a la homografia

    parametres:    
        perspectiveMatrix: matriu amb la qual s'ha realitzat la homografia
        p: punt a calcular p=(x,y)
    
    retorna: 
        les coordenades en la homografia
'''
def getPerspectiveCoords(perspectiveMatrix, p):
    px = (perspectiveMatrix[0][0]*p[0] + perspectiveMatrix[0][1]*p[1] + perspectiveMatrix[0][2]) / ((perspectiveMatrix[2][0]*p[0] + perspectiveMatrix[2][1]*p[1] + perspectiveMatrix[2][2]))
    py = (perspectiveMatrix[1][0]*p[0] + perspectiveMatrix[1][1]*p[1] + perspectiveMatrix[1][2]) / ((perspectiveMatrix[2][0]*p[0] + perspectiveMatrix[2][1]*p[1] + perspectiveMatrix[2][2]))
    return int(px),int(py)   


''' 
calcDistances(frame,pedestrians,perspectiveMatrix,punts_in,punts_out) Calcula la distancia entre els vianants i retorna la llista de parelles de vianants que estan mes a prop i la seva distancia

    parametres:    
        frame: frame de video (imatge) en el qual cercar els vianants
        pedestrians: llistat de tots els vianants reconeguts
        perspectiveMatrix: matriu amb la qual s'ha realitzat la homografia
        punts_in: punts d'entrada utilitzats per realitzar la homografia
        punts_out: punts de sortida utilitzats per realitzar la homografia
    
    retorna: 
        llistat de parelles de vianants propers
'''
def calcDistances(frame,pedestrians,perspectiveMatrix,punts_in,punts_out):
    resta = abs(punts_out[3][0]-punts_out[2][0])
    res = []
    for p in pedestrians:
        x1 = int((p.bounding_poly.normalized_vertices[2].x - (abs(p.bounding_poly.normalized_vertices[2].x-p.bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
        y1 = int((p.bounding_poly.normalized_vertices[2].y) * frame.shape[0])
        c1 = getPerspectiveCoords(perspectiveMatrix,(x1,y1))
        for p2 in pedestrians:
            x2 = int((p2.bounding_poly.normalized_vertices[2].x - (abs(p2.bounding_poly.normalized_vertices[2].x-p2.bounding_poly.normalized_vertices[3].x)/2)) * frame.shape[1])
            y2 = int((p2.bounding_poly.normalized_vertices[2].y ) * frame.shape[0])
            c2 = getPerspectiveCoords(perspectiveMatrix,(x2, y2))
            if(c1[0]!=c2[0] and c1[1]!=c2[1]):
                
                x = c1[0]-c2[0]
                y = c1[1]-c2[1]
                distanciaPixels = math.sqrt((x)**2 + (y)**2)
                if distanciaPixels > 15:
                    distanciaMetres = ((distanciaPixels * METRES) / resta) 
                    if distanciaMetres < 2:
                        res.append([p,p2,distanciaMetres])
    return res


''' 
drawBox(image, bounding, color, caption='', score =0) Dibuixa sobre la imatge rebuda un rectangle del color rebut a partir dels limits (bounding) rebuts

    parametres:    
        image: frame de video (imatge) en el qual cercar els vianants
        bounding: limits del rectangle a dibuixar (pertanyen a un vianant)
        color: color del rectangle a dibuixar

        caption: text a escriure sobre el rectangle (no el fem servir en la versio final)
        score: numero per determinar el percentatge d'encert que el rectangle sigui un vianant (no el fem servir en la versio final)
    
    retorna: 
        imatge amb el marcatge realitzat
'''
def drawBox(image, bounding, color, caption='', score =0):
    height,width,_ = image.shape
    p1 = [int(bounding.normalized_vertices[0].x * width), int(bounding.normalized_vertices[0].y * height)]
    p2 = [int(bounding.normalized_vertices[2].x * width), int(bounding.normalized_vertices[2].y * height)]
    
    image = cv.rectangle(image,(p1[0],p1[1]),(p2[0],p2[1]),color,3)

    fontScale = 0.5
    thickness = 3
    fontColor = (0,0,0)
    if score!=0:
        image = cv.putText(image,caption+'{0:.2f}m'.format(score),(int((bounding.normalized_vertices[0].x -((bounding.normalized_vertices[1].x-bounding.normalized_vertices[0].x)/2) )* width), int(bounding.normalized_vertices[0].y * height)),cv.FONT_HERSHEY_SIMPLEX,fontScale,fontColor,thickness,cv.LINE_AA)

    #image =cv.putText(image,'Confidence Score:{0:.2f}%'.format(score),(p1[0],p1[1]+20),cv.FONT_HERSHEY_SIMPLEX,fontScale,color,thickness,cv.LINE_AA)
    return image


''' 
drawBirdEye(image, bounding, color, punts_in, punts_out, perspectiveMatrix) Dibuixa sobre la imatge rebuda (homogragia) un cercle del color rebut a partir dels limits (bounding) rebuts

    parametres:    
        image: frame de video (imatge) en el qual cercar els vianants
        bounding: limits del rectangle a dibuixar (pertanyen a un vianant)
        color: color del rectangle a dibuixar
        punts_in: punts d'entrada utilitzats per realitzar la homografia
        punts_out: punts de sortida utilitzats per realitzar la homografia
        perspectiveMatrix: matriu amb la qual s'ha realitzat la homografia
    
    retorna: 
        imatge amb el marcatge realitzat
'''
def drawBirdEye(image, bounding, color, punts_in, punts_out, perspectiveMatrix):
    height, width, _ = image.shape
    x1 = int((bounding.normalized_vertices[2].x - (abs( bounding.normalized_vertices[2].x-bounding.normalized_vertices[3].x)/2)) * width)
    y1 = int((bounding.normalized_vertices[2].y) * height)
    p = [x1, y1]
    p = getPerspectiveCoords(perspectiveMatrix,p)
    p2 = getPerspectiveCoords(perspectiveMatrix, (punts_in[0][0], punts_in[0][1]))
    image = cv.circle(image, (int(p[0]), int(p[1])), 4, color, thickness=2)
    return image
