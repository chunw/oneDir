import os
from flask import Flask, request, g
from flask import send_from_directory
from werkzeug.utils import secure_filename
from os.path import expanduser
from sqlite3 import dbapi2 as sqlite3
import socket

home = expanduser("~")
UPLOAD_FOLDER = home + '/onedir'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'cpp', 'h', 'java', 'doc'])

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
fileApp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Database stuff
fileApp.config.update(dict(
    DATABASE='/home/christopher/Dropbox/Public/CS3240/oneDir-group14/OneDir_accounts.db',
    #DATABASE='/Users/chunwang1/oneDir-group14/OneDir_accounts.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
fileApp.config.from_object(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(fileApp.config['DATABASE'])
    rv.text_factory = str
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    app = Flask(__name__)
    with app.app_context():
        if not hasattr(g, 'sqlite_db'):
            g.sqlite_db = connect_db()
        return g.sqlite_db


@fileApp.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def update_db(filename, username, op):
        """ update filelist for client in database """
        app = Flask(__name__)
        with app.app_context():
            db = get_db()
            cur2 = db.execute("SELECT files FROM user_account where username =?", (username,))
            filelist = cur2.fetchone()[0]
            if op == 'add':
                db.execute("UPDATE user_account SET files='" + addFile(filelist, filename) + "' WHERE username='" + username + "'")

            if op == 'del':
                db.execute("UPDATE user_account SET files='" + removeFile(filelist, filename) + "' WHERE username='" + username + "'")

            db.commit()
            return

def addFile(dbstring, fname):
    if dbstring is None:
        dbstring = ""
    fList = dbstring.split(';')
    if fname in fList: # if the filename already exists, do nothing
        return dbstring
    else:
        fList.append(fname)
        newList = []
        for i in fList:
            x = i + ';'
            newList.append(x)
        newString = ''.join(newList)
        return newString

#@param: database string of files, and file to remove
#@return: returns the new string of files with the file removed to put back in db
#use this method when you want to remove a file from a user's associated files in the db
def removeFile(dbstring, fname):
    fList = dbstring.split(';')
    if not fname in fList:  # if filename is not in filelist, do nothing
        return dbstring
    else:
        fList.remove(fname)
        newList = []
        for i in fList:
            x =  i + ';'
            newList.append(x)
        newString = ''.join(newList)
        return newString


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


    return 'Upload Successful'
  

# view files uploaded to UPLOAD_FOLDER
@fileApp.route('/onedir/<filename>')
def uploaded_files(filename):
    return send_from_directory(fileApp.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    fileApp.run(host='0.0.0.0', port=8080, debug=True) #TODO replace local server with a real app url -> Heroku?
