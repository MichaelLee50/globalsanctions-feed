import re
from xml.etree.ElementTree import Element, SubElement, ElementTree
from playwright.sync_api import sync_playwright

URL = "https://globalsanctions.com/news/"

BAD_TITLES = {
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

date_re = re.compile(r"^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$")

def build_feed():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        text = page.locator("body").inner_text()
        browser.close()

    # Split the rendered page into clean visible lines
    lines = []
    for raw in text.splitlines():
        clean = " ".join(raw.split()).strip()
        if clean:
            lines.append(clean)

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Global Sanctions News (Custom RSS)"
    SubElement(channel, "link").text = URL
    SubElement(channel, "description").text = "Auto-generated feed from rendered Global Sanctions news list"

    seen = set()
    count = 0

    for i, line in enumerate(lines):
        if not date_re.match(line):
            continue

        if i == 0:
            continue

        title = lines[i - 1].strip()

        if title in BAD_TITLES:
            continue
        if len(title) < 12:
            continue
        if title.lower() in seen:
            continue

        # Grab a short summary from the next sensible line
        summary = ""
        for j in range(i + 1, min(i + 5, len(lines))):
            candidate = lines[j].strip()
            if not candidate:
                continue
            if date_re.match(candidate):
                break
            if candidate in BAD_TITLES:
                continue
            if candidate.lower() == "read more":
                continue
            if len(candidate) > 20:
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
        if count >= 20:
            break

    tree = ElementTree(rss)
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

    print(f"Feed generated with {count} items")

if __name__ == "__main__":
    build_feed()
