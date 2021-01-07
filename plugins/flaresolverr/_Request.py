from scraper import Request

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
            pass_on=pass_on,
            referrer=referrer
        )
        self.post = post
        self.cookies = cookies
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
