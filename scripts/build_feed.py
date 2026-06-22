import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

URL = "https://globalsanctions.com/news/"
BASE = "https://globalsanctions.com"

r = requests.get(URL)
soup = BeautifulSoup(r.text, "html.parser")

items = soup.select("a[href]")

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom Feed)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed"

count = 0

for i in items:
    link = i.get("href")
    title = i.text.strip()

    if not link or not title:
        continue

    if "/news/" not in link:
        continue

    if len(title) < 10:
        continue

    full_link = link if link.startswith("http") else BASE + link

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = full_link
    SubElement(item, "pubDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    count += 1
    if count >= 20:
        break

with open("feed.xml", "wb") as f:
    f.write(tostring(rss))
