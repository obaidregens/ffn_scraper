def main():
    import settings

    flaresolverr_location = getattr(settings,"IMPORTER_FLARESOLVERR_PROXY",None)
    if flaresolverr_location is None:
        raise Exception("No IMPORTER_FLARESOLVERR_PROXY specified")

    from scrapy.selector import Selector

    from modules.author import parse as parseAuthor
    from modules.load import getCurrent
    import modules.story as Story
    from plugins.flaresolverr import (
        Request,
        Scraper
    )

    s = Scraper(
        flaresolverr_location
    )

    def Chapter(response, request, storyData):
        sel = Selector(text=response.text)
        chap = Story.parseChapter(sel,storyData)
        if chap == False:
            return
        if chap["next"] == False:
            Story.insert(chap["storyData"])
        else:
            s.follow(request.url,Request(
                chap["next"],
                callback=Chapter,
                pass_on={"storyData": storyData}
            ))
    
    def Authors(response, request):
        sel = Selector(text=response.text)
        stories = parseAuthor(sel)
        for story in stories:
            s.follow(request.url,Request(
                story["url"],
                pass_on={"storyData": story["story"]},
                callback=Chapter
            ))

    author_urls = [ f"https://www.fanfiction.net/u/{author_ID}" for author_ID in getCurrent() ]
    for author_url in author_urls:
        s.add(Request(
            author_url,
            callback=Authors
        ))