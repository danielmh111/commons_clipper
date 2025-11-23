import requests
from rich.pretty import pprint
import re
from dataclasses import dataclass
from datetime import datetime, time
import math
from loguru import logger
from ratelimit import limits
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def parse_manifest_info(manifest: str) -> tuple[datetime, float]:
    lines: list[str] = [line for line in manifest.split("\n")]

    duration_target = int([line.split(":") for line in lines if re.match(".*TARGETDURATION.*",line)][0][1])
    actual_durations = [float(p) for line in lines for part in line.split(",") for p in part.split(":") if re.match("#EXTINF:", part) and not re.match("#EXTINF", p)]
    unique_durations = len(set(actual_durations))
    start_time = datetime.fromisoformat([line.split(":")  for line in lines if re.match(".*PROGRAM-DATE-TIME.*", line)][0][1])
    segments_independant = bool([line for line in lines if re.match(".*INDEPENDENT.*", line)])

    if not (segments_independant and unique_durations == 1):
        raise Exception("segments must be independant and the same duration for this logic to work")

    duration = actual_durations[0] if unique_durations else float(duration_target)

    return start_time, duration


def get_clip_bounds(stream_start: datetime, clip_start: str, clip_end: str, segment_duration: float) -> tuple[int, int]:

    date = stream_start.date()
    clip_start_time = time.fromisoformat(clip_start)
    clip_start_dt = datetime(date.year, date.month, date.day, clip_start_time.hour, clip_start_time.minute, clip_start_time.second)
    start_offset = clip_start_dt - stream_start

    start_segment = int(start_offset.seconds // segment_duration)

    clip_end_time = time.fromisoformat(clip_end)
    clip_end_dt = datetime(date.year, date.month, date.day, clip_end_time.hour, clip_end_time.minute, clip_end_time.second)
    end_offset = clip_end_dt - stream_start

    end_segment = math.ceil(end_offset.seconds/segment_duration)

    return start_segment, end_segment


def make_request(url: str, session: requests.Session):
    response = session.get(url=url, stream=True)
    logger.debug(f"status code: {response.status_code}")
    response.raise_for_status()

    return response


def main():
    asset_id = "03d096f3-4a94-4352-b351-70ad3bcb39cc_0D62A9b"
    material_id = "IAz5cD8Tg7_0D62A9b"
    resolution = "180p"

    manifest = fetch_manifest(asset_id=asset_id, material_id=material_id, resolution=resolution)
    start_time, segment_duration = parse_manifest_info(manifest=manifest)

    # gideon speaks at 14:53:14
    start = "14:53:14" # this is the format that will be found in the agenda/index
    end = "14:54:27"

    start_segment, end_segment = get_clip_bounds(start_time, start, end, segment_duration)

    files = [f"vod-idx-video=300000-{segment}.ts" for segment in range(start_segment, end_segment+1)]
    urls = [f"{BASE_URL}/assets/{asset_id}/materials/{material_id}/vod-idx.ism/{file}" for file in files]

    retry_logic = Retry(
        total=3,
        status_forcelist=[429, 500],
        backoff_factor=1,
        respect_retry_after_header=True,
    )
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=retry_logic))
        responses = [make_request(url, session) for url in urls]

    [pprint(response.content) for response in responses]


if __name__ == "__main__":
    main()
