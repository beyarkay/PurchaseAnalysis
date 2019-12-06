import sys
DOWNLOAD_HTML = False

def scrape_cars():

    pass


def scrape_houses():
    pass


def dev_main():
    pass


def main():
    projects = sys.argv[1:]
    if "cars" in projects:
        scrape_cars()
    if "houses" in projects:
        scrape_houses()


if __name__ == '__main__':
    print(sys.argv)
    main()
