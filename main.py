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

# [START gae_python37_app]
from flask import Flask
from flask import render_template
import os
import visio as v


IMAGE_FOLDER = os.path.join('static','resources')

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

@app.route('/')
def hello():
    
    input_image = os.path.join(os.path.join('static','resources'),'input.jpg') # 'static/resources/input.jpg'
    nObjects= 0
    text=''
    nObjects,text = v.localize_objects(os.path.join(os.path.join('static','resources'),'input.jpg'))
    
    output_image = os.path.join(os.path.join('static','resources'),'output.jpg')

    """Return a friendly HTTP greeting."""
    return render_template('index.html', inputimg = input_image,outputimg = output_image, numberObjects=nObjects, report=text)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
