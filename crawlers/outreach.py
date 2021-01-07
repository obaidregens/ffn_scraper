def main():
    from scrapy.selector import Selector
    import time
    from modules.users.connection import toMessage,sendUser
    from modules.logging.dump import html
    from modules.logging.main import log
    from data import message
    from plugins.flaresolverr import (
        Scraper,
        Request
    )
    import settings

    flaresolverr_location = getattr(settings,"SENDER_FLARESOLVERR_PROXY",None)
    if flaresolverr_location is None:
        raise Exception("No SENDER_FLARESOLVERR_PROXY specified")    

    s = Scraper(
        flaresolverr_location
    )

    authorIds = toMessage()

    rotating_cookies = [
        settings.creds.ffn_authorPM1.cookies,
        settings.creds.ffn_authorPM2.cookies,
        settings.creds.ffn_authorPM3.cookies,
        settings.creds.ffn_authorPM4.cookies,
        settings.creds.ffn_authorPM5.cookies
    ]
    queue = []

    last_sent = {}
    def continue_request():
        if len(queue) > 0:
            s.add(queue.pop(0))
    
    def Submit(response,request,authorId,username):
        last_sent[request.cookies["funn"]] = time.time()
        sel = Selector(text=response.text)
        html(response.text)
        res = sel.css('#xpreview.zhide + div + div::attr(class)').get()
        if res == "panel_success":
            sendUser(authorId)
            log(f"Sent: {authorId}")
            continue_request()
        elif res == "panel_warning":
            log(sel.css("#xpreview.zhide + div + div").get())
            log(f"Unsent: {authorId}")
            continue_request()

    def NewMessage(response,request,authorId,username):
        while (time.time() - last_sent.get(request.cookies["funn"],0)) <= 35:
            time.sleep(5)
            log("Sleep")

        sel = Selector(text=response.text)
        
        disabled_err = sel.css('.panel_warning > .gui_warning::text').get()
        if disabled_err == "Private Message Posting Denied":
            continue_request()
            return

        postData = {}
        for _input in sel.css("#fpost input,#fpost textarea"):
            postData[_input.attrib["name"]] = _input.attrib.get("value",None)
            
        postData["subject"] = message.subject.replace("###USERNAME###",username)
        postData["message"] = message.content.replace("###USERNAME###",username)

        s.follow(request.url,Request(
            f"/pm2/post.php?uid={authorId}",
            cookies=request.cookies,
            callback=Submit,
            pass_on=dict(authorId=authorId,username=username),
            post=postData
        ))
    print("Full: " + str(len(authorIds)))
    for authorId,username in authorIds.items():
        index = int(int((len(queue)/5*10)%10)/2)
        cookies = rotating_cookies[index]
        queue.append(Request(
            f"https://www.fanfiction.net/pm2/post.php?uid={authorId}",
            cookies=cookies,
            callback=NewMessage,
            pass_on=dict(authorId=authorId,username=username)
        ))
    s.add(queue.pop(0))