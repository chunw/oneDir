__author__ = 'marlenakauer'

from flask import Flask
import os
import server
import main
from os.path import expanduser

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

def clientUpload(filename):
    """ POST file to server """
    os.chdir(expanduser("~/onedir"))
    if server.allowed_file(filename):   # check file extension before uploading the file
        f = ' filedata=@'
        g = f + filename
        os.system('curl -F' + g + ' ' + main.getServerURL())


def clientDownload(filename):
    # TODO clean this method off
    os.system('curl ' + main.getServerURL() + 'onedir/' + filename + ' > ~/onedir/' + filename )

if __name__ == '__main__':
    print "I am a happy client!"