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
from flask import Flask, render_template
import visio as v
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static','resources')

FRAME_FOLDER = os.path.join('static','resources/TownCentreXVID_frames')
OUTPUT_FOLDER = os.path.join('static','resources/output')
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

@app.route('/')
def hello():
	input_image = os.path.join(FRAME_FOLDER,'TownCentreXVID 01.jpg') # 'static/resources/input.jpg'
	nObjects= 0
	text="sdaa"
	output_image = os.path.join(OUTPUT_FOLDER,'TownCentreXVID 01.jpg') # 'static/resources/input.jpg'

	nObjects,text = v.localize_objects(input_image,output_image)
	"""Return a friendly HTTP greeting."""
	return render_template('index.html', inputimg = input_image,outputimg = output_image, numberObjects=nObjects, report=text)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]