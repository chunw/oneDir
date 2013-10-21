import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask.ext.script import Command, Manager
from werkzeug.utils import secure_filename
from os.path import expanduser
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

# Configs
fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#fileManager = Manager(fileApp)

def watch_file_changes():
    """ Start watchdog. """
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@fileApp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(fileApp.config['UPLOAD_FOLDER'], filename))
    return "File uploaded!\n"


# View uploaded files
# TODO: display all files uploaded to server on one page instead of url routing.
@fileApp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)

#fileManager.add_command('upload', Upload())

if __name__ == '__main__':
    fileApp.run() # debug=True
    watch_file_changes()
    # os.system("curl -X POST -F file=@hello/hello.txt \"http://localhost:5000/\"") # use curl upload file to flask server
    #fileManager.run()
