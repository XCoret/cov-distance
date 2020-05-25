from google.cloud import vision
from google.cloud.vision import types
import cv2 as cv
import numpy as np
import os


print('Visio Loaded...')

def drawBorders(image, bounding,color, caption='', score =0):
    height,width,_ = image.shape


    p1 = [int(bounding.normalized_vertices[0].x * width), int(bounding.normalized_vertices[0].y * height)]
    p2 = [int(bounding.normalized_vertices[2].x * width), int(bounding.normalized_vertices[2].y * height)]
    
    image = cv.rectangle(image,(p1[0],p1[1]),(p2[0],p2[1]),color,5)

    fontScale = 1
    thickness = 2
    fontColor = (0,0,0)
    image =cv.putText(image,caption+'{0:.2f}%'.format(score),(p1[0],p1[1]),cv.FONT_HERSHEY_SIMPLEX,fontScale,fontColor,thickness,cv.LINE_AA)

    #image =cv.putText(image,'Confidence Score:{0:.2f}%'.format(score),(p1[0],p1[1]+20),cv.FONT_HERSHEY_SIMPLEX,fontScale,color,thickness,cv.LINE_AA)
        
    return image

def getPersons(img):
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image(content = cv.imencode('.jpg',img)[1].tobytes())

    objects = client.object_localization(image=image).localized_object_annotations

    persons=[]
    for obj in objects:
        if obj.name ==  'Person':
            persons.append(obj)
    return persons


def localize_objects(path_in,path_out):
    client = vision.ImageAnnotatorClient()

    with open(path_in, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations
    
    print('Number of objects found: {}'.format(len(objects)))
    nObjects = 0
    text=''


    im = cv.imread(path_in)
    for object_ in objects:
        if object_.name == 'Person' :#and object_.score > 0.7:
            nObjects+=1            
            im = drawBorders(im, object_.bounding_poly, (0,127,255), caption=('Person: {}'.format(nObjects)), score =object_.score)

    cv.imwrite(path_out,im)

    return nObjects,text
