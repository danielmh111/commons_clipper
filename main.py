import requests
from rich.pretty import pprint
import re

URL = "https://2f0f8fc-az-westeurope-fsly.cdn.redbee.live/ukparliament/parliamentlive/assets/03d096f3-4a94-4352-b351-70ad3bcb39cc_0D62A9b/materials/IAz5cD8Tg7_0D62A9b/vod-idx.ism/.m3u8"

def main():
    response = requests.get(URL)
    pprint(response.status_code)
    pprint(response.text)

    text = response.text
    lines = [line for line in text.split("\n") if re.match(".*(vod-idx-((video)|(audio)|(audio_eng))+=[0-9]{5,7}.m3u8)", line)]

    pprint(lines)


if __name__ == "__main__":
    main()
