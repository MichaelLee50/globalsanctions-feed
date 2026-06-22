import re
import requests
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://globalsanctions.com/news/"

response = requests.get(URL, timeout=30)
response.raise_for_status()

html = response.text

# Flatten the page text enough to make regex parsing reliable
text = re.sub(r"\s+", " ", html)

# Try to isolate the visible news block on the page
start_match = re.search(r"News\s+Home\s*>\s*News\s+\d+\s+to\s+\d+\s+of\s+\d+\s+results\s+", text)
end_match = re.search(r"Global Sanctions provides daily updates on sanctions news", text)

if start_match:
    start = start_match.end()
else:
    start = 0

if end_match:
    end = end_match.start()
else:
    end = len(text)

news_block = text[start:end]

# Pattern seen in the visible page content:
# HEADLINE DATE SUMMARY Read more
pattern = re.compile(
    r"(?P<title>.+?)\s+"
    r"(?P<date>\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\s+"
    r"(?P<summary>.+?)\s+Read more",
    re.DOTALL
)

matches = pattern.finditer(news_block)

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed from visible Global Sanctions news list"

count = 0
seen_titles = set()

for m in matches:
    title = m.group("title").strip()
    date = m.group("date").strip()
    summary = m.group("summary").strip()

    # Filter obvious junk
    if len(title) < 12:
        continue
    if title.lower() in seen_titles:
        continue

    # Remove any leading clutter that might bleed into the title
    for junk in [
        "News ",
        "Home > ",
        "Results ",
    ]:
        if title.startswith(junk):
            title = title.replace(junk, "", 1).strip()

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = URL
    SubElement(item, "description").text = summary
    SubElement(item, "pubDate").text = date

    seen_titles.add(title.lower())
    count += 1

# Write a valid feed even if zero items are found
tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
