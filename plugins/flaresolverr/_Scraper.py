from scraper import Scraper

from plugins.flaresolverr import Session

class FlaresolverrScraper(Scraper):
    def __init__(self,location, agent=None ):
        self.__session = Session(location,agent=agent)
        Scraper.__init__(self)
    async def startRequest(self,request):
        request.start(self.__session)