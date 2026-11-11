"""Weekly check of Columbia's Graham & Doddsville archive page.

What it does:
  1. Reads robots.txt and stops if the archive page is not allowed for us.
  2. Downloads the archive page once (no PDFs: robots.txt disallows them).
  3. Compares the list of issues with what the index already knows.
     - New issue: writes a draft file in data/issues/ and notes it in alert.md.
     - Known issue whose PDF link changed: notes old and new link in alert.md.
       It does NOT change the link; Ezra approves that by hand.
     - Known issue missing from the page: notes it in alert.md. Nothing is deleted.
  4. If the page can't be read or looks broken (far fewer links than before),
     it writes alert.md and changes nothing.

alert.md is what the workflow turns into a GitHub issue. No alert.md = all good.

Run locally against a saved copy:  python scripts/check.py --html saved.html
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ALERT = ROOT / "alert.md"
SEEN = DATA / "columbia_list.json"
ARCHIVE = "https://business.columbia.edu/heilbrunn/resources/graham-and-doddsville-newsletter"
USER_AGENT = "GDIndex/1.0 (+https://gd.ezrasnotes.com; weekly check of the archive page)"
SEASONS = {"winter": "01", "spring": "05", "summer": "06", "fall": "11"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self._href, self._text = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None


def parse_issues(html):
    """Return {label: absolute_pdf_url} for every 'Download the X Edition' link."""
    p = LinkParser()
    p.feed(html)
    found = {}
    for href, text in p.links:
        if not href or ".pdf" not in href.lower():
            continue
        m = re.search(r"Download the (.+?) Edition", text, re.I)
        if not m:
            continue
        found[m.group(1).strip()] = urllib.parse.urljoin(ARCHIVE, href)
    return found


def same_url(a, b):
    """Compare two links ignoring how the file name is escaped."""
    norm = lambda u: urllib.parse.unquote(urllib.parse.urljoin(ARCHIVE, u)).strip().lower()
    return norm(a) == norm(b)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def robots_allows(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(fetch("https://business.columbia.edu/robots.txt").splitlines())
    return rp.can_fetch(USER_AGENT, url)


def known_issues():
    out = {}
    for f in sorted((DATA / "issues").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        out[d["label"]] = {"file": f.name, "pdf": d["pdf"], "number": d.get("number"), "id": d["id"]}
    return out


def draft_for(label, url, known):
    """Write a skeleton issue file. Ezra (with Claude) fills in the items."""
    words = label.lower().replace("/", " ").split()
    season = next((w for w in words if w in SEASONS), "fall")
    year = max(int(w) for w in words if w.isdigit())
    iid = f"{year}-{season}"
    path = DATA / "issues" / f"{iid}.yaml"
    if path.exists():
        iid, path = f"{iid}-new", DATA / "issues" / f"{iid}-new.yaml"
    numbers = [k["number"] for k in known.values() if k["number"]]
    path.write_text(
        f"id: {iid}\n"
        f"label: {label}\n"
        f"date: {year}-{SEASONS[season]}\n"
        f"number: {max(numbers) + 1 if numbers else 'null'}   # guess: check the welcome letter on p. 2\n"
        f"pdf: {url}\n"
        f"pages: 0   # fill in: number of pages in the PDF\n"
        f"status: draft\n\n"
        f"# Found by the weekly check on {dt.date.today()}. Not public until status is published.\n"
        f"items: []\n"
    )
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="read a saved copy of the archive page instead of downloading it")
    args = ap.parse_args()
    if ALERT.exists():
        ALERT.unlink()

    problems, news = [], []
    try:
        if args.html:
            html = Path(args.html).read_text()
        else:
            if not robots_allows(ARCHIVE):
                raise RuntimeError("robots.txt no longer allows reading the archive page. The check stopped and changed nothing.")
            html = fetch(ARCHIVE)
        found = parse_issues(html)
    except Exception as e:  # noqa: BLE001 - any failure becomes an alert, never a deletion
        ALERT.write_text(f"## The weekly check couldn't read Columbia's archive page\n\n"
                         f"Error: `{e}`\n\nNothing in the index was changed. Page: {ARCHIVE}\n")
        print("Alert:", e)
        return 0

    known = known_issues()
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}

    if len(found) < 0.8 * max(len(seen), len(known), 1):
        ALERT.write_text(
            f"## Columbia's archive page looks different\n\n"
            f"The check found {len(found)} issue links, but the index knows {len(known)}. "
            f"Columbia may have redesigned the page. Nothing was changed.\n\nPage: {ARCHIVE}\n")
        print("Alert: too few links")
        return 0

    for label, url in found.items():
        if label in known:
            if not same_url(url, known[label]["pdf"]):
                problems.append(f"- **{label}**: the PDF link changed.\n  - Old: {known[label]['pdf']}\n"
                                f"  - New: {url}\n  - To accept it, paste the new link in `data/issues/{known[label]['file']}`.")
        else:
            path = draft_for(label, url, known)
            news.append(f"- **{label}**: {url}\n  - Draft created: `data/issues/{path.name}`")

    for label in known:
        if label not in found:
            problems.append(f"- **{label}** is no longer on Columbia's page. It stays in the index; check the PDF link still works.")

    SEEN.write_text(json.dumps(found, indent=1, ensure_ascii=False) + "\n")
    (DATA / "last_check.json").write_text(json.dumps({"checked": dt.date.today().isoformat(), "issues_on_page": len(found)}) + "\n")

    body = []
    if news:
        body += ["## New Graham & Doddsville issue", "",
                 "The weekly check found a new issue and created a draft entry. It is not public yet.", "", *news, "",
                 "Next: open a session with Claude, ask it to index the new issue from the PDF link above, "
                 "review the entries and summaries, then change `status: draft` to `status: published`.", ""]
    if problems:
        body += ["## Things to look at", "", *problems, ""]
    if body:
        ALERT.write_text("\n".join(body))
    print(f"{len(found)} issues on the page, {len(news)} new, {len(problems)} to look at.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
