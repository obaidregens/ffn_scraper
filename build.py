import subprocess
import os
from pprint import pprint
from shutil import copyfile
from modules.logging.main import make_way

def main():
    upload = input("Upload to SSH?").lower() == "y"
    if upload:
        upload = input("Sure?").lower() == "y"
    
    def isforUpload(path):
        toUpload = [
            "main.py",
            "requirements.txt",
            "modules",
            "data",
            "crawlers",
            "scraper",
            "plugins"
        ]
        if "__pycache__" in path: return False
        for f in toUpload:
            if path.startswith(f): return True
        return False

    source = "/Users/obaid/Documents/py-projects/ffn_scraper/"
    destination = "/Users/obaid/Documents/py-projects/ffn_scraper/temp/"

    paths = []
    for root,dirs,files in os.walk("."):
        for f in files:
            Path = os.path.join(root, f)[2:]
            if not isforUpload(Path):
                continue
            paths.append(Path)
            make_way(destination + Path)
            copyfile(source + Path,destination + Path)

    cmd = "rsync -azv " + destination + " ffonline:/home/runcloud/webapps/ffn_scraper/" 
    subprocess.call(cmd,shell=True)
    cmd = "rm -r " + destination
    subprocess.call(cmd,shell=True)

    if not upload:
        return

    print("Completed")
    

try:
    main()
except Exception as e:
    raise e
    input("Exit?")
