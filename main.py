__author__ = 'Chris'

from flask.ext.script import Manager
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, g
from os.path import expanduser
import os
import watch

#Where he client knows to look for the folder
serverURL = 'http://172.25.179.70:8080/'  #TODO replace local server with a real app url -> Heroku?

fileApp = Flask(__name__, static_folder='static', static_url_path='/')

manager = Manager(fileApp)

# Load default config and override config from an environment variable
#TODO: This needs to be on the server
fileApp.config.update(dict(
    #DATABASE='/home/christopher/Dropbox/Public/CS3240/oneDir-group14/OneDir_accounts.db',
    DATABASE='/Users/chunwang1/oneDir-group14/OneDir_accounts.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
fileApp.config.from_object(__name__)


#DATABASE COMMANDS
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
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@fileApp.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#TODO: can create a file directly in onedir -> check allowed extensions before uploading
#TODO: can handle uploads when file has a space in its name (server OR file string)
#TODO: try returning a blank string on server call (instead of successful download)
#TODO: change calls to fileUpload to client.fileUpload (import client)
#TODO: update file list for user after watchdog upload occurs -> auto-downloading
#TODO: maybe move the .db file over to server.py?

#@param: database string of files, and file to find
#@return: returns a boolean value based on whether or not the user has this file
#use this method to verify if user can view a file, sharing, etc
def findFile(dbstring, fname):
    fList = dbstring.split(';')
    for i in fList:
        if i == fname:
            return True
        else:
            return False

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

#@param: database string of files
#@return: return the new string of files as a parseable list
def parseList(dbstring):
    return dbstring.split(';')


#@param: database string of files, and file to remove
#@return: returns the new string of files with the file added to put back in db
#use this method when you want to add a file to a user's associated files in the db
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

#POST file to server
def clientUpload(filename, inputUserName):
    os.chdir(expanduser("~/onedir"))
    f = ' filedata=@'
    g = f + filename
    os.system('curl -F' + g + ' ' + serverURL)

    #Update the file list for that user
    updateCurs = get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    if fileList is None and not filename.contains('~'):
        fileList = filename + ';'
    elif not filename in fileList:
        fileList += filename +';'
    get_db().execute("UPDATE user_account SET files =? WHERE username =?", (fileList, inputUserName,))
    get_db().commit()


#pass in username as well so that the DB can verify the user can make this request
def clientDownload(inputUserName):
    #Update the files listed for user
    updateCurs = get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    if fileList is not None:
        fileList = parseList(fileList)
        for filename in fileList:
            os.system('curl ' + serverURL + 'onedir/'+ filename + ' > ' + expanduser("~/onedir/") + filename)


def getServerURL():
    """ client-side getter for server url """
    return serverURL


@manager.command
def start():
    "Kick off the user command line interface."
    db = get_db()
    finalUserName = ''

    inputNew = raw_input("Are you a new user? y/n ")

    if inputNew == 'Y' or inputNew == 'y' or inputNew == 'yes' or inputNew == 'Yes':
        newUserName = raw_input("Please enter the user name you would like. ")
        newPassword = raw_input("Please enter the password you would like. ")
        createNewAccount(newUserName, newPassword, db)
        finalUserName = newUserName

    else:
        inputUserName = raw_input("Please enter your existing username: ")
        inputPassword = raw_input("Password: ")

        cur = db.execute("SELECT username FROM user_account where username =?", (inputUserName,))
        cur2 = db.execute("SELECT password FROM user_account where password =? and username =?",
                          (inputPassword, inputUserName))

        entries = cur.fetchall()
        entries2 = cur2.fetchall()
        if (len(entries) == 0 or len(entries2) == 0):
            print "Invalid login, please re-run the program to log in."
            exit(0)
        else:
            finalUserName = inputUserName

    #When starting up the user commands, create the onedir folder if it doesn't already exist
    if not os.path.exists(expanduser("~/onedir")):
        os.makedirs(expanduser("~/onedir"))

    #Get user type (file or admin)
    cur = db.execute("SELECT user_type FROM user_account where username =?", (finalUserName,))
    type = cur.fetchone()[0]


    #Before beginning, update your files to the server (local copies override server copies)
    if type == 'normal':
        clientDownload(finalUserName)

        #Start watchdog
        observer = watch.Observer()
        event_handler = watch.MyEventHandler(finalUserName, serverURL)
        observer.schedule(event_handler, path=expanduser("~/onedir"), recursive=True)
        observer.start()

    opt = 22

    while (opt != 0):
        if type == 'normal': #show file user options
            print '''
            FILE USER OPTIONS

            1) Share a file
            2) Change password
            3) Turn auto synch on or off
            '''
            opt = input("Please enter an option you want to do, or '0' to quit. ")
            while opt < 0 or opt > 3 or not isinstance(opt, int):
                opt = input("That is an invalid option, please re-try. ")
            if opt == 1:
                shareFile()
            if opt == 2:
                changePassword()
            if opt == 3:
                changeSynch()

        elif type == 'admin': #show admin user options
            print '''
            ADMIN OPTIONS

            1) Delete user
            2) Change a user's password
            3) Start or stop file system
            4) See user information
            5) Get file system information
            6) View traffic report log
            7) Change your password
            '''
            opt = input("Please enter an option you want to do, or '0' to quit. ")
            while opt < 0 or opt > 6 or not isinstance(opt, int):
                opt = input("That is an invalid option, please re-try. ")
            if opt == 1:
                deleteUser()
            if opt == 2:
                changePasswordAsAdmin()
            if opt == 3:
                changeSystem()
            if opt == 4:
                viewUserInfo()
            if opt == 5:
                viewFileSystem()
            if opt == 6:
                viewReportLog()
            if opt == 7:
                changePassword()

    #Stop watching files
    if type == 'normal':
        observer.stop()
        observer.join()


def createNewAccount(newUserName, newPassword, db):
    db.cursor().execute('''INSERT INTO user_account (username, password, user_type)
        VALUES (?, ?, 'normal')''', (newUserName, newPassword))
    db.commit()


def shareFile():
    print "This is how you would share files"
    filename = raw_input("Which file to share? >> ").strip()
    if not os.path.isfile(expanduser("~") + "/onedir/" + filename):
        print "Oops, file does not exist."
        return
    username = raw_input("Who to share with? >> ").strip()
    cur = get_db().execute("SELECT username FROM user_account where username =?", (username,))
    entries = cur.fetchall()
    if len(entries) == 0:
        print "Oops, user does not exist."
        return

    # NOTE: the other user need to restart the onedir program to see this file.
    # If the filename has existed in that user's onedir, this method will overwrite it.
    #filelist = ""
    cur2 = get_db().execute("SELECT files FROM user_account where username =?", (username,))
    filelist = cur2.fetchone()[0]
    get_db().execute("UPDATE user_account SET files='" + addFile(filelist, filename) + "' WHERE username='" + username + "'")
    get_db().commit()
    print("File sent to " + username + "!")


def changePassword():
    print "This is how you would change your password"


def changeSynch():
    print "This is how you would change the autosynch settings"


def deleteUser():
    print "This is how you would delete a user"


def changePasswordAsAdmin():
    print "This is how the admin user would change a user's password"


def changeSystem():
    print "This is how you would start or stop the system"


def viewUserInfo():
    print "This is how you would view current user information"


def viewFileSystem():
    print "This is how you would view the file system"


def viewReportLog():
    print "This is how you would view a report log of system access"


if __name__ == '__main__':
    manager.run()
