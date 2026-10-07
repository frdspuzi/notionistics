"""Regenerate the reviews marquee in index.html from fiverr_reviews.csv.

Usage: python -I tools/build_reviews.py fiverr_reviews.csv index.html

Rules (see AGENTS.md > Client privacy): 5-star reviews with a real sentence, one per reviewer,
countries with an SVG flag symbol in index.html. Credit = display_name when its confidence is
confirmed / from your reply / shown in your chats or orders (shown as "First L."), otherwise a masked username.
"""
import csv
import html
import re
import sys

FLAGS = {  # country -> flag symbol id in index.html
    "United States": "us", "Germany": "de", "United Kingdom": "gb", "Netherlands": "nl", "Estonia": "ee",
    "Indonesia": "id", "France": "fr", "Sweden": "se", "Japan": "jp", "Belgium": "be", "Ireland": "ie",
    "Denmark": "dk", "Spain": "es",
}
MIN_LEN, MAX_LEN = 45, 230
TRUSTED = ("confirmed", "from your reply", "shown as display name", "signs messages as")  # never "probable" / "matches username"


def masked(user):
    head, mid, tail = user[:2], user[2:-2], user[-2:]
    return f'{html.escape(head)}<span class="mask" aria-hidden="true">{"*" * len(mid)}</span>{html.escape(tail)}'


def credit(row):
    name, conf = row["display_name"].strip(), row["name_confidence"].strip()
    if name and conf.startswith(TRUSTED):
        first, *rest = name.split()
        return html.escape(f"{first} {rest[-1][0]}." if rest else first)
    return masked(row["username"])


def excerpt(text):
    """Verbatim, cut at a sentence boundary when long."""
    text = " ".join(text.split())
    if len(text) <= MAX_LEN:
        return text
    cut = max(text.rfind(p, 0, MAX_LEN) for p in (". ", "! ", "? "))
    return text[: cut + 1] + " …" if cut > MIN_LEN else text[:MAX_LEN].rsplit(" ", 1)[0] + " …"


STARS = '<div class="stars" role="img" aria-label="5 out of 5 stars">' + '<svg class="i" aria-hidden="true"><use href="#i-star"/></svg>' * 5 + "</div>"


AVATARS = {}  # username -> neutral file, from the private clients_map.csv (see main)


def years_ago(when):
    """'4 months ago' -> 0, '1 year ago' -> 1, '3 years ago' -> 3."""
    n, unit = when.split()[:2]
    return int(n) if unit.startswith("year") else 0


