import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
from urllib.parse import urljoin

URL = "https://globalsanctions.com/news/"
BASE = "https://globalsanctions.com"

response = requests.get(URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed"

seen = set()
count = 0

# Strategy:
# The page pattern appears to be headline + date + summary + "Read more".
# So only use links whose text is exactly "Read more", then pull the nearest heading nearby.

read_more_links = []
for a in soup.find_all("a", href=True):
    text = a.get_text(" ", strip=True)
    if text.lower() == "read more":
        read_more_links.append(a)

def find_title_for_link(a_tag):
    # Look up a few parent levels and search for headings in the same block
    node = a_tag
    for _ in range(6):
        if node is None:
            break

        # Prefer headings in this block
        for tag_name in ["h1", "h2", "h3", "h4"]:
            heading = node.find(tag_name)
            if heading:
                title = heading.get_text(" ", strip=True)
                if title and len(title) > 8:
                    return title

        node = node.parent

    return None

for a in read_more_links:
    href = a.get("href", "").strip()
    if not href:
        continue

    full_link = urljoin(BASE, href)

    # Ignore obvious non-news paths
    bad_bits = [
        "/region/",
        "/sanctioning-states/",
        "/guidance/",
        "/licensing/",
        "/enforcement/",
        "/judgments/",
        "/register",
        "/login",
        "/subscribe",
    ]
    if any(bit in full_link for bit in bad_bits):
        continue

    title = find_title_for_link(a)
    if not title:
        continue

    if title in seen:
        continue
    seen.add(title)

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = full_link
    SubElement(item, "pubDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    count += 1
    if count >= 20:
        break

# If nothing was found, write an empty but valid feed
tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
