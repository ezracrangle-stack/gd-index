"""Check every data file before the site is built. Stops the build with a clear message if something is wrong."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


topics = yaml.safe_load((DATA / "topics.yaml").read_text()) or {}
ids = set()
for f in sorted((DATA / "issues").glob("*.yaml")):
    where = f"data/issues/{f.name}"
    try:
        d = yaml.safe_load(f.read_text())
    except yaml.YAMLError as e:
        err(where, f"the file can't be read (often a missing quote or a bad indent): {e}")
        continue
    for k in ("id", "label", "date", "pdf", "pages", "status", "items"):
        if k not in d:
            err(where, f"missing '{k}'")
    if d.get("id") in ids:
        err(where, f"id '{d.get('id')}' is used twice")
    ids.add(d.get("id"))
    if d.get("status") not in ("draft", "published"):
        err(where, "status must be draft or published")
    if not str(d.get("pdf", "")).startswith("https://business.columbia.edu/"):
        err(where, "pdf must link to Columbia's site")
    pages = d.get("pages") or 0
    if d.get("status") == "published" and not pages:
        err(where, "fill in 'pages' before publishing")
    for n, it in enumerate(d.get("items") or [], 1):
        w = f"{where}, item {n}"
        t = it.get("type")
        if t not in ("interview", "pitch", "pitches", "other"):
            err(w, f"unknown type '{t}'")
        if not isinstance(it.get("page"), int) or it["page"] < 1 or (pages and it["page"] > pages):
            err(w, f"page {it.get('page')} is outside the PDF (1 to {pages})")
        if it.get("summary_status") not in (None, "draft", "approved"):
            err(w, "summary_status must be draft or approved")
        if t == "interview":
            if not it.get("investors"):
                err(w, "an interview needs at least one investor")
            for tp in it.get("topics") or []:
                if tp not in topics:
                    err(w, f"topic '{tp}' is not in data/topics.yaml")
        if t == "pitch":
            for k in ("company", "direction", "students"):
                if not it.get(k):
                    err(w, f"a pitch needs '{k}'")
            if it.get("direction") not in ("long", "short"):
                err(w, "direction must be long or short")
        s = it.get("summary") or ""
        if "—" in s or "–" in s:
            err(w, "summary has a long dash; use a comma, colon or period")

if errors:
    print("Found problems. The site was not built:\n")
    print("\n".join(errors))
    sys.exit(1)
print(f"Data OK: {len(ids)} issues.")
