import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask.ext.script import Command, Manager
from werkzeug.utils import secure_filename
from os.path import expanduser

home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'cpp', 'h', 'java', 'doc'])

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#fileManager = Manager(fileApp)

#Helper - see if file is allowed
def allowed_file(filename):
   return '.' in filename and \
   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
    return "File uploaded!\n"


#View uploaded files
@fileApp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)

#fileManager.add_command('upload', Upload())

if __name__ == '__main__':
    fileApp.run() # debug=True
    os.system("curl -X POST -F file=@hello.txt \"http://localhost:5000/\"") # use curl upload file to flask server
    #fileManager.run()
