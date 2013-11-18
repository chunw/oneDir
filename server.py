import os
from flask import Flask, request
from flask import send_from_directory
from werkzeug.utils import secure_filename
from os.path import expanduser

home = expanduser("~")
UPLOAD_FOLDER = home + '/onedir'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'cpp', 'h', 'java', 'doc'])

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# save files uploaded to this route to UPLOAD_FOLDER
@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['filedata']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
            # let client know about this update


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
     '''

# view files uploaded to UPLOAD_FOLDER
@fileApp.route('/onedir/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    fileApp.run(host='0.0.0.0', port=8080, debug=True)
