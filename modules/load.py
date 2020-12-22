from modules.mysql_connection import db 

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

all_imported = []

def getStoryIds(ffn_user):
    return toImport[int(ffn_user)]["stories"].keys()
def getUserId(ffn_user):
    return toImport[int(ffn_user)]["user_id"]