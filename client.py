__author__ = 'marlenakauer'

from flask import Flask
from flask import send_from_directory
from os.path import expanduser
import os


fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
serverURL = 'http://172.25.107.209:8080/'
#POST file to server
def clientUpload(filename):
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F'+g +' http://172.25.107.209:8080/')

#create method on client side that will create uploads or onedir folder if none exists

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(filename):
    #check with database that user can download this file
    os.system('curl ' + serverURL + 'uploads/'+ filename + ' > ~/uploads/' + filename )

if __name__ == '__main__':
    clientUpload('blah.txt')
    clientDownload('db.py')
