import requests
import random
import json
import atexit
from urllib.parse import urlparse,urlencode

from plugins.flaresolverr import Response

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
        return Response(res["solution"])
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
