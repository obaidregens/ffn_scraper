import os
def path(path: str):
    return os.path.join("logs/",path)
def log(line: str,filename: str = "main.log"):
    filename = path(filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print(line)
    with open(filename, "a+") as dump:
        dump.write( line + "\n" )