from time import time
import asyncio
import atexit
import logging
from functools import partial
import cloudscraper
from modules.logging.main import log
from modules.utils import url_join

class Request:
    def __init__(
        self,
        url,
        callback=None,
        cookies={},
        pass_on={},
        proxies=None
    ):
        self.url = url
        self.callback = Request.dummy
        if callback is not None:
            self.callback = callback
        self.cookies = cookies
        self.proxies = proxies
        self.pass_on = pass_on
    async def start(self, cloudscraper_instance):
        kwargs = {}
        if self.proxies is not None:
            kwargs["proxies"] = self.proxies
        response = cloudscraper_instance.get(self.url,**kwargs)
        if self.callback is not None:
            self.callback(response=response,request=self,**self.pass_on)

    @classmethod
    def dummy(self,response,request,**kwargs):
        pass

class Scraper:
    requests_per_second = 1
    def __init__(self,base = None,browser:dict = None,proxies=None):
        self.base = base
        self.__logfile = "thread-" + str(time()) + ".log"
        self.__queue = []
        self.__running = []
        self.__ended = []
        self.__cloudscraper = cloudscraper.create_scraper(
            browser=browser
        )
        if proxies is not None:
            self.__cloudscraper.proxies = proxies
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
    def restartRequest(self, req):
        try:
            self.__running.remove(req)
        except:
            pass
        req.began = 0
        req.ended = 0
        self.__queue.append(req)
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
        if int(response.status_code) == 200:
            self.__ended.append(request)
            request.ended = time()
            try:
                callback(response=response,request=request,**kwargs)
            except Exception as e:
                self.restartRequest(request)
                log(f"""

                Caught an Exception
                {e}
                with request callback
                {request}
                {request.url}
                
                """)
        else:
            self.restartRequest(request)
    async def run(self):
        while not self.__closed or self.running() or self.queued():
            if not self.isEmpty():
                in_last_second = self.running()
                log("",self.__logfile)
                log(time(),self.__logfile)
                log(f'{in_last_second} Running',self.__logfile)
                i = len(self.__ended)-1
                while i >= 0 and in_last_second < Scraper.requests_per_second:
                    if (time() - self.__ended[i].ended) <= 1.01:
                        in_last_second += 1
                    i -= 1
                log(f'{in_last_second} In last second',self.__logfile)
                log("",self.__logfile)
                for n in range(Scraper.requests_per_second - in_last_second):
                    req = self.__queue.pop(0)
                    req.began = time()
                    self.__running.append(req)
                    try:
                        await req.start(self.__cloudscraper)
                    except Exception as e:
                        self.restartRequest(req)
                        log(f"""

                        Caught Exception
                        {e}
                        while getting
                        {req}
                        {req.url}
                        
                        """)
            await asyncio.sleep(0.1)