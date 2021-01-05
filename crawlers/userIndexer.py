def main():
    PROXY_IP = "http://45.79.151.177:8191/v1"
    MAX_PAGES = 50
    
    from scrapy.selector import Selector
    from time import time
    from modules.users.connection import shouldScrape,startScrape,insertScrape
    from modules.users.parse import Author as parseAuthor
    from plugins.flaresolverr import (
        FlaresolverrScraper as Scraper,
        FlaresolverrRequest as Request
    )

    s = Scraper(
        PROXY_IP,
        base="https://www.fanfiction.net/"
    )
    def parseProfile(response, request, uid):
        sel = Selector(text=response.text)
        collect = parseAuthor(sel,uid)
        insertItems = {
            "ffn_user_id": uid,
            "scraped": int(time()),
            "ffn_username": collect["data"]["username"],
            "ffn_joined": collect["data"]["ffn_joined"],
            "profile_updated": collect["data"]["profile_updated"],
            "total_stories": collect["data"]["total_stories"],
            "most_fandom": collect["data"]["most_fandom"],
            "total_chapters": collect["total"]["chapters"],
            "total_words": collect["total"]["words"],
            "total_favs": collect["total"]["favs"],
            "total_follows": collect["total"]["follows"],
            "total_reviews": collect["total"]["reviews"],
            "total_rating": collect["total"]["rating"],
            "top_favs_fandom": collect["top_favs"]["fandom"],
            "top_favs_words": collect["top_favs"]["words"],
            "top_favs_reviews": collect["top_favs"].get('reviews',0),
            "top_favs_chapters": collect["top_favs"]["chapters"],
            "top_favs_favs": collect["top_favs"].get("favs",0),
            "top_favs_follows": collect["top_favs"].get("follows",0),
            "top_favs_rating": collect["top_favs"]["rating"],
            "top_favs_language": collect["top_favs"]["language"],
            "top_favs_genre": collect["top_favs"]["genre"],
            "top_favs_updated": collect["top_favs"]["updated"],
            "top_favs_published": collect["top_favs"]["published"],
            "oldest_published": collect["oldest"]["published"],
            "oldest_updated": collect["oldest"]["updated"],
            "newest_published": collect["newest"]["published"],
            "newest_updated": collect["newest"]["published"],
            "sent": 0
        }
        insertScrape(insertItems)

    def Evaluate(response,request):
        sel = Selector(text=response.text)
        for book in sel.css('#content_wrapper_inner > div.z-list'):
            Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])
            if not shouldScrape(Author_ID):
                continue
            startScrape(Author_ID)
            s.follow(Request(
                "/u/" + str(Author_ID),
                callback=parseProfile,
                pass_on={
                    "uid": Author_ID
                }
            ))
        pg = int(sel.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get())
        next_pg_attr = sel.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib
        if ("href" in next_pg_attr) & (pg < MAX_PAGES):
            next_pg = next_pg_attr['href']
            s.follow(Request(
                next_pg,
                callback=Evaluate
            ))

    start_urls = ["/" + url + "?&srt=5&r=10&t=4" for url in [
        "book/Harry-Potter/",
        "game/Pokémon/",
        "anime/Naruto/",
        "book/Twilight/",
        "anime/Hetalia-Axis-Powers/",
        "anime/Inuyasha/",
        "tv/Supernatural/",
        "tv/Glee/"
    ]]
    for url in start_urls:
        s.follow(Request(
            url,
            callback=Evaluate
        ))
