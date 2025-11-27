import json

import requests
from bs4 import BeautifulSoup
from rich.pretty import pprint

FEED_URL = "http://data.parliamentlive.tv/api/event/feed"


def find_recent_events() -> list[str]:
    response = requests.get(FEED_URL)
    html = BeautifulSoup(response.text, "lxml")
    urls = [str(url.get("xml:base")) for url in html.find_all("entry")]

    return urls


def request_main_video(event_ids: list[str]) -> dict[str, dict]:
    video_responses = {
        event_id: requests.get(
            f"https://parliamentlive.tv/Event/GetMainVideo/{event_id}"
        )
        for event_id in event_ids
    }

    return {event_id: response.json() for event_id, response in video_responses.items()}


def main():
    event_urls = find_recent_events()
    pprint(event_urls)

    # responses = [requests.get(url) for url in event_urls]
    # event_html = [BeautifulSoup(response.text, "lxml") for response in responses]

    event_ids = [url.split("/")[-1] for url in event_urls]

    # for id, html in zip(event_ids, event_html):
    #     with open(f"html/{id}.html", "w+") as f:
    #         f.write(str(html.string))

    main_video_info = request_main_video(event_ids=event_ids)

    for event_id, info in main_video_info.items():
        with open(f"json/{event_id}.json", "w+") as f:
            f.write(json.dumps(info))

    embedded_code = [info.get("embedCode") for info in main_video_info.values()]

    pprint(embedded_code)


if __name__ == "__main__":
    main()
