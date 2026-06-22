import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://globalsanctions.com/news/"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "Auto-generated feed"

count = 0

# Look for article titles (these are plain text blocks)
paragraphs = soup.find_all("p")

for p in paragraphs:
    text = p.get_text(strip=True)

    # Filter likely article titles (long enough, contains meaningful wording)
    if len(text) < 50:
        continue

    # Optional: look for sentences that look like article summaries
    if "." not in text:
        continue

    item = SubElement(channel, "item")
    SubElement(item, "title").text = text[:120]  # shorten title
    SubElement(item, "link").text = URL
    SubElement(item, "pubDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    count += 1
    if count >= 10:
        break

tree = ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

print(f"Feed generated with {count} items")