INTEGRATION_FLOWS = {
    "dvorakj": {
        "label": "Schematic of the integration: Typeform to Zapier to Kit",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("app-kit", "Kit")],
        "note": "Connected a 10-result quiz so each customer automatically receives the right follow-up email series for their answers.",
    },
    "donstein630": {
        "label": "Schematic of the integration: Typeform to Zapier to branching emails",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("app-kit", "Kit")],
        "note": "Updated survey logic so different answers guide people down separate follow-up paths with zero duplicate emails.",
    },
    "mhome12345": {
        "label": "Schematic of the integration: Zapier to Notion to email alerts",
        "nodes": [("app-zapier", "Zapier"), ("app-notion", "Notion"), ("i-mail", "Email alerts")],
        "note": "Diagnosed why email alerts were delayed, fixed missing form fields, and got instant notifications delivering reliably.",
    },
    "designmediaz": {
        "label": "Schematic of the integration: Typeform to Zapier to Shopify",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("app-shopify", "Shopify")],
        "note": "Repaired broken product order forms so customer selections and checkout details sync straight into the store again.",
    },
    "lesj82": {
        "label": "Schematic of the integration: Typeform to Zapier to Custom API",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("i-code", "Custom API (POST)")],
        "note": "Form submissions were failing to connect to their partner system. Re-formatted name fields and restored data delivery.",
    },
    "antoine123nyc": {
        "label": "Schematic of the integration: Typeform to Zapier to notifications",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("i-mail", "Notifications")],
        "note": "Built custom intake routing and automated alerts so the team gets notified immediately on every new booking enquiry.",
    },
    "sdgreal": {
        "label": "Schematic of the integration: Outlook to Zapier to Notion",
        "nodes": [("app-outlook", "Outlook"), ("app-zapier", "Zapier"), ("app-notion", "Notion")],
        "note": "Order emails were creating cluttered cards in Notion. Cleaned up card titles and added an automated 14-day follow-up.",
    },
    "pursuitcompany": {
        "label": "Schematic of the integration: PDF products to Squarespace to downloads",
        "nodes": [("i-file", "Digital PDFs"), ("i-cart", "Squarespace"), ("i-cloud", "Auto Downloads")],
        "note": "Set up an automated digital shop so buyers receive their downloadable PDF files immediately after checkout.",
    },
    "angelajudith1": {
        "label": "Schematic of the integration: Outlook to Zapier to Notion",
        "nodes": [("app-outlook", "Outlook"), ("app-zapier", "Zapier"), ("app-notion", "Notion")],
        "note": "Moving emails into subfolders was creating duplicate cards in Notion. Fixed tracking IDs to stop duplicate entries.",
    },
    "heartwebdesign": {
        "label": "Schematic of the integration: Typeform to Zapier to Notion",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("app-notion", "Notion")],
        "note": "Client intake answers were being copied by hand. Automated form responses directly into individual Notion properties.",
    },
    "jonathanbent122": {
        "label": "Schematic of the integration: Squarespace to Zapier to Google Drive",
        "nodes": [("i-cart", "Squarespace"), ("app-zapier", "Zapier"), ("app-drive", "Google Sheets")],
        "note": "New store orders were not logging automatically. Connected new purchases to populate the central team spreadsheet instantly.",
    },
    "federicoboc": {
        "label": "Schematic of the integration: Typeform to Zapier to CRM",
        "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("i-users", "Engagebay CRM")],
        "note": "Customer questionnaire responses were missing in CRM. Connected form submissions directly to matching contact profiles.",
    },
    "erikaepuise": {
        "label": "Schematic of the integration: Notion database formulas and dashboard",
        "nodes": [("app-notion", "Notion DB"), ("i-code", "Formulas"), ("i-db", "Dashboard")],
        "note": "Finance tracker had broken formulas and progress views. Fixed database calculations and cleaned up layout views.",
    },
    "leerichards263": {
        "label": "Schematic of the integration: Google Sheets to Zapier to Notion",
        "nodes": [("app-drive", "Google Sheets"), ("app-zapier", "Zapier"), ("app-notion", "Notion")],
        "note": "Spreadsheet entries stopped appearing in Notion due to a changed column format. Fixed field types and secured the database.",
    },
    "mallaryk": {
        "label": "Schematic of the integration: Notion client portal and permissions",
        "nodes": [("app-notion", "Notion Portal"), ("i-users", "Permissions"), ("i-db", "Client Views")],
        "note": "Client portal was exposing shared views across clients. Configured database permissions so each client sees only their own data.",
    },
}

DEFAULT_FLOW = {
    "label": "Schematic of the integration: Typeform to Zapier to Notion",
    "nodes": [("app-typeform", "Typeform"), ("app-zapier", "Zapier"), ("app-notion", "Notion")],
    "note": "Rebuilt workflow connection and verified form responses map to the right fields without data loss.",
}


