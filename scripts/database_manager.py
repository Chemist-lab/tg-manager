import sqlite3

con = sqlite3.connect('Truster.db')
cur = con.cursor()

print('Database has been loaded')
