class db:
    name = "ffonline"
    user = "root"
    password = "root"
    port = 8889
    
    @classmethod
    def get(self, key, default = None):
        return getattr(self,key,default)

class __ffn_creds:
    def __init__(self, email = None, password = None,cookies = {}):
        self.email = email
        self.password = password
        self.cookies = dict(cookies)
    def update(self, email = None, password = None,cookies = {}):
        if email is not None:
            self.email = str(email)
        if password is not None:
            self.password = str(password)
        self.cookies.update(dict(cookies))

class creds:
    none = None

creds.ffn = __ffn_creds(
    cookies={
        "finn": "8b8e975eee8e75ef4fd31dc2660c29abbf98847849e2822aef3c4ec06a292179",
        "fknn": "4961361bc5f3b08c90227d946f467d97b7334cc642851c5742726d3682d481b7",
        "funn": "gofojom703"
    }
)
creds.ffn_authorPM1 = __ffn_creds(
    email="norig98466@brosj.net",
    password="fnjewknmfkmlkewr32u8jr8093j0940932",
    cookies={
        "finn": "01bcace25d884a9af8060542240166070954bd2a52159af94f352b4645ca53ab",
        "fknn": "8e2a12d8559c33743fc08cba1e03310eccb19dbb1e70008be671e056a46da806",
        "funn": "norga"
    }
)
creds.ffn_authorPM2 = __ffn_creds(
    email="libay27118@adeata.com",
    password="fnoj3wg9834h9f43hj98h98",
    cookies={
        "finn": "3a7076b1f20573efe68314f4da115e6df37b76bbd297c8a709c0196a0400e8f6",
        "fknn": "43e00bfa7abd7e853e53ee4332bb798aaea5f2c64dc6d5ecace25636bacce2fb",
        "funn": "libay"
    }
)
creds.ffn_authorPM3 = __ffn_creds(
    email="jasiyah.bud@eerees.com",
    password="fwnefnlewmifj843u8r34fdiu43",
    cookies={
        "finn": "7e5c855f2f2c27e251b8b1435d40d5cda430451c0c34c589e2b50c7392ef0928",
        "fknn": "49804582ceab7c4dad7c0ebdd9a295ca5c9bb883f57a15a36fd3a8d466162d16",
        "funn": "jasee"
    }
)
creds.ffn_authorPM4 = __ffn_creds(
    email="emarion.nyshawn@eerees.com",
    password="fnwoenmfo9843jr98439uf9m439ifn",
    cookies={
        "finn": "b705ecbb9888f2f80705ecfa32cf38d9194e5062af4347a0a077ceb966859c36",
        "fknn": "ddea595634b4b11c9c76b7bd8316a997fa3c9fcdf7a181dcf6264903523106ed",
        "funn": "pradra"
    }
)
creds.ffn_authorPM5 = __ffn_creds(
    email="lonnie.nashawn@eerees.com",
    password="gmkremglkmkwfm32mrflkm",
    cookies={
        "finn": "cb36a8f926aa14cfd2bf927f7dd15159ad94f28921ce920b3441b55c0dce7ac8",
        "fknn": "ccf1f9b4ac4ec301e85a216038acb35650642d63fbdd060c7c0b1cd8ecde4753",
        "funn": "franya"
    }
)

USE_PROXY = "http://192.81.133.72"