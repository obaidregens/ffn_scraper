def main():
    from scrapy.selector import Selector
    from modules.story import parse
    from plugins.flaresolverr import (
        FlaresolverrScraper as Scraper,
        FlaresolverrRequest as Request
    )

    PROXY_IP = "http://45.79.151.177:8191/v1"
    s = Scraper(
        PROXY_IP,
        base="https://www.fanfiction.net/"
    )
    def Author(response,request):
        sel = Selector(text=response.text)
        story = parse(sel.css('div.z-list.mystories:last-child')[0])
        print(story)

    s.follow(Request(
        "/u/11675501",
        callback=Author
    ))
