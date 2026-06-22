import re
import requests
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://globalsanctions.com/news/"

response = requests.get(URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Flatten visible text in page order
lines = []
for s in soup.stripped_strings:
    text = " ".join(str(s).split()).strip()
    if text:
        lines.append(text)

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed from visible Global Sanctions news list"

date_re = re.compile(r"^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$")

bad_titles = {
    "News",
    "Home > News",
    "Sanctions regimes",
    "Geographic regimes",
    "Thematic regimes",
    "Expired regimes",
    "Sanctioning states",
    "Target Search",
    "Guidance",
    "Licensing",
    "Enforcement",
    "Judgments & arbitration",
    "Arbitration",
    "Subscription",
    "Register for free email alerts",
    "Subscribe for full access",
    "Login",
    "About",
    "FAQ",
    "Contact",
    "Read more",
}

seen = set()
count = 0

# Find lines that are dates, then take the previous line as headline
for i, line in enumerate(lines):
    if not date_re.match(line):
        continue

    if i == 0:
        continue

    title = lines[i - 1].strip()

    if title in bad_titles:
        continue

    # Ignore obvious non-headlines
    if len(title) < 15:
        continue
    if title.lower().startswith("news home"):
        continue
    if "target search" in title.lower():
        continue
    if title.lower() in seen:
        continue

    # Optional summary: next non-date, non-junk line after the date
    summary = ""
    for j in range(i + 1, min(i + 4, len(lines))):
        candidate = lines[j].strip()
        if not candidate:
            continue
        if date_re.match(candidate):
            break
        if candidate in bad_titles:
            continue
        if candidate.lower() == "read more":
            continue
        if len(candidate) > 25:
            summary = candidate
            break

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = URL
    if summary:
        SubElement(item, "description").text = summary
    SubElement(item, "pubDate").text = line

    seen.add(title.lower())
    count += 1

# Write feed.xml
tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
