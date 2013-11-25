__author__ = 'Chris'

from flask.ext.script import Manager
from flask import Flask
from os.path import expanduser
import os
import watch
import server
import client

#Where he client knows to look for the folder

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


#@param: database string of files
#@return: return the new string of files as a parseable list
def parseList(dbstring):
    return dbstring.split(';')


#@param: database string of files, and file to remove
#@return: returns the new string of files with the file added to put back in db
#use this method when you want to add a file to a user's associated files in the db
def clientDownloadOff(inputUserName):
    updateCurs = server.get_db().execute("SELECT files FROM user_account where username =?", (inputUserName,))
    fileList = updateCurs.fetchone()[0]
    fname = raw_input('Please enter the name of the file you would like to download.')
    if findFile(fileList, fname) == True:
        os.system('curl ' + client.getServerURL() + 'onedir/'+ fname + ' > ' + expanduser("~/onedir/") + fname)
    else:
        print "Sorry, you do not have permission to download this file."

@manager.command
def start():
    "Kick off the user command line interface."
    db = server.get_db()

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
        observer.start()

    opt = 22
    autosync = True
    while (opt != 0):
        if type == 'normal': #show file user options
            print '''
            FILE USER OPTIONS

            1) Share a file
            2) Change password
            3) Turn auto synch on or off
            '''
            opt = input("Please enter an option you want to do, or '0' to quit. ")

            while opt < 0 or opt > 4 or not isinstance(opt, int):
                opt = input("That is an invalid option, please re-try. ")

            if opt == 1 and autosync is True:
                shareFile()
            if opt == 2 and autosync is True:
                changePassword(finalUserName, db)
            if opt == 3 and autosync is True:
                autosync = False
                observer.stop()

                print '''
                   FILE USER OPTIONS

                1) Share a file
                2) Change password
                3) Turn auto sync on
                4) Upload a file
                5) Download a file

                Entering 0 will still exit the program

                '''
                optOff = input("Please enter an option you want to do or '0' to quit.")

                if optOff == 1:
                    shareFile()

                if optOff == 2:
                    changePassword(finalUserName, db)

                if optOff == 3:
                    autosync = True
                    # TODO
                    # observer.start()


                if optOff == 4:
                    fname = input("Please enter the file name.")
                    client.clientUpload(fname, finalUserName)

                if optOff == 5:
                    clientDownloadOff(finalUserName)

                if optOff == 0:
                    opt = 0

                else:
                    print "You have entered an invalid option."

    #end of autosync code


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
    cur = server.get_db().execute("SELECT username FROM user_account where username =?", (username,))
    entries = cur.fetchall()
    if len(entries) == 0:
        print "Oops, user does not exist."
        return

    # NOTE: the other user need to restart the onedir program to see this file.
    # If the filename has existed in that user's onedir, this method will overwrite it.
    #filelist = ""
    cur2 = server.get_db().execute("SELECT files FROM user_account where username =?", (username,))
    filelist = cur2.fetchone()[0]
    server.get_db().execute("UPDATE user_account SET files='" + server.addFile(filelist, filename) + "' WHERE username='" + username + "'")
    server.get_db().commit()
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