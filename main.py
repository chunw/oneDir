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
    print '''
    Please provide your log-in information.
    '''
    username = input("Username: ")
    password = input("Password: ")
    #get user type
    opt = 22

    while (opt != 0):
        #TODO: ask for login info, then show a different set of user options based on login type
        #if (user type == file user)
        print '''
        1) share
        2) change password
        3) turn auto synch on or off
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
        1) delete user
        2) add user
        3) start or stop file system
        '''
        opt = input("Please enter an option you want to do, or '0' to quit. ")
        while opt < 0 or opt > 3 or not isinstance(opt, int):
            opt = input("That is an invalid option, please re-try. ")
        if opt == 1:
            deleteUser()
        if opt == 2:
            addUser()
        if opt == 3:
            changeSystem()

def shareFile():
    print "This is how you would share files"

def changePassword():
    print "This is how you would change your password"

def changeSynch():
    print "This is how you would change the autosynch settings"

def deleteUser():
    print "This is how you would delete a user"

def addUser():
    print "This is how you would add a user"

def changeSystem():
    print "This is how you would start or stop the system"

if __name__ == '__main__':
    manager.run()

