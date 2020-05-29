'''Modul de control'''
# Aquest es modul principal de l'aplicacio.
# Realitza les crides al modufl de Visio (visio.py) i al modul de Video (camara.py)
# Serveix la pagina web utilitzant tecnologia Flask


import os
from flask import Flask, render_template, Response
from camara import VideoCamera
import cv2 as cv
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
os.environ['GCP_BUCKET_NAME'] = 'cov-distance-bucket'


app = Flask(__name__)
# Es la funcio que es crida en entrar a la web
@app.route('/')
def index():
    return render_template('index.html')

''' gen(cam,i) Executa el bucle que mentre duri el video anira retornant un de cada 10 frames que el formen.

    parametres: 
        cam: Objecte camera per poder accedir al video
        i: index del frame que es vol que retorni
    
    retorna: 
        retorna el frame original amb les persones i les distancies marcades o el frame de la homografia depenent si i es 0 o 1 respectivament
'''
def gen(cam,i):
    iterador = 0;
    while True:
        if iterador %10==0:
            frame = cam.get_frame()[i]

            frame = cv.imencode('.jpg',frame)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')
   

''' video_feed() Crida a gen() i rep el frame original tractat com a resposta
    
    retorna: 
        la resposta s'envia al HTML i es mostrara en el tag que tingui la variable {{video_feed}}
'''
@app.route('/video_feed')
def video_feed():
    video_path = get_blob('TownCentreXVID_short.mp4')
    return Response(gen(VideoCamera(video_path), 0), mimetype='multipart/x-mixed-replace; boundary=frame')


''' out_feed() Crida a gen() i rep el frame de la homografia com a resposta
    
    retorna: 
        la resposta s'envia al HTML i es mostrara en el tag que tingui la variable {{out_feed}}
'''
@app.route('/out_feed')
def out_feed():
    video_path = get_blob('TownCentreXVID_short.mp4')
    return Response(gen(VideoCamera(video_path), 1), mimetype='multipart/x-mixed-replace; boundary=frame')


''' 
---- CLOUD STORAGE ----

get_blob(source_blob) Cerca si existeix cap fitxer amb el nom passat per parametre en emmagatzematge local, en cas que no hi sigui el descarrega de Cloud Storage
                         finalment retorna la seva direccio (path)

    parametres:    
        source_blob: nom del fitxer a tractar
    
    retorna: 
        retorna path del fitxer demanat
'''
def get_blob(source_blob):
    mediaDir = 'static/resources'
    if not source_blob in os.listdir(mediaDir):
        dest_file_name = '{}/{}'.format(mediaDir,source_blob)
        # Definim el bucket (deposit) del nostre Cloud Storage
        bucket_name = os.environ.get('GCP_BUCKET_NAME')
        # Definim nostre client de Cloud Storage 
        storage_client = storage.Client()
        # cerquem el fitxer a Cloud Storage
        blobs = storage_client.list_blobs(bucket_name)
        for blob in blobs:
            if blob.name == source_blob:
                # Descarreguem el fitxer
                blob.download_to_filename(dest_file_name)
    else:
        dest_file_name = '{}/{}'.format(mediaDir,source_blob)
    print(dest_file_name)

    return dest_file_name


''' main:  Executa l'aplicacio en cas que s'executi en local
        Serveix l'aplicacien la url localhost ( 127.0.0.1:8080 )
'''
if __name__ == '__main__':
    app.run(host='127.0.0.1',port = '8080', debug = True)
