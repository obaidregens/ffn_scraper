import requests
class Request:
    def __init__(
        self,
        url,
        callback=None,
        pass_on={},
        proxies=None
    ):
        self.url = url
        self.callback = Request.dummy
        if callback is not None:
            self.callback = callback
        self.proxies = proxies
        self.pass_on = pass_on
    def get_response (self):
        kwargs = {}
        if self.proxies is not None:
            kwargs["proxies"] = self.proxies
        response = requests.get(self.url,**kwargs)
        return response
    def start(self,*args,**kwargs):
        response = self.get_response(*args,**kwargs)
        if self.callback is not None:
            self.callback(response=response,request=self,**self.pass_on)

    @classmethod
    def dummy(self,response,request,**kwargs):
        pass