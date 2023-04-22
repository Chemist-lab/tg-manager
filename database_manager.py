import sqlite3

con = sqlite3.connect('Truster.db--symlink')
cur = con.cursor()

print('Database has been loaded')
