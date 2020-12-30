import sqlite3
import json

connection = sqlite3.connect("data/UserData.db")
db = connection.cursor()

db.execute(
    """
    CREATE TABLE IF NOT EXISTS unsent (
        ffn_user_id INTEGER PRIMARY KEY,
        message_sent INTEGER,
        ffn_username TEXT,
        ffn_joined INTEGER,
        profile_updated INTEGER,
        total_stories INTEGER,
        most_fandom TEXT,
        total_chapters INTEGER,
        total_words INTEGER,
        total_favs INTEGER,
        total_follows INTEGER,
        total_reviews INTEGER,
        total_rating INTEGER,
        top_favs_fandom TEXT,
        top_favs_words INTEGER,
        top_favs_reviews INTEGER,
        top_favs_chapters INTEGER,
        top_favs_favs INTEGER,
        top_favs_follows INTEGER,
        top_favs_rating TEXT,
        top_favs_language TEXT,
        top_favs_genre TEXT Romance,
        top_favs_updated INTEGER,
        top_favs_published INTEGER,
        oldest_published INTEGER,
        oldest_updated INTEGER,
        newest_published INTEGER,
        newest_updated INTEGER
    )
    """
)

def placeholder(l):
    return ",".join(['?'] * l )

def insert(table,insertData):
    keys = ",".join(insertData.keys())
    values = placeholder(len(insertData))
    sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
    db.execute(sql,list(insertData.values()))
    connection.commit()
    return db.lastrowid


with open("data/UserDataAll.jsonl","r") as fp:
    f = fp.readlines()
for r in f:
    row_id = insert("unsent",json.loads(r))