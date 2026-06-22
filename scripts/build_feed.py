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

# ✅ TARGET: headings in the news list
for item in soup.find_all("h3"):
    title = item.get_text(strip=True)

    if not title or len(title) < 10:
        continue

    # Look for link inside or nearby
    link_tag = item.find_parent("a") or item.find("a")

    if link_tag and link_tag.get("href"):
        href = link_tag.get("href")
    else:
        # fallback: use page
        href = URL

    if not href.startswith("http"):
        href = BASE + href

    entry = SubElement(channel, "item")
    SubElement(entry, "title").text = title
    SubElement(entry, "link").text = href
    SubElement(entry, "pubDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    count += 1
    if count >= 10:
        break

tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
