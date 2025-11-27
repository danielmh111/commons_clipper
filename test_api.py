import json
from typing import Any
from uuid import uuid4

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


def extract_playback_url(embedding_code: list[str]) -> list[str | Any]:
    iframes = [
        BeautifulSoup(code).find("iframe", id="UKPPlayer") for code in embedding_code
    ]

    return [iframe.get("src") for iframe in iframes]


def get_session_token():
    response = requests.post(
        "https://exposure.api.redbee.live/v2/customer/UKParliament/businessunit/ParliamentLive/auth/anonymous",
        json={
            "device": {"type": "WEB", "name": "Python script"},
            "deviceId": str(uuid4()),
        },
    )
    return response.json().get("sessionToken")


def get_asset_material_ids(event_ids, session_token) -> list[tuple[str, str]]:
    source_urls = [
        f"https://exposure.api.redbee.live/v2/customer/UKParliament/businessunit/ParliamentLive/entitlement/{event_id}_0D62A9b/play"
        for event_id in event_ids
    ]

    responses = [
        requests.get(
            url=source_url, headers={"Authorization": f"Bearer {session_token}"}
        )
        for source_url in source_urls
    ]

    data: list[dict] = [response.json() for response in responses]
    ids = [(datum.get("assetId", ""), datum.get("materialId", "")) for datum in data]

    return ids


def main():
    event_urls = find_recent_events()
    print("\n", "" * 80, "\n")
    print("URLS:")
    pprint(event_urls)
    print("\n", "" * 80, "\n")

    # responses = [requests.get(url) for url in event_urls]

    # event_html = [BeautifulSoup(response.text, "lxml") for response in responses]
    event_ids = [url.split("/")[-1] for url in event_urls]

    # for id, html in zip(event_ids, event_html):
    #     with open(f"html/{id}.html", "w+", encoding="utf-8") as f:
    #         f.write(str(html))

    # main_video_info = request_main_video(event_ids=event_ids)

    # for event_id, info in main_video_info.items():
    #     with open(f"json/{event_id}.json", "w+") as f:
    #         f.write(json.dumps(info))

    # embedded_code = [info.get("embedCode", "") for info in main_video_info.values()]

    # print("\n", "" * 80, "\n")
    # print("CODE:")
    # pprint(embedded_code)
    # print("\n", "" * 80, "\n")

    # playback_urls = extract_playback_url(embedded_code)

    # print("\n", "" * 80, "\n")
    # print("PLAYBACK URL:")
    # pprint(playback_urls)
    # print("\n", "" * 80, "\n")

    # playback_responses = [requests.get(url) for url in playback_urls]

    # recorded_playback_responses = {
    #     event_id: requests.get(
    #         f"https://videoplayback.parliamentlive.tv/Player/Recorded/{event_id}?audioOnly=False&autoStart=False"
    #     )
    #     for event_id in event_ids
    # }

    # for event_id, response in recorded_playback_responses.items():
    #     with open(f"recorded_playback/{event_id}.html", "w+") as f:
    #         f.write(str(response.text))

    session_token = get_session_token()
    ids = get_asset_material_ids(event_ids=event_ids, session_token=session_token)

    pprint(ids)


if __name__ == "__main__":
    main()
