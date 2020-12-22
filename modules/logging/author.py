from modules.logging.main import log as log_main

def log(author_ID,num_stories,storyIDs_imported):
    imported_string = ", ".join(map(str,storyIDs_imported))
    if imported_string == "":
        imported_string = None
    log_main(f"""

        Crawled Author {author_ID} with {num_stories} stories
        Story IDs updated and crawled: {imported_string}
        
    """)