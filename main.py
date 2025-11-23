import requests
from rich.pretty import pprint
import re
from dataclasses import dataclass
from datetime import datetime, time
import math


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

    match resolution:
        case "180p":
            manifest = ManifestExtensions.Video180p
        case "360p":
            manifest = ManifestExtensions.Video360p
        case "576p":
            manifest = ManifestExtensions.Video576p
        case "1080p":
            manifest = ManifestExtensions.Video1080p
        case _:
            raise ValueError(
                f"specified resolution {resolution} is not valid. Valid formats are: '180p', '360p', '576p', '1080p'"
                )

    url = f"{BASE_URL}/assets/{asset_id}/materials/{material_id}/vod-idx.ism/{manifest}"

    response = requests.get(url)
    response.raise_for_status()

    return response.text


# gideon speaks at 14:53:14

def main():
    asset_id = "03d096f3-4a94-4352-b351-70ad3bcb39cc_0D62A9b"
    material_id = "IAz5cD8Tg7_0D62A9b"
    resolution = "180p"

    manifest = fetch_manifest(asset_id=asset_id, material_id=material_id, resolution=resolution)
    lines: list[str] = [line for line in manifest.split("\n")]

    duration_target = int([line.split(":") for line in lines if re.match(".*TARGETDURATION.*",line)][0][1])
    actual_durations = [float(p) for line in lines for part in line.split(",") for p in part.split(":") if re.match("#EXTINF:", part) and not re.match("#EXTINF", p)]
    unique_durations = len(set(actual_durations))
    start_time = datetime.fromisoformat([line.split(":")  for line in lines if re.match(".*PROGRAM-DATE-TIME.*", line)][0][1])
    segments_independant = bool([line for line in lines if re.match(".*INDEPENDENT.*", line)])

    stream_start: time = start_time.time()
    date = start_time.date()
    clip_start = time.fromisoformat("14:53:14")
    clip_start_dt = datetime(date.year, date.month, date.day, clip_start.hour, clip_start.minute, clip_start.second)
    start_offset = clip_start_dt - start_time
    print(start_offset)

    if segments_independant and unique_durations == 1:
        start_segment = int(start_offset.seconds // actual_durations[0])
        print(start_segment)    

    clip_end = time.fromisoformat("14:54:27")
    clip_end_dt = datetime(date.year, date.month, date.day, clip_end.hour, clip_end.minute, clip_end.second)
    end_offset = clip_end_dt - start_time

    if segments_independant and unique_durations == 1:
        end_segment = math.ceil(end_offset.seconds/actual_durations[0])
        print(end_segment)


if __name__ == "__main__":
    main()
