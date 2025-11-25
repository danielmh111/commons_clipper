import requests
from bs4 import BeautifulSoup
from rich.pretty import pprint

url = "http://data.parliamentlive.tv/api/event/feed"

response = requests.get(url)

text = response.text

soup = BeautifulSoup(text, "lxml")

readable = soup.prettify()

print(readable)
