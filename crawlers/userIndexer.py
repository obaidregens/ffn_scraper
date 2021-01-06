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
    from modules.logging.main import log

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
            "total_chapters": collect["total"]["Chapters"],
            "total_words": collect["total"]["Words"],
            "total_favs": collect["total"]["Favs"],
            "total_follows": collect["total"]["Follows"],
            "total_reviews": collect["total"]["Reviews"],
            "total_rating": collect["total"]["Rated"],
            "top_favs_fandom": collect["top_favs"]["Fandom"],
            "top_favs_words": collect["top_favs"]["Words"],
            "top_favs_reviews": collect["top_favs"].get('Reviews',0),
            "top_favs_chapters": collect["top_favs"]["Chapters"],
            "top_favs_favs": collect["top_favs"].get("Favs",0),
            "top_favs_follows": collect["top_favs"].get("Follows",0),
            "top_favs_rating": collect["top_favs"]["Rated"],
            "top_favs_language": collect["top_favs"]["Language"],
            "top_favs_genre": collect["top_favs"]["Genre"],
            "top_favs_updated": collect["top_favs"]["Updated"],
            "top_favs_published": collect["top_favs"]["Published"],
            "oldest_published": collect["oldest"]["Published"],
            "oldest_updated": collect["oldest"]["Updated"],
            "newest_published": collect["newest"]["Published"],
            "newest_updated": collect["newest"]["Published"],
            "sent": 0
        }
        insertScrape(insertItems)

    def Evaluate(response,request,fandom):
        sel = Selector(text=response.text)
        for book in sel.css('#content_wrapper_inner > div.z-list'):
            Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])
            if not shouldScrape(Author_ID):
                continue
            startScrape(Author_ID)
            log("Will Scrape: " + str(Author_ID))
            s.follow(Request(
                "/u/" + str(Author_ID),
                callback=parseProfile,
                pass_on={
                    "uid": Author_ID
                }
            ))
        pg = int(sel.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get())
        log(f"Page Parsed: {pg} of Fandom {fandom}")
        next_pg_attr = sel.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib
        if ("href" in next_pg_attr) & (pg < MAX_PAGES):
            next_pg = next_pg_attr['href']
            s.follow(Request(
                next_pg,
                callback=Evaluate,
                pass_on={"fandom": fandom}
            ))

    start_urls = [
        "book/Harry-Potter/",
        "game/Pokémon/",
        "anime/Naruto/",
        "book/Twilight/",
        "anime/Hetalia-Axis-Powers/",
        "anime/Inuyasha/",
        "tv/Supernatural/",
        "tv/Glee/"
    ]
    for url in start_urls:
        s.follow(Request(
            "/" + url + "?&srt=5&r=10&t=4",
            callback=Evaluate,
            pass_on={"fandom": url}
        ))
