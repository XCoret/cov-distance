import os
from flask import Flask, render_template, Response
from camara import VideoCamera
import cv2 as cv
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
os.environ['GCP_BUCKET_NAME'] = 'cov-distance-bucket'


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',message = "Hello Flask!")

def gen(cam,i):
    while True:
        frame = cam.get_frame()[i]

        frame = cv.imencode('.jpg',frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')
   

@app.route('/video_feed')
def video_feed():
    video_path = get_blob('TownCentreXVID_short.mp4')
    # video_path = storage.child('{}/{}'.format(os.environ.get('GCP_BUCKET_NAME'),'TownCentreXVID_short.mp4'))
    return Response(gen(VideoCamera(video_path), 0), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/out_feed')
def out_feed():
    video_path = get_blob('TownCentreXVID_short.mp4')
    return Response(gen(VideoCamera(video_path), 1), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_blob(source_blob):
    mediaDir = 'static/resources'
    if not source_blob in os.listdir(mediaDir):
        dest_file_name = '{}/{}'.format(mediaDir,source_blob)

        bucket_name = os.environ.get('GCP_BUCKET_NAME')
        storage_client = storage.Client()

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = storage_client.list_blobs(bucket_name)
        for blob in blobs:
            if blob.name == source_blob:
                blob.download_to_filename(dest_file_name)
    else:
        dest_file_name = '{}/{}'.format(mediaDir,source_blob)
    print(dest_file_name)

    return dest_file_name

if __name__ == '__main__':
    app.run(host='127.0.0.1',port = '8080', debug = True)
