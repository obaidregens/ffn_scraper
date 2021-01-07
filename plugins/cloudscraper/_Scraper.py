import cloudscraper as cloudscraper_original

from scraper import Scraper

class CloudscraperScraper(Scraper):
    def __init__(self, proxies:dict = None, browser:dict = None ):
        self.__session = cloudscraper_original.create_scraper(
            browser=browser
        )
        if proxies is not None:
            self.__session.proxies = proxies
        Scraper.__init__(self)
    async def startRequest(self,request):
        request.start(self.__session)