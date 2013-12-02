__author__ = 'Chris'

from flask.ext.script import Manager
from flask import Flask, g
from os.path import expanduser
import os
import watch
import client
from sqlite3 import dbapi2 as sqlite3
import socket

#Where the client knows to look for the folder

serverURL = 'http://0.0.0.0:8080/'

fileApp = Flask(__name__, static_folder='static', static_url_path='/')

manager = Manager(fileApp)

finalUserName = ''

# Load default config and override config from an environment variable

def getUsername():
    return finalUserName


#TODO: can create a file directly in onedir -> check allowed extensions before uploading
#TODO: can handle uploads when file has a space in its name (server OR file string)
#TODO: try returning a blank string on server call (instead of successful download)
#TODO: change calls to fileUpload to client.fileUpload (import client)
#TODO: update file list for user after watchdog upload occurs -> auto-downloading

#Database stuff
fileApp.config.update(dict(
    DATABASE=expanduser("~/Dropbox/server/OneDir_accounts.db"),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
fileApp.config.from_object(__name__)

def getURL():
    return serverURL

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
#@return: returns the new string of files with the file added to put back in db
#use this method when you want to add a file to a user's associated files in the db
def clientDownloadOff(inputUserName):
    updateCurs = get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    fname = raw_input('Please enter the name of the file you would like to download.')
    if findFile(fileList, fname) == True:
        os.system('curl ' + client.getServerURL() + 'onedir/'+ fname + ' > ' + expanduser("~/onedir/") + fname)
    else:
        print "Sorry, you do not have permission to download this file."

@manager.command
def start():
    "Kick off the user command line interface."
    db = get_db()

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
        client.clientDownload(finalUserName)

        #Start watchdog
        observer = watch.Observer()
        event_handler = watch.MyEventHandler(finalUserName, client.getServerURL())
        observer.schedule(event_handler, path=expanduser("~/onedir"), recursive=True)

        #This creates a lock on the watchdog thread "observer", the Lock object created is called lock
        #when locked, the watchdog thread will be blocked until the lock is released
        #lock is intialized as unlocked
        lock = observer._lock
        observer.start()

    opt = 22

    while (opt != 0):
        if type == 'normal': #show file user options
            print '''
            FILE USER OPTIONS

            1) Share a file
            2) Change password
            3) Turn auto synch on or off

            These options are only necessary if auto synchronization is off.
            Autosynchronization is the default, and the program begins with autosynchronization ON.

            4) Upload a file manually
            5) Download a file manually
            '''
            opt = input("Please enter an option you want to do, or '0' to quit. ")

            while opt < 0 or opt > 6 or not isinstance(opt, int):
                opt = input("That is an invalid option, please re-try. ")

            if opt == 1:
                shareFile()
            if opt == 2:
                changePassword(finalUserName, db)

                #This option handles toggling the autosynchronization.
            if opt == 3:
                #This checks if the lock is already locked. The lock is initialized as unlocked.
                #If the observer thread is locked, then release the lock. This will allow auto synch to continue again.
                #And will unblock the observer thread.
                if lock.locked():
                    #If it gets to here. Then the observer thread was locked.
                    #This will release the lock on the observer thread, and the observer thread will start watching files again.
                    lock.release()
                    print 'Autosynch is now ON.'
                #If the lock is not locked, then autosynch was on and the user wants to turn auto synch off.
                #Thus, the lock must be acquired which will lock the lock and stop the observer thread
                    #until it is released (i.e the user turns it back on)
                else:
                    lock.acquire()
                    print 'Autosynch is now OFF. '

            #If autosynch is off, then the dowload/upload methods need to be given the names of the files to be downloaded/uploaded
            #upload prompts the user for a file name and then uses the same clientUpload() method used when autosync is on
            if opt == 4:
                fname = input("Please enter the file name.")
                client.clientUpload(fname, finalUserName)
            #The user is prompted for the file name within the clientDownloadOff() and it is used in that method for downloading the file.
            if opt == 5:
                clientDownloadOff(finalUserName)


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
            while opt < 0 or opt > 7 or not isinstance(opt, int):
                opt = input("That is an invalid option, please re-try. ")
            if opt == 1:
                deleteUser(db)
            if opt == 2:
                changePasswordAsAdmin(db)
            if opt == 3:
                changeSystem()
            if opt == 4:
                viewUserInfo(db)
            if opt == 5:
                viewFileSystem()
            if opt == 6:
                viewReportLog()
            if opt == 7:
                changePassword(finalUserName, db)

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


def changePassword(finalUserName, db):
    newPassword = raw_input("Please enter the new password you want to change to: ")
    db.cursor().execute('''UPDATE user_account SET password = ? WHERE username = (?) ''', (newPassword, finalUserName, ))
    db.commit()

def changeSynch():
    print "This is how you would change the autosynch settings"


def deleteUser(db):
    deletedUserName = raw_input("Please enter the username you want to delete: ")
    db.cursor().execute('''DELETE FROM user_account WHERE username = (?) ''', (deletedUserName,))
    db.commit()


def changePasswordAsAdmin(db):
    changedUserName = raw_input("Please enter the username whose password you want you change: ")
    newPassword = raw_input("Please enter the new password you want to change to: ")
    db.cursor().execute("UPDATE user_account SET password = (?) WHERE username = (?)", (newPassword, changedUserName, ))
    db.commit()


def changeSystem():
    print "This is how you would start or stop the system"


def viewUserInfo(db):
    userInfoName = raw_input("Please enter the username you want to view: ")
    cur = db.execute("SELECT username FROM user_account where username =?", (userInfoName,))
    cur1 = db.execute("SELECT password FROM user_account where username =?", (userInfoName,))
    cur2 = db.execute("SELECT files FROM user_account where username =?", (userInfoName,))
    type = cur.fetchone()[0]
    type1 = cur1.fetchone()[0]
    type2 = cur2.fetchone()[0]
    print 'username: ' + type
    print 'password: ' + type1
    viewFiles(type2)

def viewFileSystem():
    print "This is how you would view the file system"


def viewReportLog():
    print "This is how you would view a report log of system access"


def viewFiles(dbstring):
    print 'files: '
    fList = dbstring.split(';')
    for i in fList:
        print i


if __name__ == '__main__':
    manager.run()
