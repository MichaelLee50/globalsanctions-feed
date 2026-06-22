import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://globalsanctions.com/news/"
BASE = "https://globalsanctions.com"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed"

count = 0
seen = set()

for a in soup.find_all("a"):
    title = a.get_text(strip=True)
    href = a.get("href")

    if not title or not href:
        continue

    # Only keep links with meaningful article titles
    if len(title) < 30:
        continue

    # Ignore navigation junk
    if "Read more" in title:
        continue

    full_link = href if href.startswith("http") else BASE + href

    if full_link in seen:
        continue
    seen.add(full_link)

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = full_link
    SubElement(item, "pubDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    count += 1
    if count >= 15:
        break

tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
