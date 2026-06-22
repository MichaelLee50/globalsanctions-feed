import re
import requests
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://globalsanctions.com/news/"

response = requests.get(URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Turn the page into ordered visible text lines
raw_lines = soup.get_text("\n").splitlines()
lines = []
for line in raw_lines:
    clean = " ".join(line.split()).strip()
    if clean:
        lines.append(clean)

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed from visible Global Sanctions news list"

date_re = re.compile(r"^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$")

bad_titles = {
    "News",
    "Sanctions regimes",
    "Geographic regimes",
    "Thematic regimes",
    "Expired regimes",
    "Sanctioning states",
    "Arbitration",
    "Subscription",
    "Register for free email alerts",
    "Subscribe for full access",
    "Login",
    "About",
    "FAQ",
    "Contact",
}

items_found = 0
seen = set()

for i, line in enumerate(lines):
    if not date_re.match(line):
        continue

    # The visible page pattern should be:
    # previous line = headline
    # current line = date
    # next line = summary
    if i == 0:
        continue

    title = lines[i - 1].strip()

    if title in bad_titles:
        continue

    if len(title) < 12:
        continue

    if title.lower() in seen:
        continue

    summary = ""
    if i + 1 < len(lines):
        next_line = lines[i + 1].strip()
        if next_line and not date_re.match(next_line) and len(next_line) > 20:
            summary = next_line

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = URL
    if summary:
        SubElement(item, "description").text = summary
    SubElement(item, "pubDate").text = line

    seen.add(title.lower())
    items_found += 1

# Write the feed
tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {items_found} items")
