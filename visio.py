import argparse
import io
import os
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

def drawBorders(image, bounding,color, caption='', score =0):
    width,height = image.size
    draw = ImageDraw(image)
    draw.polygon([
        bounding.normalized_vertices[0].x * width,
        bounding.normalized_vertices[0].y * height,
        bounding.normalized_vertices[1].x * width,
        bounding.normalized_vertices[1].y * height,
        bounding.normalized_vertices[2].x * width,
        bounding.normalized_vertices[2].y * height,
        bounding.normalized_vertices[3].x * width,
        bounding.normalized_vertices[3].y * height], fill=None, outline=color)
    font_size = 12

    draw.text((
        bounding.normalized_vertices[0].x * width,
        bounding.normalized_vertices[0].y * height), text=caption,fill=color)

    draw.text((bounding.normalized_vertices[0].x*width,
                bounding.normalized_vertices[0].y*height +20), text='Confidence Score:{0:.2f}%'.format(score),fill=color)
    
    return image

def localize_objects(path):
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations
    vects = []
    print('Number of objects found: {}'.format(len(objects)))
    nObjects = 0
    text=''
    vects = []


    
    for object_ in objects:
        if object_.name == 'Person':
            nObjects+=1
            person=[]
            #print('\n{} (confidence: {})'.format(object_.name, object_.score))
            
            for vertex in object_.bounding_poly.normalized_vertices:
                person.append([vertex.x, vertex.y])
                text+=' - ({}, {})'.format(vertex.x, vertex.y)
            vects.append(person)

    drawBorders(image, bounding,color, caption='', score =0):


    return nObjects,text

