__author__ = 'Justin'

import sqlite3

createDb = sqlite3.connect('OneDir_accounts.db')
createDb.text_factory = str
queryCurs = createDb.cursor()


def createTable():
    queryCurs.execute('''CREATE TABLE user_account
    (username TEXT PRIMARY KEY, PASSWORD TEXT)''')

def addUserAccount(username, password, user_type):
        queryCurs.execute('''INSERT INTO user_account (username, password, user_type)
        VALUES (?, ?, 'normal')''', (username, password))

def main():
    #createTable()
    #queryCurs.execute("ALTER TABLE user_account ADD COLUMN files TEXT") #one time change
    queryCurs.execute("UPDATE user_account SET files = 'file1,file2' WHERE username = 'chun'")
    #queryCurs.execute('''DELETE  FROM user_account where username = 'justinc' ''')
    #addUserAccount('smithc1', 'password', 'normal')
    createDb.commit()
    queryCurs.execute('SELECT * FROM user_account')

    for i in queryCurs:
        print i;

    #queryCurs.execute("SELECT files FROM user_account WHERE username = 'chun'")
    #for i in queryCurs:
    #    print i[0].split(',')


if __name__ == "__main__": main()

