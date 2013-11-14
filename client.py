from flask import Flask,request
import os
from flask import send_from_directory
from os.path import expanduser

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
    return "Welcome to OneDir-group14"

@fileApp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    os.system("curl -X POST file=@db.py http://1455d817.ngrok.com")