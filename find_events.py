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


def find_ids_for_recent_events():
    event_urls = find_recent_events()
    event_ids = [url.split("/")[-1] for url in event_urls]

    session_token = get_session_token()

    ids = get_asset_material_ids(event_ids=event_ids, session_token=session_token)

    pprint(ids)
