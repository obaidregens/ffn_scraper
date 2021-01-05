import sqlite3
import json

connection = sqlite3.connect("data/UserData.db")
db = connection.cursor()

db.execute("SELECT ffn_user_id from ffn_outreach")
existingAuthors = [int(tup[0]) for tup in db.fetchall()]

def shouldScrape(AuthorID):
    return int(AuthorID) not in existingAuthors

