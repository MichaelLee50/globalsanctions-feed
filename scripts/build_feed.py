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

for article in soup.find_all("a"):
    title = article.get_text(strip=True)
    link = article.get("href")

    if not title or not link:
        continue

    # ✅ Only include article links (these contain readable sentences)
    if len(title) < 40:
        continue

    # ✅ Exclude navigation / categories
    bad_words = ["sanctions regimes", "guidance", "licensing", "enforcement",
                 "judgments", "register", "login", "subscribe"]

    if any(word in title.lower() for word in bad_words):
        continue

    full_link = link if link.startswith("http") else BASE + link

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
    if count >= 10:
        break

tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
