__author__ = 'Chris'

from flask.ext.script import Manager, prompt_bool

from flask import Flask

fileApp = Flask(__name__, static_folder = 'static', static_url_path = '/')

manager = Manager(fileApp)
#manager2 = Manager(usage="Perform something")

#TODO: Commands
#run python file -> log in
#change password
#share file
#turn auto synch on or off
#NOT add file -> this is done automatically by moving files around
#Signal sharing library (in Python)?
#FTP/Curl for sharing

@manager.command
def start():
    "Kick off the user command line interface."
    opt = 22
    while (opt != 0):
        #TODO: ask for login info, then show a different set of user options based on login type
        #but, for now, show file user options
        #admin user options - delete user, add user, start/stop back end stuff, more?
        print '''
        1) login
        2) share
        3) change password
        4) turn auto synch on or off
        '''
        opt = input("Please enter an option you want to do, or '0' to quit. ")
        while opt < 0 or opt > 4 or not isinstance(opt, int):
            opt = input("That is an invalid option, please re-try. ")
        if opt == 1:
            login()
        if opt == 2:
            shareFile()
        if opt == 3:
            changePassword()
        if opt == 4:
            changeSynch()

def login():
    print "This is how you would log in"

def shareFile():
    print "This is how you would share files"

def changePassword():
    print "This is how you would change your password"

def changeSynch():
    print "This is how you would change the autosynch settings"

if __name__ == '__main__':
    manager.run()
