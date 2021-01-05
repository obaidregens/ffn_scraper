import sqlite3
from modules.mysql_connection import db as mysqldb

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

connection = sqlite3.connect("data/UserData.db")
connection.row_factory = dict_factory
db = connection.cursor()

db.execute(
    """
    CREATE TABLE IF NOT EXISTS ffn_scraped (
        ffn_user_id INTEGER PRIMARY KEY,
        scraped INTEGER,
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
        top_favs_genre TEXT,
        top_favs_updated INTEGER,
        top_favs_published INTEGER,
        oldest_published INTEGER,
        oldest_updated INTEGER,
        newest_published INTEGER,
        newest_updated INTEGER,
        sent INTEGER
    )
    """
)

def placeholder(l):
    return ",".join(['?'] * l )

def insert(table,insertData):
    keys = ",".join(insertData.keys())
    values = placeholder(len(insertData))
    sql = f"INSERT OR IGNORE INTO {table} ({keys}) VALUES ({values})"
    db.execute(sql,list(insertData.values()))
    connection.commit()
    return db.lastrowid

rowNames = [
    'ffn_user_id',
    'message_sent',
    'ffn_username',
    'ffn_joined',
    'profile_updated',
    'total_stories',
    'most_fandom',
    'total_chapters',
    'total_words',
    'total_favs',
    'total_follows',
    'total_reviews',
    'total_rating',
    'top_favs_fandom',
    'top_favs_words',
    'top_favs_reviews',
    'top_favs_chapters',
    'top_favs_favs',
    'top_favs_follows',
    'top_favs_rating',
    'top_favs_language',
    'top_favs_genre',
    'top_favs_updated',
    'top_favs_published',
    'oldest_published',
    'oldest_updated',
    'newest_published',
    'newest_updated'
]

mysqldb.execute("SELECT * FROM ffn_outreach")
for row_tuple in mysqldb.fetchall():
    row = {}
    i = 0
    for val in row_tuple:
        row[rowNames[i]] = val
        i += 1
    row["scraped"] = row.pop("message_sent")
    row["sent"] = row["scraped"]
    insert("ffn_scraped",row)
connection.commit()
db.execute("SELECT COUNT(*) FROM ffn_scraped")
print(db.fetchone())
