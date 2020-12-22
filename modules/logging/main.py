import os
def make_way(filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    return filename
def path(_path: str):
    return os.path.join("logs/",_path)
def log(line: str,filename: str = "main.log"):
    filename = make_way(path(filename))
    print(line)
    with open(filename, "a+") as dump:
        dump.write( str(line) + "\n" )