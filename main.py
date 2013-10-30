import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask.ext.script import Command, Manager
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
    #os.system("curl -X POST -F file=@hello.txt \"http://localhost:5000/\"") # use curl upload file to flask server
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
            return "File uploaded!\n"
    return "Welcome"

# This method will share the file by changing 
def share_file(string filename):
    os.system("curl --user  GET -F file=filename \"http://localhost:5000/\"")
    os.system("chmod u+rwx filename")
    
    
    
# View uploaded files
# TODO: display all files uploaded to server on one page instead of url routing.
@fileApp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)

#fileManager.add_command('upload', Upload())

if __name__ == '__main__':
    fileApp.run() # debug=True

        #to verify the username and password when trying to upload or access a file simply
        #add "--user name: password http://localhost:5000/"
       #this command will upload the file "hello.txt" to the server. 
       #adding this would make sharing easier
    
    #fileManager.run()
