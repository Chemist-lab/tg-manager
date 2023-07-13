import sqlite3

con = None
cur = None

try:
    con = sqlite3.connect('Truster.db')
    cur = con.cursor()
    print('Database has been loaded')
except:
    print("Error while connecting to database")


