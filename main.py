# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
from flask import Flask, render_template, Response
import visio as v
import os
from camara import Camara

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static','resources')

#FRAME_FOLDER = os.path.join('static','resources/TownCentreXVID_frames')
#OUTPUT_FOLDER = os.path.join('static','resources/output')

FRAME_FOLDER = 'static/resources/TownCentreXVID_frames/'
OUTPUT_FOLDER = 'static/resources/output/'
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

input_image = FRAME_FOLDER+'TownCentreXVID 01.jpg' # 'static/resources/input.jpg'

output_image = OUTPUT_FOLDER+'TownCentreXVID 01.jpg' # 'static/resources/input.jpg'

nObjects= 0
text="sdaa"

@app.route('/')
def index():
	"""Return a friendly HTTP greeting."""
	return render_template('index.html', inputimg = input_image,outputimg = output_image, numberObjects=nObjects, report=text)
    
def gen(cam,i):
    while True:
        frame = cam.get_frame()[i]
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camara(),0),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/homografia_feed')
def homografia_feed():
    return Response(gen(Camara(),1),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]