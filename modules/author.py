from modules.load import toImport
from modules.story import parse as parseStory
from modules.logging.story import isErrored
from modules.logging.author import log as author_log
from modules.logging.dump import html as html_dump

def parse(response):
    Author_ID = int(response.css("#content_wrapper_inner > a.pull-right:first-child").attrib["href"][8:-1])
    Author_Name = response.css("#content_wrapper_inner > a.pull-right:first-child + span::text").get().lstrip()
    Author = toImport[Author_ID]

    stories = []
    myStories = response.css("div.z-list.mystories")
    for storyBlock in myStories:
        storyData = parseStory(storyBlock)
        storyData["Author ID"] = Author_ID
        storyData["Author Name"] = Author_Name
        if storyData["_id"] not in Author["stories"]:
            continue
        Story = Author["stories"][storyData["_id"]]
        
        chapterStartAt = Story["chapters"]+1
        
        storyData["Reimport"] = False
        if Story["status"] == "reimport":
            storyData["Reimport"] = True
            chapterStartAt = 1

        storyData["Existing"] = True
        if Story["status"] == "pending":
            storyData["Existing"] = False

        storyData["chapterStartAt"] = chapterStartAt
        if chapterStartAt > storyData["Tags"]["Chapters"]:
            continue

        if not isErrored(storyData["_id"]):
            stories.append({
                "url": "/s/" + str(storyData["_id"]) + "/" + str(chapterStartAt),
                "story": storyData
            })            
    author_log(
        Author_ID,
        len(myStories),
        [storySingle["story"]["_id"] for storySingle in stories]
    )
    return stories