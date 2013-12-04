import os
from flask import Flask, request, g
from flask import send_from_directory
from werkzeug.utils import secure_filename
from os.path import expanduser


serverURL = 'http://0.0.0.0:8080/'

home = expanduser("~")
UPLOAD_FOLDER = home + '/onedirserver'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'cpp', 'h', 'java', 'doc'])

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getServerURL():
    """ client-side getter for server url """
    return serverURL

# save files uploaded to this route to UPLOAD_FOLDER
@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['filedata']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))


    return 'Upload Successful'

def deleteFile(filename):
    os.chdir(expanduser('~/onedir'))
    os.remove(filename)

  

# view files uploaded to UPLOAD_FOLDER
@fileApp.route('/onedir/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    fileApp.run(host='0.0.0.0', port=8080, debug=True) #TODO replace local server with a real app url -> Heroku?
