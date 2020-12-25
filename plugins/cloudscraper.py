import cloudscraper
from scraper import Request,Scraper

class CloudscraperRequest(Request):
    def get_response(self, session):
        kwargs = {}
        if self.proxies is not None:
            kwargs["proxies"] = self.proxies
        response = session.get(self.url,**kwargs)
        return response

class CloudscraperScraper(Scraper):
    def __init__(self,base=None, proxies:dict = None, browser:dict = None ):
        self.__session = cloudscraper.create_scraper(
            browser=browser
        )
        if proxies is not None:
            self.__session.proxies = proxies
        Scraper.__init__(self,base)
    async def startRequest(self,request):
        request.start(self.__session)