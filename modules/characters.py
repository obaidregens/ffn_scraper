import sqlite3
import json

connection = sqlite3.connect("data/CharacterMaps.db")
db = connection.cursor()

def find_fandom(fandom):
    sql = "SELECT fandom,category,characters FROM ffnMap WHERE fandom = ?"
    db.execute(sql,[fandom])
    results = db.fetchall()
    if len(results) == 0:
        return False
    return {
        "fandom":       results[0][0],
        "category":     results[0][1],
        "characters":   json.loads(results[0][2])
    }
