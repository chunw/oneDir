__author__ = 'Justin'

import sqlite3

createDb = sqlite3.connect('OneDir_accounts.db')
createDb.text_factory = str
queryCurs = createDb.cursor()


def createTable():
    queryCurs.execute('''CREATE TABLE user_account
    (username TEXT PRIMARY KEY, PASSWORD TEXT)''')

def addUserAccount(username, password):
        queryCurs.execute('''INSERT INTO user_account (username, password)
        VALUES (?, ?)''', (username, password))

def main():
    #queryCurs.execute('''DELETE  FROM user_account where username = 'justinc' ''')
    #addUserAccount('justinc', 'qwerty')
    #addUserAccount('user1', 'password')
    createDb.commit()
    queryCurs.execute('SELECT * FROM user_account')

    for i in queryCurs:
        print i;

if __name__ == "__main__": main()

