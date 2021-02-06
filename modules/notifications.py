import json
import atexit
from time import time
from modules.mysql_connection import (
    insert as dbInsert
)

from modules.load import getUserId
from modules.logging.main import log,make_way
from modules.utils import url_join

import settings

all_imported = {}

def importQueueAdd():
    log("Imported Queue Added")
    log(all_imported)
    for author_ID,_time in all_imported.items():
        user_id = getUserId(author_ID)        
        dbInsert("notifications",{
            "user_id": user_id,
            "notification_type": "stories_imported",
            "type_of": "user",
            "type_of_id": user_id,
            "type_by": "ffn_user",
            "type_by_id": author_ID,
            "email_status": "none",
            "timestamp": _time
        })
atexit.register(importQueueAdd)

def importQueue(author_ID,_time):
    log(f"Imported Notifications: {author_ID}")
    all_imported[author_ID] = _time

def chapter(chapter_id):
    site_dir = getattr(settings,"SITE_DIR",None)
    start_time = getattr(settings,"START_TIME",time())
    if site_dir is None:
        log("No SITE_DIR specified")
        return False
    fn = make_way(url_join(site_dir,f"/temp_notifications/notifications-{start_time}.jsonl"))
    with open(fn,"a+") as fdump:
        json_object = json.dumps({
            "chapter_id": chapter_id,
            "time_added": time()
        })
        fdump.write(json_object + "\n")

def verified(author_ID):
    user_id = getUserId(author_ID)
    dbInsert("notifications",{
        "user_id": user_id,
        "notification_type": "account_verified",
        "type_of": "user",
        "type_of_id": user_id,
        "type_by": "ffn_user",
        "type_by_id": author_ID,
        "email_status": "none",
        "timestamp": time()
    })