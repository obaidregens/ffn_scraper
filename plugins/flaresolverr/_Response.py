class FlaresolverrResponse:
    def __init__(self, solution):
        self.status_code = solution["headers"].get("status",0)
        self.cookies = solution["cookies"]
        self.headers = solution["headers"]
        self.text = solution["response"]