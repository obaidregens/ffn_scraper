import settings
from modules.mysql_connection import db,placeholder
from modules.logging.main import make_way
from modules.logging.cache import path as cache_path

sql_cmd = """
SELECT
    a.import_user,
    a.user_id,
    a.import_story,
    a.story_id,
    COUNT(CONCAT(a.import_story,"-",a.story_id)) as chapters,
    a.import_status
FROM import_stories as a
INNER JOIN wp_posts as b ON b.post_parent = a.story_id
WHERE import_status IN ('pending','live','reimport')
GROUP BY CONCAT(a.import_story,"-",a.story_id)
"""
db.execute(sql_cmd)

toImport = {}
for row in db.fetchall():
    row = list(row)
    import_status = str(row.pop())
    ffn_user,user_id,ffn_story,story_id,chapters = map(int,row)
    if ffn_user not in toImport:
        toImport[ffn_user] = {
            "stories"   : {},
            "user_id"   : user_id
        }
    if import_status == "pending":
        chapters = 0
    toImport[ffn_user]["stories"][ffn_story] = {
        "story_id": story_id,
        "status": import_status,
        "chapters": chapters
    }

sql_cmd = """
SELECT connection_user,user_id
FROM user_connections
"""
if len(toImport) > 0:
    sql_cmd += f"WHERE connection_user NOT IN ({placeholder(len(toImport))})"
db.execute(sql_cmd,list(toImport.keys()))
for row in db.fetchall():
    try:
        ffn_user_id = int(row[0])
    except:
        continue
    toImport[ffn_user_id] = {
        "stories": {},
        "user_id": int(row[1])
    }


def getCurrent():
    fn = make_way(cache_path("authors-load.json"))
    n = getattr(settings,"AUTHOR_LOAD_CHUNK",50)
    
    try:
        with open(fn,"r") as fp:
            authorIds = list(map(int,fp.readlines()))
    except Exception:
        authorIds = []
    
    newAuthors = list(set(toImport.keys()) - set(authorIds))[:n]
    for i in range(len(newAuthors),min(n,len(authorIds))):
        newAuthors.append(authorIds.pop(0))

    with open(fn,"w+") as fp:
        fp.write("\n".join(map(str,authorIds + newAuthors)))
    
    return newAuthors
def getStoryIds(_ffn_user):
    return toImport[int(_ffn_user)]["stories"].keys()
def getUserId(_ffn_user):
    return toImport[int(_ffn_user)]["user_id"]

