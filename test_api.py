import requests
from bs4 import BeautifulSoup
from rich.pretty import pprint

FEED_URL = "http://data.parliamentlive.tv/api/event/feed"


def find_recent_events() -> list[str]:
    response = requests.get(FEED_URL)
    html = BeautifulSoup(response.text, "lxml")
    urls = [str(url.get("xml:base")) for url in html.find_all("entry")]

    return urls


def main():
    urls = find_recent_events()
    pprint(urls)


if __name__ == "__main__":
    main()
