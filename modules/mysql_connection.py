import mysql.connector
import settings

connection = mysql.connector.connect(
    host = "localhost",
    user = settings.db.user,
    password = settings.db.password,
    database = settings.db.name,
    port = settings.db.get("port",3306)
)
db = connection.cursor()

def placeholder(l):
    return ",".join(['%s'] * l )

def insert(table,insertData):
    sql = "INSERT INTO " + table + " (" + ",".join(insertData.keys()) + ")" + " VALUES (" + placeholder(len(insertData)) + ")"
    db.execute(sql,list( insertData.values()))
    connection.commit()
    return db.lastrowid
