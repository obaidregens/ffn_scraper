import sqlite3
import json

connection = sqlite3.connect("data/UserData.db")
db = connection.cursor()

db.execute("SELECT ffn_user_id from ffn_scraped")
existingAuthors = [int(tup[0]) for tup in db.fetchall()]

db.execute("SELECT ffn_user_id from ffn_scraped WHERE sent != 0")
sentAuthors = [int(tup[0]) for tup in db.fetchall()]

current = []
def shouldScrape(AuthorID):
    return (int(AuthorID) not in existingAuthors) and (int(AuthorID) not in current)

def shouldMessage(AuthorID):
    return int(AuthorID) not in sentAuthors

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