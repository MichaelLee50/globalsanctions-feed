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

