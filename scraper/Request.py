import requests

class Request:
    def __init__(
        self,
        url,
        callback=None,
        pass_on={},
        proxies=None,
        referrer=None
    ):
        self.url = url
        self.callback = Request.dummy
        if callback is not None:
            self.callback = callback
        self.proxies = proxies
        self.referrer = referrer
        self.pass_on = pass_on
    def get_response (self):
        kwargs = {}
        if self.proxies is not None:
            kwargs["proxies"] = self.proxies
        if self.referrer is not None:
            kwargs["headers"] = {"Referer": self.referrer}
        response = requests.get(self.url,**kwargs)
        return response
    def start(self,*args,**kwargs):
        response = self.get_response(*args,**kwargs)
        if self.callback is not None:
            self.callback(response=response,request=self,**self.pass_on)
    def __str__(self):
        return self.url
    def __repr__(self):
        return f"<Request: {self.url} >"

    @classmethod
    def dummy(self,response,request,**kwargs):
        pass