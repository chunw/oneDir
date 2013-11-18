__author__ = 'marlenakauer'

from flask import Flask
import os
from os.path import expanduser


fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')
SERVER_URL = 'http://172.25.203.58:8080/'

#POST file to server
def clientUpload(filename):
    os.chdir(expanduser("~/onedir"))
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F'+ g +' http://172.25.203.58:8080/')

#create method on client side that will create uploads or onedir folder if none exists

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(filename):
    #check with database that user can download this file
    os.system('curl ' + SERVER_URL + 'onedir/' + filename + ' > ~/onedir/' + filename )

if __name__ == '__main__':
    #clientUpload('inlab9.txt')
    clientDownload('hi4.txt')
