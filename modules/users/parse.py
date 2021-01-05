import math
from data.rating_map import ratingNums

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
            "chapters": 0,
            "words":    0,
            "favs":     0,
            "follows":  0,
            "reviews":  0,
            "rating":   0
        },
        "newest": {},
        "oldest": {},
        "top_favs": {}
    }
    if (sel.css("#content_wrapper_inner > table > tbody > tr > td > table > tbody > tr:nth-child(2) > td > span:nth-of-type(2)")):
        dataSend["data"]["profile_updated"] =  int(sel.css("#content_wrapper_inner > table > tbody > tr > td > table > tbody > tr:last-child > td > span:nth-of-type(2)").attrib["data-xutime"])
        
    fandoms_count = {}
    for story in sel.css("div.z-list.mystories"):
        raw_tags_string = ''.join(story.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall())
        # Remove Crossover
        if raw_tags_string[:12] == "Crossover - ":
            raw_tags_string = raw_tags_string[12:]
        # Remove Fandom
        raw_tags_string = raw_tags_string[len(story.attrib["data-category"]) + len(" - "):]

        tags = raw_tags_string.split(' - ')
        tags_dict = {}
        tags_dict["fandom"] = story.attrib["data-category"]
        tags_dict["updated"] = int(story.attrib["data-dateupdate"])
        tags_dict["published"] = int(story.attrib["data-datesubmit"])
        tags_dict["language"] = tags.pop(1)
        if 'Chapters: ' not in tags[1]:
            tags_dict['genre'] = tags.pop(1)
        else:
            tags_dict["genre"] = "General"
        for tag in tags:
            sp = tag.split(": ")
            if (len(sp) < 2):
                continue
            if sp[0] == "Rated":
                dataSend["total"]['rating'] += ratingNums[sp[1]]
                tags_dict['rating'] = sp[1]
            if sp[0] in ["Chapters","Words","Reviews","Favs","Follows"]:
                field = sp[0].lower()
                value = int(sp[1].replace(',',''))
                dataSend["total"][field] += value
                tags_dict[field] = value
        # Tags Collected
        if (tags_dict["updated"] > dataSend["newest"].get("updated",0)):
            dataSend["newest"] = tags_dict
        if (tags_dict.get("favs",0) > dataSend["top_favs"].get("favs",0)):
            dataSend["top_favs"] = tags_dict
        if (tags_dict["published"] < dataSend["oldest"].get("published",math.inf)):
            dataSend["oldest"] = tags_dict
        fandoms_count[tags_dict["fandom"]] = fandoms_count.get(tags_dict["fandom"],0) + 1 

    for fandom,count in fandoms_count.items():
        if "most_fandom" not in dataSend["data"]:
            dataSend["data"]["most_fandom"] = fandom
            continue
        if count > fandoms_count[dataSend["data"]["most_fandom"]]:
            dataSend["data"]["most_fandom"] = fandom
    for attr in ["newest","oldest","top_favs"]:
        if dataSend[attr] == {}:
            dataSend[attr] = tags_dict
    return dataSend