__author__ = 'marlenakauer'

from flask import Flask
import os
import main
from os.path import expanduser
import server

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

serverURL = 'http://0.0.0.0:8080/'

def getServerURL():
    """ client-side getter for server url """
    return serverURL

#POST file to server
def clientUpload(filename, inputUserName):
    os.chdir(expanduser("~/onedir"))
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F' + g + ' ' + serverURL)

    #Update the file list for that user
    updateCurs = server.get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    if fileList is None and not filename.contains('~'):
        fileList = filename + ';'
    elif not filename in fileList:
        fileList += filename +';'
    server.get_db().execute("UPDATE user_account SET files =? WHERE username =?", (fileList, inputUserName,))
    server.get_db().commit()

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(inputUserName):
    #Update the files listed for user
    updateCurs = server.get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    if fileList is not None:
        fileList = server.parseList(fileList)
        for filename in fileList:
            if filename is not '': #TODO: make it so the actual parser works better (no semicolon at beginning)
                os.system('curl ' + serverURL + 'onedir/'+ filename + ' > ' + expanduser("~/onedir/") + filename)

#pass in username as well so that the DB can verify the user can make this request
def clientDownload(filename):
    #check with database that user can download this file
    os.system('curl ' + serverURL + 'onedir/' + filename + ' > ~/onedir/' + filename )

if __name__ == '__main__':
    #clientUpload('inlab9.txt')
    clientDownload('hi4.txt')
