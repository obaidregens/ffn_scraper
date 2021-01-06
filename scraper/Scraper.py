from time import time
import asyncio
import atexit
import logging
from functools import partial
from modules.logging.main import log
from modules.utils import url_join
from scraper import Request
import traceback
from pprint import pprint

class Scraper:
    requests_per_second = 4
    def __init__(self,base = None):
        self.base = base
        self.__logfile = "thread-" + str(time()) + ".log"
        self.__queue = []
        self.__running = []
        self.__calling = []
        self.__ended = []
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
    def called(self):
        return len(self.__calling)
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
                self.__calling.append(request)
                callback(response=response,request=request,**kwargs)
                self.__calling.remove(request)
            except Exception as e:
                
                try: self.__calling.remove(request)
                except Exception as e: pass

                self.restartRequest(request)
                log(f"""

                Caught an Exception
                {e}
                with request callback
                {request}
                {request.url}

                Traceback:
                {traceback.format_exc()}
                
                """,filename="exceptions.log")
        else:
            self.restartRequest(request)
    async def startRequest(self,request):
        request.start()
    async def run(self):
        while not self.__closed or self.running() or self.queued() or self.called():
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
                    if len(self.__queue) < 1:
                        break
                    req = self.__queue.pop(0)
                    req.began = time()
                    self.__running.append(req)
                    try:
                        req.running_task = asyncio.get_event_loop().create_task(self.startRequest(req))
                    except Exception as e:
                        self.restartRequest(req)
                        log(f"""

                        Caught Exception
                        {e}
                        while getting
                        {req}
                        {req.url}

                        Traceback:
                        {traceback.format_exc()}

                        """,filename="exceptions.log")
            await asyncio.sleep(0.1)
