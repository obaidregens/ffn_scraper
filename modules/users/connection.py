import sqlite3
import json
from time import time

connection = sqlite3.connect("data/UserData.db")
db = connection.cursor()

db.execute("SELECT ffn_user_id from ffn_scraped")
existingAuthors = [int(tup[0]) for tup in db.fetchall()]

current = []
def shouldScrape(AuthorID):
    return (int(AuthorID) not in existingAuthors) and (int(AuthorID) not in current)

def startScrape(AuthorID):
    current.append(int(AuthorID))

def placeholder(l):
    return ",".join(['?'] * l )

def insert(table,insertData):
    keys = ",".join(insertData.keys())
    values = placeholder(len(insertData))
    sql = f"INSERT OR IGNORE INTO {table} ({keys}) VALUES ({values})"
    db.execute(sql,list(insertData.values()))
    connection.commit()
    return db.lastrowid

def insertScrape(insertData):
    insert("ffn_scraped",insertData)

def toMessage():
    db.execute("""
    SELECT ffn_user_id,ffn_username FROM ffn_scraped
    WHERE sent = 0
    AND (
        total_favs >= 350
        OR total_follows >= 350
    )
    """)
    return dict([[int(tup[0]),tup[1]] for tup in db.fetchall()])

def sendUser(AuthorId):
    sql = f"UPDATE ffn_scraped SET sent={time()} WHERE ffn_user_id=?"
    db.execute(sql,[str(AuthorId)])
    connection.commit()
    return AuthorId