"""Build the static site into docs/ from data/.

    python scripts/build.py            # public build: published issues, approved summaries
    python scripts/build.py --preview  # also shows draft issues and draft summaries, marked
"""
import argparse
import hashlib
import datetime as dt
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs"
SEASON_ORDER = {"winter": 1, "spring": 2, "summer": 3, "fall": 4}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load(name, default=None):
    p = DATA / name
    return (yaml.safe_load(p.read_text()) or default) if p.exists() else default


def alias_map(table):
    out = {}
    for canon, v in (table or {}).items():
        out[canon] = canon
        for a in (v or {}).get("aliases", []):
            out[a] = canon
    return out


def checked_on():
    """Build date, shown as 'Updated ...' in the header. The site only rebuilds when the data changes."""
    return dt.date.today().strftime("%B %-d, %Y")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    site = yaml.safe_load((ROOT / "site.yaml").read_text())
    topics = load("topics.yaml", {})
    inv_alias = alias_map(load("investors.yaml", {}))
    co_alias = alias_map(load("companies.yaml", {}))

    issues = []
    for f in sorted((DATA / "issues").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") != "published" and not args.preview:
            continue
        d["draft"] = d.get("status") != "published"
        d["year"] = int(str(d["date"])[:4])
        season = d["label"].split()[0].lower()
        d["sort"] = (str(d["date"]), SEASON_ORDER.get(season, 0))
        issues.append(d)
    issues.sort(key=lambda d: d["sort"], reverse=True)

    investors, companies, topic_hits, pitches, students = {}, {}, defaultdict(list), [], {}

    def company(name):
        name = co_alias.get(name, name)
        return companies.setdefault(slugify(name), {"name": name, "slug": slugify(name), "interviews": [], "pitches": []})

    for iss in issues:
        iss["interviews"], iss["pitches"], iss["other"] = [], [], []
        for it in iss["items"]:
            it["issue"] = iss
            it["url"] = f'{iss["pdf"]}#page={it["page"]}'
            s = it.get("summary")
            it["show_summary"] = bool(s) and (it.get("summary_status") == "approved" or args.preview)
            it["summary_draft"] = it.get("summary_status") != "approved"
            t = it["type"]
            if t == "interview":
                it["people"] = []
                for p in it["investors"]:
                    name = inv_alias.get(p["name"], p["name"])
                    inv = investors.setdefault(slugify(name), {"name": name, "slug": slugify(name), "firms": [], "hits": []})
                    if p.get("firm") and p["firm"] not in inv["firms"]:
                        inv["firms"].append(p["firm"])
                    inv["hits"].append(it)
                    it["people"].append({"name": name, "slug": inv["slug"], "firm": p.get("firm", "")})
                it["firms"] = list(dict.fromkeys(p["firm"] for p in it["people"] if p["firm"]))
                it["cos"] = []
                for c in it.get("companies") or []:
                    co = company(c["name"])
                    co["interviews"].append(it)
                    it["cos"].append(co)
                it["tops"] = []
                for tp in it.get("topics") or []:
                    if tp not in topics:
                        raise SystemExit(f'{iss["id"]}: topic "{tp}" is not in data/topics.yaml')
                    topic_hits[tp].append(it)
                    it["tops"].append({"slug": tp, "label": topics[tp]})
                iss["interviews"].append(it)
            elif t == "pitch":
                co = company(it["company"])
                co["pitches"].append(it)
                it["co"] = co
                for s_ in it.get("students", []):
                    students.setdefault(s_, []).append(it)
                pitches.append(it)
                iss["pitches"].append(it)
            elif t == "other":
                iss["other"].append(it)
        for k in ("interviews", "pitches", "other"):
            iss[k].sort(key=lambda x: x["page"])

    inv_list = sorted(investors.values(), key=lambda i: i["name"].split()[-1].lower())
    co_list = sorted(companies.values(), key=lambda c: c["name"].lower())
    topic_list = [{"slug": k, "label": topics[k], "hits": v} for k, v in sorted(topic_hits.items(), key=lambda kv: topics[kv[0]].lower())]

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "static").mkdir(parents=True)
    for f in (ROOT / "static").iterdir():
        shutil.copy(f, OUT / "static" / f.name)
    (OUT / ".nojekyll").write_text("")
    (OUT / "CNAME").write_text("gd.ezrasnotes.com\n")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape())
    # Content hash: same files give the same pages, so rebuilds don't touch every page.
    asset_v = hashlib.sha1(b"".join(f.read_bytes() for f in sorted((ROOT / "static").glob("*.[cj]s*")))).hexdigest()[:10]
    common = dict(site=site, preview=args.preview, asset_v=asset_v,
                  updated=checked_on(),
                  counts={"issues": len(issues), "interviews": sum(len(i["interviews"]) for i in issues),
                          "pitches": len(pitches), "investors": len(investors)})

    def render(tpl, page, **kw):
        depth = page.count("/")
        html = env.get_template(tpl).render(page=page, root="../" * depth, **common, **kw)
        p = OUT / page
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html)

    render("index.html", "index.html", issues=issues)
    for iss in issues:
        render("issue.html", f'i/{iss["id"]}.html', iss=iss)
    render("investors.html", "investors.html", investors=inv_list)
    for inv in inv_list:
        years = defaultdict(list)
        for h in inv["hits"]:
            years[h["issue"]["year"]].append(h)
        render("investor.html", f'p/{inv["slug"]}.html', inv=inv, years=sorted(years.items(), reverse=True))
    render("companies.html", "companies.html", companies=co_list)
    for co in co_list:
        render("company.html", f'c/{co["slug"]}.html', co=co)
    render("topics.html", "topics.html", topics=topic_list)
    for tp in topic_list:
        render("topic.html", f't/{tp["slug"]}.html', tp=tp)
    years = sorted({p["issue"]["year"] for p in pitches}, reverse=True)
    render("pitches.html", "pitches.html", pitches=pitches, years=years)
    render("search.html", "search.html")
    render("about.html", "about.html")
    render("404.html", "404.html")

    # Search index: short keys keep the file small.
    idx = []
    for inv in inv_list:
        idx.append({"k": "Investors", "n": inv["name"], "m": ", ".join(inv["firms"]), "u": f'p/{inv["slug"]}.html', "x": ""})
    for co in co_list:
        n = len(co["interviews"]) + len(co["pitches"])
        idx.append({"k": "Companies", "n": co["name"], "m": f'{n} mention{"s" if n != 1 else ""}', "u": f'c/{co["slug"]}.html', "x": ""})
    for tp in topic_list:
        idx.append({"k": "Topics", "n": tp["label"], "m": f'{len(tp["hits"])} interview{"s" if len(tp["hits"]) != 1 else ""}', "u": f't/{tp["slug"]}.html', "x": ""})
    for name, its in sorted(students.items()):
        for it in its:
            idx.append({"k": "Student pitches", "n": f'{it["co"]["name"]} ({it["direction"].title()})',
                        "m": f'{name} · {it["issue"]["label"]}', "u": f'i/{it["issue"]["id"]}.html#p{it["page"]}', "x": name})
    for inv in inv_list:  # firms are searchable through their investors
        idx[[i["n"] for i in idx].index(inv["name"])]["x"] = " ".join(inv["firms"])
    (OUT / "search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))

    # RSS: newest issues first.
    items = []
    for iss in issues[:20]:
        names = "; ".join(" & ".join(p["name"] for p in it["people"]) for it in iss["interviews"])
        when = dt.datetime.strptime(str(iss["date"]) + "-01", "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
        link = f'{site["site_url"]}/i/{iss["id"]}.html'
        items.append(f"<item><title>Graham &amp; Doddsville, {escape(iss['label'])}</title><link>{link}</link>"
                     f"<guid>{link}</guid><pubDate>{format_datetime(when)}</pubDate>"
                     f"<description>{escape(f'Interviews: {names}. Student pitches: {len(iss["pitches"])}.')}</description></item>")
    (OUT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>'
        f"<title>The G&amp;D Index · Ezra's Notes</title><link>{site['site_url']}</link>"
        "<description>New issues of Graham &amp; Doddsville, indexed.</description>"
        + "".join(items) + "</channel></rss>\n")
    print(f'Built {len(issues)} issues, {len(inv_list)} investors, {len(co_list)} companies, {len(pitches)} pitches'
          + (" (preview)" if args.preview else ""))


if __name__ == "__main__":
    main()
