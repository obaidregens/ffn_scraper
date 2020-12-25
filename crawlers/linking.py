def main():
    from scrapy.selector import Selector
    from time import time
    from modules.mysql_connection import (
        db,
        connection as sql_connection,
        insert as dbInsert
    )
    from modules.logging.main import log
    from plugins.flaresolverr import (
        FlaresolverrScraper as Scraper,
        FlaresolverrRequest as Request
    )
    from settings import creds
    cookies = creds.ffn.cookies

    t = time()
    db.execute(
        f"""
        SELECT uc.ID,uc.connection_user,uc.user_id,vc.code
        FROM user_connections as uc
        INNER JOIN verification_codes as vc ON vc.ID = uc.verification_ID
        WHERE uc.connection_from = 'ffn'
        AND uc.status = 'unverified'
        AND vc.issued > {t - (60*60*24*7)}
        """
    )
    user_codes = {}
    for row in db.fetchall():
        code = row.pop(-1)
        ID,ffn_user,user_id = map(int,row)
        user_codes[ffn_user] = {
            "ID": ID,
            "user_id": user_id,
            "code": code
        }

    def verify(user,code):
        fn = "verifications.log"
        log(f"""
        Verifying connection for user {user} with code {code}""",fn)
        user = int(user)
        if user not in user_codes:
            log("""Verification request for user does not exist
            """,fn)
            return False
        realCode = user_codes[user]["code"]
        if realCode != code:
            log(f"""The actual code is {realCode}, rejected.
            """,fn)
            return False
        
        db.execute(
            """
            UPDATE user_connections
            SET status = 'verified',
            link_timestamp = %s
            WHERE ID = %s
            """,
            [t, user_codes[user]["ID"]]
        )
        user_id = user_codes[user]["user_id"]
        dbInsert("notifications",{
            "user_id": user_id,
            "notification_type": "account_verified",
            "type_of": "user",
            "type_of_id": user_id,
            "type_by": "ffn_user",
            "type_by_id": user,
            "email_status": "none",
            "timestamp": time()
        })

        log("""Succesfully Verified!
        """,fn)
        return True

    s = Scraper(
        "http://192.46.223.28:8191/v1",
        base="https://www.fanfiction.net/"
    )
    def Conversation(response, request):
        sel = Selector(text=response.text)
        response = None
        last_msg = sel.css('.round8.bubbledRight')[-1]
        code = last_msg.xpath('img[1]/following-sibling::text()').get()
        Author_ID = sel.css('#gui_table2i > tbody > tr:nth-child(2) > td:nth-child(2) > a:nth-of-type(1)::attr(href)').get()[3:].rstrip('/')
        verify(Author_ID,code)

    def Inbox(response, request):
        sel = Selector(text=response.text)
        response = None
        convs = sel.css('#content_wrapper_inner > table .bubbledNNormal > a:nth-of-type(2)::attr(href)').getall()
        for conv in convs:
            s.follow(Request(
                "/pm2/"+conv,
                callback=Conversation,
                cookies=cookies
            ))

    s.follow(Request(
        "/pm2/inbox.php",
        cookies=cookies,
        callback=Inbox
    ))