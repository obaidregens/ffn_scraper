if __name__ == "__main__":
    from sys import argv
    from os import listdir
    from importlib import import_module

    available = []
    for fn in listdir("scrapers"):
        if fn[-3:] == ".py" and fn != ".py":
            available.append(fn[:-3])
    if len(available) < 1:
        raise Exception("No Scrapers defined!")
    opt = ""
    if len(argv) > 1:
        opt = argv[1]
    while opt not in available:
        opt = input("Scraper?")

    module = import_module("scrapers." + opt)
    if not hasattr(module,"main"):
        raise Exception("Scraper has no 'main' function defined")

    module.main()