def flow_art(username):
    flow = INTEGRATION_FLOWS.get(username, DEFAULT_FLOW)
    items = []
    for i, (icon_id, text) in enumerate(flow["nodes"]):
        if i > 0:
            items.append('<svg class="i arrow" aria-hidden="true"><use href="#i-arrow"/></svg>')
        icon_cls = "app-mark" if icon_id.startswith("app-") else "i"
        items.append(f'<span class="node"><svg class="{icon_cls}" aria-hidden="true"><use href="#{icon_id}"/></svg> {html.escape(text)}</span>')
    nodes_html = "".join(items)
    note = flow.get("note")
    note_html = (f'<div class="snap-note"><svg class="i" aria-hidden="true"><use href="#i-check"/></svg> '
                 f'<span><strong>Fixed:</strong> {html.escape(note)}</span></div>') if note else ""
    return (f'<div class="review-art review-flow" role="img" aria-label="{html.escape(flow["label"])}">'
            f'<div class="snap-bar"><span></span><span></span><span></span></div>'
            f'<div class="v-flow">{nodes_html}</div>'
            f'{note_html}</div>')


def card(row, repeat):
    is_api = row["gig"].startswith("API")
    kind = "integration fix" if is_api else "avatar"
    if repeat:
        kind += " · repeat client"
    country = row["country"]
    face = AVATARS.get(row["username"])
    if is_api:
        art = flow_art(row["username"])
        has_art = True
    elif face:
        art = (f'<div class="review-art"><img src="{face}" width="200" height="240" loading="lazy" draggable="false" '
               f'alt="Their Notion-style avatar, drawn by Notionistics"></div>')
        has_art = True
    else:
        art = ""
        has_art = False
    return (f'<figure class="review{" has-art" if has_art else ""}" data-years="{years_ago(row["when"])}">{art}<div class="review-body">'
            f'<blockquote>"{html.escape(excerpt(row["review"]))}"</blockquote>'
            f'<figcaption>{STARS}<span><svg class="flag" role="img" aria-label="{country}"><use href="#f-{FLAGS[country]}"/></svg> '
            f"{credit(row)} · {kind}</span></figcaption></div></figure>")


def row_html(cards, label):
    group = "".join(cards)
    return (f'    <div class="marquee" role="region" aria-label="{label}" tabindex="0">\n'
            f'      <div class="marquee-track">\n'
            # three copies: the visitor starts on the middle one; JS wraps scrollLeft by one copy's width
            f'        <div class="marquee-group" aria-hidden="true" inert>{group}</div>\n'
            f'        <div class="marquee-group">{group}</div>\n'
            f'        <div class="marquee-group" aria-hidden="true" inert>{group}</div>\n'
            f"      </div>\n    </div>\n")


def main(csv_path, page_path, map_path="clients_map.csv"):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    try:  # private, git-ignored: username -> assets/clients/cNN.svg
        AVATARS.update({r["username"]: r["file"] for r in csv.DictReader(open(map_path, encoding="utf-8"))})
    except FileNotFoundError:
        pass
    counts = {}
    for r in rows:
        counts[r["username"]] = counts.get(r["username"], 0) + 1
    best = {}
    for r in rows:
        if r["rating"] != "5" or r["country"] not in FLAGS or len(r["review"].strip()) < MIN_LEN:
            continue
        if len(r["review"]) > len(best.get(r["username"], {"review": ""})["review"]):
            best[r["username"]] = r
    picked = sorted(best.values(), key=lambda r: int(r["#"]))  # CSV order = newest first
    cards = [card(r, counts[r["username"]] > 1 or r["tag"]) for r in picked]  # one row, newest first

    block = ("    <!-- reviews:start (generated by tools/build_reviews.py) -->\n"
             + row_html(cards, "Client reviews")
             + "    <!-- reviews:end -->\n")
    page = open(page_path, encoding="utf-8").read()
    page, n = re.subn(r"    <!-- reviews:start.*?<!-- reviews:end -->\n", lambda m: block, page, flags=re.S)
    assert n == 1, "reviews markers not found"
    for r in rows:  # full usernames must never reach the page
        assert r["username"] not in page, r["username"]
    open(page_path, "w", encoding="utf-8").write(page)
    print(f"{len(cards)} reviews")


if __name__ == "__main__":
    main(*sys.argv[1:3])
