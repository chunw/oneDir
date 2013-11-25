__author__ = 'Justin'

import sqlite3

createDb = sqlite3.connect('OneDir_accounts.db')
createDb.text_factory = str
queryCurs = createDb.cursor()


def createTable():
    queryCurs.execute('''CREATE TABLE user_account
    (username TEXT PRIMARY KEY, PASSWORD TEXT)''')

def addUserAccount(username, password):
        queryCurs.execute('''INSERT INTO user_account (username, password, user_type)
        VALUES (?, ?, 'normal')''', (username, password))

def addAdminAccount(username, password):
        queryCurs.execute('''INSERT INTO user_account (username, password, user_type)
        VALUES (?, ?, 'admin')''', (username, password))

def main():
    #createTable()
    #queryCurs.execute("ALTER TABLE user_account ADD COLUMN user_type TEXT")
    #queryCurs.execute("ALTER TABLE user_account ADD COLUMN files TEXT")
    queryCurs.execute("UPDATE user_account SET user_type = 'admin' WHERE username = 'justinc'")
    #queryCurs.execute('''DELETE  FROM user_account where username = 'david' ''')
    #addUserAccount('justinc', 'qwerty')
    #addUserAccount('user1', 'password')
    #addUserAccount('smithc', 'password')
    #addAdminAccount('david', 'password')
    createDb.commit()
    queryCurs.execute('SELECT * FROM user_account')

    for i in queryCurs:
        print i;

if __name__ == "__main__": main()