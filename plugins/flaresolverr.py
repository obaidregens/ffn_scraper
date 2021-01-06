from scraper import Request,Scraper
import requests
import atexit
import signal
import json
import random
from urllib.parse import urlparse,urlencode
from modules.utils import url_join
from modules.logging.dump import html

class FlaresolverrResponse:
    def __init__(self, solution):
        self.status_code = solution["headers"].get("status",0)
        self.cookies = solution["cookies"]
        self.headers = solution["headers"]
        self.text = solution["response"]
class FlaresolverrSession:
    def __init__(self,location,agent=None):
        if agent is None:
            try:
                with open("data/agents.json","r") as fp:
                    agent = random.choice(json.load(fp))
            except Exception:
                agent = ""
        self.location = location
        self.headers = {
            "Content-Type": "application/json"
        }
        res = requests.post(
            location,
            headers=self.headers,
            json=dict(
                cmd="sessions.create",
                userAgent=agent
            )
        )
        self.id = res.json()["session"]

        # catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
        # for sig in catchable_sigs:
        #     signal.signal(sig, self.destroy)

        atexit.register(self.destroy)
    def destroy(self,*args,**kwargs):
        res = requests.post(
            self.location,
            headers=self.headers,
            json=dict(
                cmd="sessions.destroy",
                session=self.id
            )
        )
    def request(self,url,cookies={},post=None,referrer=None):
        body = dict(
            cmd="request.get",
            url=url,
            session=self.id,
            cookies=FlaresolverrSession.parseCookies(cookies,url)
        )

        if post is not None:
            body["cmd"] = "request.post"
            body["postData"] = FlaresolverrSession.serializePostData(post)
            body["headers"] = {"Content-Type": "application/x-www-form-urlencoded"}
        
        if referrer is not None:
            body["headers"] = body.get("headers",{})
            body["headers"]["Referer"] = referrer

        res = requests.post(
            self.location,
            headers=self.headers,
            json=body
        )
        res = res.json()
        return FlaresolverrResponse(res["solution"])
    @classmethod
    def serializePostData(self,postData):
        return urlencode(postData)
    @classmethod
    def parseCookies(self,cookies_dict,url):
        cookies_list = []
        for name,value in cookies_dict.items():
            cookies_list.append(dict(
                name=name,
                value=value,
                domain=urlparse(url).netloc
            ))
        return cookies_list
class FlaresolverrRequest(Request):
    def __init__(
        self,
        url,
        callback=None,
        pass_on={},
        cookies={},
        post=None,
        referrer=None
    ):
        Request.__init__(
            self,
            url=url,
            callback=callback,
            pass_on=pass_on
        )
        self.post = post
        self.cookies = cookies
        self.referrer = referrer
    def get_response(self, session):
        response = session.request(
            self.url,
            cookies=self.cookies,
            post=self.post,
            referrer=self.referrer
        )
        return response
    def __repr__(self):
        return f"<Request: {self.url} Cookies={self.cookies} >"

class FlaresolverrScraper(Scraper):
    def __init__(self,location,base=None, agent=None ):
        self.__session = FlaresolverrSession(location,agent=agent)
        Scraper.__init__(self,base)
    async def startRequest(self,request):
        request.start(self.__session)
    def follow(self, request: Request):
        if self.base is None:
            raise Exception("Cannot follow, base is None")
        if request.referrer is not None:
            request.referrer = url_join(self.base,request.referrer)
        Scraper.follow(self,request)