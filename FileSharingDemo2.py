__author__ = 'Christopher Smith (cts2bu)'
__date__ = '18 October 2013'

import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask.ext.script import Command, Manager
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/christopher/Uploads'
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
            #return redirect(url_for('uploaded_file', filename=filename))
            #return redirect(url_for('uploaded_file'))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
     '''

#View uploaded files
@fileApp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)

#fileManager.add_command('upload', Upload())

if __name__ == '__main__':
    fileApp.run(debug=True)
    #fileManager.run()