__author__ = 'marlenakauer'

from flask import Flask
import os
import main
from os.path import expanduser

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

#POST file to server
def clientUpload(filename):
    os.chdir(expanduser("~/onedir"))
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F' + g + ' ' + main.getServerURL())

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(filename):
    #check with database that user can download this file
    os.system('curl ' + main.getServerURL() + 'onedir/' + filename + ' > ~/onedir/' + filename )

if __name__ == '__main__':
    #clientUpload('inlab9.txt')
    clientDownload('hi4.txt')
