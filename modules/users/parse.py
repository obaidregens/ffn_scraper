import math
from data.rating_map import ratingNums
from modules.story import parse as parseStory

def Author(sel,uid):
    dataSend = {
        "uid": uid,
        "data": {
            "username": sel.css("#content_wrapper_inner > span:first-of-type::text").get().lstrip(),
            "ffn_joined": int(sel.css("#content_wrapper_inner > table > tbody > tr > td > table > tbody > tr:last-child > td > span:nth-child(1)").attrib["data-xutime"]),
            "profile_updated": 0,
            "total_stories": int(sel.css("#l_st > span::text").get())
        },
        "total": {
            "Chapters": 0,
            "Words":    0,
            "Favs":     0,
            "Follows":  0,
            "Reviews":  0,
            "Rated":   0
        },
        "newest": {},
        "oldest": {},
        "top_favs": {}
    }
    if (sel.css("#content_wrapper_inner > table > tbody > tr > td > table > tbody > tr:nth-child(2) > td > span:nth-of-type(2)")):
        dataSend["data"]["profile_updated"] =  int(sel.css("#content_wrapper_inner > table > tbody > tr > td > table > tbody > tr:last-child > td > span:nth-of-type(2)").attrib["data-xutime"])
        
    fandoms_count = {}
    for story in sel.css("div.z-list.mystories"):
        Tags = parseStory(story)["Tags"]
        print(Tags)
        Tags["Fandom"] = story.attrib["data-category"]
        Tags["Updated"] = int(story.attrib["data-dateupdate"])
        Tags["Published"] = int(story.attrib["data-datesubmit"])

        # Genre
        if len(Tags.get("Genre",[])) < 1:
            Tags["Genre"] = "General"
        else:
            Tags["Genre"] = "/".join(Tags["Genre"])

        dataSend["total"]['Rated'] += ratingNums[Tags["Rated"]]
        for tagName in ["Chapters","Words","Reviews","Favs","Follows"]:
            if tagName not in Tags:
                continue
            dataSend["total"][tagName] += Tags[tagName]

        # Tags Collected
        if (Tags["Updated"] > dataSend["newest"].get("Updated",0)):
            dataSend["newest"] = Tags
        if (Tags.get("Favs",0) > dataSend["top_favs"].get("Favs",0)):
            dataSend["top_favs"] = Tags
        if (Tags["Published"] < dataSend["oldest"].get("Published",math.inf)):
            dataSend["oldest"] = Tags
        fandoms_count[Tags["Fandom"]] = fandoms_count.get(Tags["Fandom"],0) + 1 

    for fandom,count in fandoms_count.items():
        if "most_fandom" not in dataSend["data"]:
            dataSend["data"]["most_fandom"] = fandom
            continue
        if count > fandoms_count[dataSend["data"]["most_fandom"]]:
            dataSend["data"]["most_fandom"] = fandom
    for attr in ["newest","oldest","top_favs"]:
        if dataSend[attr] == {}:
            dataSend[attr] = Tags
    return dataSend