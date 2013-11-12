import os


import requests
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
#from flask.ext.script import Command, Manager
from werkzeug.utils import secure_filename
from os.path import expanduser
import requests

#fileManager = Manager(fileApp)

# Configs
fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#fileManager = Manager(fileApp)

@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
            return "File uploaded!\n"
    return "Welcome"

# View uploaded files
# TODO: display all files uploaded to server on one page instead of url routing.
@fileApp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    fileApp.run()           # debug=True

    #fileManager.run()
