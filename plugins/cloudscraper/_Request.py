from scraper import Request

class CloudscraperRequest(Request):
    def get_response(self, session):
        kwargs = {}
        if self.proxies is not None:
            kwargs["proxies"] = self.proxies
        if self.referrer is not None:
            kwargs["headers"] = {"Referer": self.referrer}
        response = session.get(self.url,**kwargs)
        return response