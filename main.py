import requests
from rich.pretty import pprint
import re
from dataclasses import dataclass
from datetime import datetime

BASE_URL = "https://2f0f8fc-az-westeurope-fsly.cdn.redbee.live/ukparliament/parliamentlive"

@dataclass
class ManifestExtensions:
    Master: str = ".msu8"
    Video180p: str = "vod-idx-video=300000.m3u8"
    Video360p: str = "vod-idx-video=850000.m3u8"
    Video576p: str = "vod-idx-video=1300000.m3u8"
    Video1080p: str = "vod-idx-video=3000000.m3u8"
    Audio: str = "vod-idx-audio_eng=64000.m3u8"


def fetch_manifest(asset_id: str, material_id: str, resolution: str) -> str:

    if resolution == "180p":
        manifest = ManifestExtensions.Video180p
    elif resolution == "360p":
        manifest = ManifestExtensions.Video360p
    elif resolution == "576p":
        manifest = ManifestExtensions.Video576p
    elif resolution == "1080p":
        manifest = ManifestExtensions.Video1080p
    else:
        raise ValueError(
            f"specified resolution: {resolution} is not valid. Valid formats are: '180p', '360p', '576p', '1080p'"
            )

    url = f"{BASE_URL}/assets/{asset_id}/materials/{material_id}/vod-idx.ism/{manifest}"

    response = requests.get(url)
    response.raise_for_status()

    return response.text


def main():
    asset_id = "03d096f3-4a94-4352-b351-70ad3bcb39cc_0D62A9b"
    material_id = "IAz5cD8Tg7_0D62A9b"
    resolution = "180p"

    manifest = fetch_manifest(asset_id=asset_id, material_id=material_id, resolution=resolution)
    lines: list[str] = [line for line in manifest.split("\n")]

    pprint(lines)

    duration_target = int([line.split(":") for line in lines if re.match(".*TARGETDURATION.*",line)][0][1])
    print(duration_target)

    start_time = datetime.fromisoformat([line.split(":")  for line in lines if re.match(".*PROGRAM-DATE-TIME.*", line)][0][1])
    print(start_time)

    segments_independant = bool([line for line in lines if re.match(".*INDEPENDANT.*", line)])
    print(segments_independant)


if __name__ == "__main__":
    main()
