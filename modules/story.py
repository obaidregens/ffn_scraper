# External Libs
import lxml.html.clean as clean
from datetime import datetime
from time import time
import json
# Data
from data.rating_map import rating_map
# Modules
from modules.logging.story import error as storyError,success as storySuccess
from modules.logging.dump import html as html_dump
from modules.logging.main import log,make_way
from modules.load import getUserId,getStoryIds,all_imported
from modules.characters import find_fandom
from modules.utils import str_word_count,url_join
# SQL
from modules.mysql_connection import (
    db,
    connection as sql_connection,
    placeholder,
    insert as dbInsert
)
import modules.terms as terms
import modules.pairings as pairings
import settings

def notify(chapter_id):
    site_dir = getattr(settings,"SITE_DIR",None)
    start_time = getattr(settings,"START_TIME",time())
    if site_dir is None:
        log("No SITE_DIR specified")
        return False
    fn = make_way(url_join(site_dir,f"/temp_notifications/notifications-{start_time}.jsonl"))
    print(fn)
    with open(fn,"a+") as fdump:
        json_object = json.dumps({
            "chapter_id": chapter_id,
            "time_added": time()
        })
        fdump.write(json_object + "\n")
    

def insert(story):
    character_fandoms = {}
    characterOfFandoms = {}
    fandomOfName = {}
    # First Confirm that Characters & Fandoms exist in Map. Else Reject
    for fandomName in story["Tags"]["Fandom"]:
        fandom = find_fandom(fandomName)
        if fandom == False:
            storyError(story["_id"],"Fandom not found",{
                "fandom": fandomName
            })
            return
        if '"' in fandom or '+' in fandom:
            storyError(story["_id"],'Fandom has either `+` or `"` ',{
                "fandom": fandomName
            })
            return
        fandomOfName[fandomName] = fandom
        for characterName in story["Tags"].get("All Characters",[]):
            if characterName not in fandom["characters"]:
                continue
            character_fandoms[characterName] = fandom
            if (fandomName not in characterOfFandoms):
                characterOfFandoms[fandomName] = []
            characterOfFandoms[fandomName].append(characterName)
    if sorted(list(character_fandoms.keys())) != sorted( list(set(story["Tags"].get("All Characters",[]))) ):
        storyError(story["_id"],'Unmatched Characters',{
            "err": ",".join(character_fandoms.keys()) + " != " + ",".join(story["Tags"]["All Characters"])
        })
        return
    # Both of the above returns indicate that something has not been found in mapper

    # Check if all required Tags are present
    for tagNameReq in ["Status","Rated","Language"]:
        if tagNameReq not in story["Tags"]:
            storyError(story["_id"],'Required Tag Name not present',{
                "Tag Name": tagNameReq
            })
            return

    # Now confirm if rating is proper
    if story["Tags"]["Rated"] not in rating_map:
        storyError(story["_id"],'Rating not valid',{
            "Rating": "Rated: " + story["Tags"]["Rated"]
        })
        return

    author_ID = str(story["Author ID"])
    user_id = getUserId(author_ID)
    date = datetime.fromtimestamp(story["Published"]).strftime('%Y-%m-%d %H:%M:%S')
    modified = date
    current_time = int(time())
    if ("Updated" in story):
        modified = datetime.fromtimestamp(story["Updated"]).strftime('%Y-%m-%d %H:%M:%S')
    if (story["Existing"] == False):
        # Insert Story
        sql = "INSERT INTO wp_posts (post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,ping_status,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (user_id,date,date,"",story["Title"],story["Description"],'closed',"","",modified,modified,"",'book')
        db.execute(sql, val)
        sql_connection.commit()
        storyID = db.lastrowid
        metaVal = [
            (storyID,'author_name',story["Author Name"]),
            (storyID,'ffn_author_id',author_ID),
            (storyID,'ffn_book_id',story["_id"]),
            (storyID,'first_publish',story["Published"]),
            (storyID,'last_edited',current_time)
        ]
        # Add Tags
        # Tags - Fandom
        characterIdOfName = {}
        for fandomName in story["Tags"]["Fandom"]:
            fandom = fandomOfName[fandomName]
            categoryID = terms.ensure(fandom["category"].capitalize(),'category')
            fandomID = terms.ensure(fandom["fandom"],'category',categoryID)
            terms.connect(storyID,fandomID)
            for characterName in characterOfFandoms.get(fandomName,[]):
                if characterName == "OC":
                    characterID = terms.ensure(characterName,'character',0)
                else:
                    characterID = terms.ensure(characterName,'character',fandomID)
                characterIdOfName[characterName] = characterID
                terms.connect(storyID,characterID)
        # Tags - Language
        terms.connect(storyID,terms.ensure(story["Tags"]["Language"],'language'))
        # Tags - Status
        terms.connect(storyID,terms.ensure(story["Tags"]["Status"],'status'))
        # Tags - Rated
        terms.connect(storyID,terms.ensure(rating_map[story["Tags"]["Rated"]],'rating'))
        # Tags - Genre
        for genreName in story["Tags"].get("Genre",[]):
            terms.connect(storyID,terms.ensure(genreName,'genre'))
        # Tags - Pairing
        for relationship in story["Tags"].get("Relationships",[]):
            relationshipCharacters = []
            for char in relationship:
                relationshipCharacters.append(characterIdOfName[char])
            pairings.insert(storyID,relationshipCharacters)
        updateImport = """
        UPDATE import_stories
        SET import_status='live', story_id=%s, import_time=%s, import_favs=%s,import_follows=%s
        WHERE import_from='ffn' AND import_story=%s 
        """
        db.execute(updateImport,[storyID,current_time,story["Tags"].get("Favs",0),story["Tags"].get("Follows",0),story["_id"]])
    else:
        # Update Story Time as per FFN for Updating and Reimporting Stories
        storyID = int(story["Existing"])
        db.execute("""
        UPDATE wp_posts
        SET post_modified=%s, post_modified_gmt=%s
        WHERE ID=%s
        """,[modified,modified,storyID])
        metaVal = []
    if story["Reimport"] == True:
        # Set to Live
        updateImport = """
        UPDATE import_stories
        SET import_status='live'
        WHERE import_from='ffn'
        AND story_id = %s
        AND import_story=%s
        AND import_status='reimport' 
        """
        db.execute(updateImport,[ storyID, story["_id"] ])
        # Get current chapters
        sql = """
        SELECT b.meta_value,a.ID FROM wp_posts as a
        INNER JOIN wp_postmeta as b ON a.ID = b.post_id
        WHERE a.post_parent = %s
        AND a.post_type = 'chapter'
        AND b.meta_key = 'chapter_order'
        """
        db.execute(sql,[storyID])
        chapters = {int(tup[0]):int(tup[1]) for tup in db.fetchall()}
        toDelete = []
        for i in list(range(len(story["Chapters"]),len(chapters))):
            toDelete.append(chapters[i+1])
        if len(toDelete) > 0:
            db.execute("DELETE FROM wp_posts WHERE ID IN (" + placeholder(len(toDelete)) + ")",toDelete)

        chapterIndex = 1
        for chapter in story["Chapters"]:
            if chapterIndex in chapters:
                db.execute(
                    "UPDATE wp_posts SET post_content = %s, post_title = %s WHERE ID = %s",
                    [chapter['content'],chapter['title'],chapters[chapterIndex]]
                )
                # Update Word Count
                db.execute(
                    "UPDATE wp_postmeta SET meta_value = %s WHERE meta_key = 'word-count' AND post_id = %s",
                    [chapter["wordCount"],chapters[chapterIndex]]
                )
            else:
                chapter_id = dbInsert("wp_posts",{
                    "post_author": user_id,
                    "post_date": modified,
                    "post_date_gmt": modified,
                    "post_content": chapter["content"],
                    "post_title": chapter["title"],
                    "post_excerpt": "",
                    "ping_status": "closed",
                    "to_ping": "",
                    "pinged": "",
                    "post_modified": modified,
                    "post_modified_gmt": modified,
                    "post_content_filtered": "",
                    "post_parent": storyID,
                    "post_type": "chapter"
                })
                metaVal.append((chapter_id,'word-count',chapter["wordCount"]))
                metaVal.append(( chapter_id, 'chapter_order', chapterIndex ))
                notify(chapter_id)
            chapterIndex += 1
    else:
        # Chapter
        chapter_sql = "INSERT INTO wp_posts (post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,ping_status,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_parent,post_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        chapterIndex = story.get("chapterStartAt",1)
        totalWords = 0
        for chapter in story["Chapters"]:
            # Insert Chapter
            chapter_val = (user_id,modified,modified,chapter["content"],chapter["title"],"",'closed',"","",modified,modified,"",storyID,'chapter')
            db.execute(chapter_sql, chapter_val)
            sql_connection.commit()
            chapterID = db.lastrowid
            # Add to Chapter Meta Value
            totalWords += chapter["wordCount"]
            metaVal.append((chapterID,'word-count',chapter["wordCount"]))
            metaVal.append((chapterID,'chapter_order',chapterIndex))
            chapterIndex += 1
            notify(chapterID)
    
    # Insert Story and Chapter Meta
    if story["Existing"] == False:
        metaVal.append((storyID,'word-count',totalWords))
    metaSql = "INSERT INTO wp_postmeta (post_id,meta_key,meta_value) VALUES (%s, %s, %s)"
    db.executemany(metaSql,metaVal)

    if story["Reimport"] == True or story["Existing"] == False:
        # Now Let's add a notification if all users stories have been done.
        all_imported.append(str(story["_id"]))
        if len(set( getStoryIds(author_ID) - set(all_imported) )) < 1:
            db.execute(
                """
                INSERT INTO notifications (user_id,notification_type,type_of,type_of_id,type_by,type_by_id,email_status,timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                [user_id,'stories_imported','user',user_id,'ffn_user',author_ID,'none',current_time]
            )
        sql_connection.commit()
    if story["Existing"] != False:
        # Update Words
        db.execute("""
        SELECT SUM(wp_postmeta.meta_value) as c FROM wp_postmeta
        INNER JOIN wp_posts ON wp_posts.ID = wp_postmeta.post_id
        WHERE wp_postmeta.meta_key = 'word-count'
        AND wp_posts.post_parent = %s
        """,[storyID])
        word_count = int(db.fetchone()[0])
        db.execute("""
        UPDATE wp_postmeta
        SET meta_value = %s
        WHERE post_id=%s AND meta_key="word-count"
        """,[word_count,storyID])
        db.execute("""
        UPDATE wp_postmeta
        SET meta_value = %s
        WHERE post_id=%s AND meta_key="last_edited"
        """,[current_time,storyID])
    sql_connection.commit()
    storySuccess(storyID)

def parse(storyBlock):
    ID = int(storyBlock.css("a.stitle::attr(href)").get().split('/')[2])

    raw_tags_string = ''.join(storyBlock.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall())

    # Remove Crossover
    if raw_tags_string[:12] == "Crossover - ":
        raw_tags_string = raw_tags_string[12:]
    # Remove Fandom
    fixed_cat = storyBlock.attrib["data-category"].replace("\\'","'").replace("  "," ")
    raw_tags_string = raw_tags_string[len(fixed_cat) + len(" - "):]

    raw_tags = raw_tags_string.split(' - ')
    tags = {}

    tags['Language'] = raw_tags.pop(1)
    if 'Chapters: ' not in raw_tags[1]:
        tags['Genre'] = raw_tags.pop(1).split('/')
    if 'Complete' == raw_tags[-1]:
        tags['Status'] = raw_tags.pop(-1)
    else:
        tags['Status'] = 'In Progress'
    for tag_is in raw_tags:
        if 'Updated: ' in tag_is or 'Published: ' in tag_is:
            pass
        elif ': ' in tag_is:
            tag_is_arr = tag_is.split(': ')
            if tag_is_arr[0] in ['Chapters','Words','Reviews','Favs','Follows']:
                tag_is_arr[1] = int(tag_is_arr[1].replace(',',''))
            tags[tag_is_arr[0]] = tag_is_arr[1]
        else:
            raw_characters = tag_is.split(']')
            if '' in raw_characters: raw_characters.remove('')
            tags['Relationships'] = []
            tags['Characters'] = []
            tags['All Characters'] = []
            for characters_piece in raw_characters:
                char_set = characters_piece.lstrip(' [').split(', ')
                if '[' in characters_piece:
                    tags['Relationships'].append(char_set)
                else:
                    tags['Characters'] = char_set
                tags['All Characters'] += char_set
    story_data = {
        '_id'           : ID,
        'Title'         : storyBlock.css("a.stitle::text").get(),
        'Description'   : storyBlock.css("div.z-indent.z-padtop::text").get(),
        'Tags'          : tags,
        'Chapters'      : []
    }
    first_time = storyBlock.css('.z-padtop2.xgray > span:nth-of-type(1)::attr(data-xutime)').get()
    second_time = storyBlock.css('.z-padtop2.xgray > span:nth-of-type(2)::attr(data-xutime)').get()
    if second_time is not None:
        story_data['Updated'] = int(first_time)
        story_data['Published'] = int(second_time)
    else:
        story_data['Published'] = int(first_time)
    return story_data

def parseChapter(response,storyData):

    cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=set(["style"]),page_structure=False)

    isCrossover = response.css('#pre_story_links > span > img[src="//ff74.b-cdn.net/static/fcons/arrow-switch.png"]').get() is not None
    if isCrossover:
        storyData["Tags"]["Fandom"] = response.css('#pre_story_links > span > a::text').get()[:-10].split(' + ')
    else:
        storyData["Tags"]["Category"] = response.css("#pre_story_links > span > a:first-of-type::text").get()
        storyData["Tags"]["Fandom"] = [response.css('#pre_story_links > span > a:last-child::text').get()]
    title = response.css('select#chap_select > option[selected]::text').get()
    if (title is None):
        title = '1. Chapter 1'
    chapterArr = title.split(". ",1)
    currentChapter = int(chapterArr[0])
    title = chapterArr[1]
    cont = ''.join(response.css('#storytext > p,#storytext > hr').getall())
    if len(cont) > 0:
        # Strip Div Tag Cleaner adds
        cont = cleaner.clean_html(cont)[5:-6]
        storyData['Chapters'].append({
            "title"     : title,
            "content"   : cont,
            "wordCount" : str_word_count( " ".join(response.css("#storytext > p::text").getall() )),
        })
        next_btn = response.css('#chap_select + button.btn::attr(onclick)').get()
        forward = {
            "storyData": storyData,
            "next": False
        }
        if storyData["Tags"]["Chapters"] > currentChapter and next_btn is not None:
            forward["next"] = next_btn.replace('self.location=\'','').rstrip('\'')
        return forward
    else:
        storyID = storyData["_id"]
        html_dump(str(response.get()),f"chapterError-{storyID}-{currentChapter}.html")
        storyError(
            storyID,
            "Chapter Error",{
                "chapter": currentChapter
            }
        )
        return False

def addNewRow(storyData):
    log(f"""
        Added UnImported Row of Story
        {storyData["_id"]}
    """)
    dbInsert("import_stories",{
        "import_user": storyData["Author ID"],
        "import_from": "ffn",
        "user_id": getUserId(storyData["Author ID"]),
        "story_id": 0,
        "import_story": storyData["_id"],
        "import_status": "not_imported",
        "request_time": 0,
        "import_time": int(time()),
        "import_favs": storyData["Tags"].get("Favs",0),
        "import_follows": storyData["Tags"].get("Follows",0),
        "import_title": storyData["Title"]
    },insertIgnore=True)