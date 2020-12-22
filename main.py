def main():
    from scrapy.selector import Selector
    from modules.scraper import Scraper,Request
    from modules.author import parse as parseAuthor
    from modules.load import toImport
    import modules.story as Story

    s = Scraper(
        base="https://www.fanfiction.net/"
    )

    def Chapter(response, request, storyData):
        with open("index.html", "w+") as dump_file:
            dump_file.write(response.text)
        sel = Selector(text=response.text)
        chap = Story.parseChapter(sel,storyData)
        if chap == False:
            return
        if chap["next"] == False:
            Story.insert(chap["storyData"])
        else:
            s.follow(Request(
                url=chap["next"],
                callback=Chapter,
                pass_on={"storyData": storyData}
            ))
    def Authors(response, request):
        sel = Selector(text=response.text)
        stories = parseAuthor(sel)
        for story in stories:
            s.follow(Request(
                url=story["url"],
                pass_on={"storyData": story["story"]},
                callback=Chapter
            ))

    author_urls = [ ("https://www.fanfiction.net/u/" + str(author_ID) ) for author_ID in toImport.keys() ]
    for author_url in author_urls:
        s.add(Request(
            url=author_url,
            callback=Authors
        ))
if __name__ == "__main__":
    main()
