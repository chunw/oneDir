__author__ = 'Chris'

from flask.ext.script import Manager, prompt_bool
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

fileApp = Flask(__name__, static_folder='static', static_url_path='/')

manager = Manager(fileApp)

# Load default config and override config from an environment variable
fileApp.config.update(dict(
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


@manager.command
def start():
    "Kick off the user command line interface."
    db = get_db()

    inputNew = raw_input("Are you a new user? y/n ")

    if (inputNew == 'Y' or inputNew == 'y'):
        createNewAccount()

    else:
        inputUserName = raw_input("Username: ")
        inputPassword = raw_input("Password: ")

        cur = db.execute("SELECT username FROM user_account where username =?", (inputUserName,))
        cur2 = db.execute("SELECT password FROM user_account where password =? and username =?", (inputPassword, inputUserName))

        entries = cur.fetchall()
        entries2 = cur2.fetchall()
        if (len(entries) == 0 or len(entries2) == 0):
            print "Invalid login, please re-run the program to log in."
            exit(0)

    opt = 22

    while (opt != 0):
        #if (user type == file user)
        print '''
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

        #else if (user type == admin user)
        print '''
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


def createNewAccount():
    db = get_db()
    newUserName = raw_input("Please enter the user name you would like. ")
    newPassword = raw_input("Please enter the password you would like. ")
    db.cursor().execute('''INSERT INTO user_account (username, password, user_type, files)
         VALUES (?, ?, ?, ?)''', (newUserName, newPassword, 'normal', None))
    db.commit()



def shareFile():
    print "This is how you would share files"


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
