def main():
    from scrapy.selector import Selector
    from modules.story import parse
    from plugins.flaresolverr import (
        Scraper,
        Request
    )
    import settings
    flaresolverr_location = getattr(settings,"INDEXER_FLARESOLVERR_PROXY",None)
    if flaresolverr_location is None:
        raise Exception("No INDEXER_FLARESOLVERR_PROXY specified")

    s = Scraper(
        flaresolverr_location
    )
    def Author(response,request):
        sel = Selector(text=response.text)
        story = parse(sel.css('div.z-list.mystories:last-child')[0])
        print(story)

    s.add(Request(
        "https://www.fanfiction.net/u/11675501",
        callback=Author
    ))
