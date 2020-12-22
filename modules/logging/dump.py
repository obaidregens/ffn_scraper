import os
from modules.logging.main import make_way,path as log_path
from time import time

def path(_path):
    return log_path(os.path.join("html/",_path))
def html(html,filename: str = str(time()) + ".html"):
    filename = make_way(path(filename))
    with open(filename,"w+") as dump:
        dump.write(html)
