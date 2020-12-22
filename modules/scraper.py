from time import time_ns as time
from functools import partial
import cloudscraper
import asyncio
import atexit
import logging
from modules.utils import url_join

class Request:
    def __init__(
        self,
        url,
        callback=None,
        cookies={},
        pass_on={}
    ):
        self.url = url
        self.callback = Request.dummy
        if callback is not None:
            self.callback = callback
        self.cookies = cookies
        self.pass_on = pass_on
    async def start(self, cloudscraper_instance):
        response = cloudscraper_instance.get(self.url)
        if self.callback is not None:
            self.callback(response=response,request=self,**self.pass_on)

    @classmethod
    def dummy(self,response,request,**kwargs):
        pass

class Scraper:
    requests_per_second = 1
    def __init__(self,base = None):
        self.base = base
        self.__queue = []
        self.__running = []
        self.__ended = []
        self.__cloudscraper = cloudscraper.create_scraper()
        self.__main_task = asyncio.get_event_loop().create_task(self.run())
        self.__closed = False
        atexit.register(self.awaitAll)
    def add(self, request: Request):
        request.callback = partial(self.closeRequest,request.callback)
        self.__queue.append(request)
    def follow(self, request: Request):
        if self.base is None:
            raise Exception("Cannot follow, base is None")
        request.url = url_join(self.base,request.url)
        self.add(request)
    def isEmpty(self):
        return len(self.__queue) < 1
    def running(self):
        return len(self.__running)
    def queued(self):
        return len(self.__queue)
    def close(self):
        self.__closed = True
    def awaitAll(self):
        loop = asyncio.get_event_loop()
        try:
            self.close()
            loop.run_until_complete(self.__main_task)
        finally:
            logging.info("Ended")
            loop.close()
    def closeRequest(self,callback,response,request,**kwargs):
        self.__running.remove(request)
        self.__ended.append(request)
        request.ended = time()
        callback(response=response,request=request,**kwargs)
    async def run(self):
        while not self.__closed or self.running() or self.queued():
            if not self.isEmpty():
                in_last_second = self.running()
                i = len(self.__ended)-1
                while i >= 0 and in_last_second < Scraper.requests_per_second:
                    if (time() - self.__ended[i].ended) <= 1.01:
                        in_last_second += 1
                    i -= 1
                for n in range(Scraper.requests_per_second - in_last_second):
                    req = self.__queue.pop(0)
                    req.began = time()
                    self.__running.append(req)
                    await req.start(self.__cloudscraper)
            await asyncio.sleep(0.1)