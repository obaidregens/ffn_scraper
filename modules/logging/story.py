import json
from modules.logging.main import log,make_way
from modules.logging.cache import path

errCache = None
errFile = make_way(path("errored_stories.cache"))
def isErrored(storyID):
    global errCache
    if errCache is None:
        try:
            with open(errFile, "r") as dump_file:
                dump_is = dump_file.readlines()
        except:
            dump_is = []
        errCache = []
        for line in dump_is:
            errCache.append( int(json.loads(line)["storyID"]) )
    isIn = int(storyID) in errCache
    return isIn
def success(storyID):
    log(f"""
    ---------------------------------------
    SUCCESS

    Imported Story ID {storyID}
    ---------------------------------------
    """)
def error(storyID,err,meta = {}):
    if errCache is not None:
        errCache.append(int(storyID))
    with open(errFile,"a+") as dump_file:
        dump_file.write(json.dumps({
            "storyID": int(storyID),
            "err": str(err),
            "meta": meta
        }) + "\n")

    meta = json.dumps(meta)
    log(f"""
    ---------------------------------------
    ERROR

    Error importing Story ID {storyID}
    {err}
    Meta: {meta}
    ---------------------------------------
    """)