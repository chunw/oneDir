__author__ = 'marlenakauer'

from flask import Flask
import os


fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
SERVER_URL = 'http://172.25.107.209:8080/'

#POST file to server
def clientUpload(filename):
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F' + g + ' ' + SERVER_URL)

#create method on client side that will create uploads or onedir folder if none exists

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(filename):
    #check with database that user can download this file
    os.system('curl ' + SERVER_URL + 'uploads/' + filename + ' > ~/uploads/' + filename )

if __name__ == '__main__':
    clientUpload('blah.txt')
    clientDownload('db.py')
