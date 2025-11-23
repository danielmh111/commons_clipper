import requests
from rich.pretty import pprint
import re
from dataclasses import dataclass

BASE_URL = "https://2f0f8fc-az-westeurope-fsly.cdn.redbee.live/ukparliament/parliamentlive"

@dataclass
class ManifestExtensions:
    Master: str = ".msu8"
    Video180p: str = "vod-idx-video=300000.m3u8"
    Video360p: str = "vod-idx-video=850000.m3u8"
    Video576p: str = "vod-idx-video=1300000.m3u8"
    Video1080p: str = "vod-idx-video=3000000.m3u8"
    Audio: str = "vod-idx-audio_eng=64000.m3u8"



def main():
    asset_id = "03d096f3-4a94-4352-b351-70ad3bcb39cc_0D62A9b"
    material_id = "IAz5cD8Tg7_0D62A9b"
    manifest = ManifestExtensions.Video180p

    url = f"{BASE_URL}/assets/{asset_id}/materials/{material_id}/vod-idx.ism/{manifest}"
    pprint(url)

    response = requests.get(url)
    pprint(response.status_code)
    
    text = response.text
    pprint(text)


if __name__ == "__main__":
    main()
