#!/usr/bin/env python3
"""Tribe Board Index. Scans ~40 European scaleup Ashby job boards and prints
the market statistics every cold email quotes: medians by category, percentile
probes, the >90/>180/>300 day counts, and the open TA-roles list.

Run before EVERY outreach batch. Never quote a number in an email that did not
come from a scan run the same week. Optional args: a company slug to also print
that board's full role list (for the prospect-specific facts), and --probe N to
get the percentile for a specific role age.

Usage:
    python3 index.py                 # full index stats
    python3 index.py monumental      # index stats + that board's roles
    python3 index.py --probe 127     # percentile for a 127-day-old role
"""
import json, sys, datetime, statistics as st, concurrent.futures as cf
import urllib.request

TODAY = datetime.date.today()

# The 40-board universe. Add new boards here so week-over-week numbers stay
# comparable; note the change in the skill when you do.
SLUGS = """peec wordsmith aveni olix monumental jupus kittl choco kombo langdock
legora lovable taktile pleo the-exploration-company proxima-fusion tacto
black-forest-labs enpal pennylane alan deepl sereact n8n qonto dust photoroom
nabla forto juro sylvera 1x sanity multiverse nelly corti sorare ledger
knowunity upvest flip""".split()

def get(slug):
    url = "https://api.ashbyhq.com/posting-api/job-board/" + slug
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return (slug, json.load(r).get("jobs", []))
    except Exception:
        return (slug, [])

def categorize(title):
    t = (title or "").lower()
    if any(k in t for k in ("engineer", "developer", "scientist", "devops",
                            "architect", "physicist", "technician")):
        return "eng"
    if any(k in t for k in ("sales", "account executive", "sdr", "bdr",
                            "revenue", "business development", "gtm",
                            "partnership")):
        return "sales"
    if any(k in t for k in ("recruit", "talent", "people", "hr ")):
        return "ta"
    return "other"

rows = []
with cf.ThreadPoolExecutor(20) as ex:
    for slug, jobs in ex.map(get, sorted(set(SLUGS))):
        for j in jobs:
            pub = (j.get("publishedAt") or "")[:10]
            if not pub:
                continue
            age = (TODAY - datetime.date(*map(int, pub.split("-")))).days
            rows.append((slug, j.get("title"), age, categorize(j.get("title")),
                         j.get("location")))

ages = sorted(r[2] for r in rows)
print(f"SCAN DATE: {TODAY}")
print("BOARDS:", len(set(r[0] for r in rows)), "ROLES:", len(rows))
print(f"median all: {st.median(ages):.0f}d | mean {st.mean(ages):.0f}d")
for c in ("eng", "sales", "ta"):
    a = sorted(r[2] for r in rows if r[3] == c)
    if a:
        print(f"{c}: n={len(a)} median={st.median(a):.0f}d "
              f"p75={a[int(len(a)*0.75)]}d p90={a[int(len(a)*0.9)]}d")
o90 = sum(1 for x in ages if x > 90)
o180 = sum(1 for x in ages if x > 180)
o300 = sum(1 for x in ages if x > 300)
n = len(ages)
print(f">90d: {o90} ({100*o90/n:.0f}%) | >180d: {o180} ({100*o180/n:.0f}%) | "
      f">300d club: {o300} ({100*o300/n:.1f}%)")

def pct(age):
    return 100 * sum(1 for x in ages if x < age) / n

probes = [50, 60, 90, 140, 300]
args = sys.argv[1:]
if "--probe" in args:
    probes.append(int(args[args.index("--probe") + 1]))
for p in sorted(set(probes)):
    print(f"a role at {p}d is older than {pct(p):.0f}% of all tracked roles")

print("--- open TA roles across the index (>50d) ---")
for s, t, d, c, loc in sorted(rows, key=lambda r: -r[2]):
    if c == "ta" and d > 50:
        print(f"  {d:>4}d {s:<22} {t}")

for slug in [a for a in args if not a.startswith("--") and not a.isdigit()]:
    print(f"--- full board: {slug} ---")
    for s, t, d, c, loc in sorted(rows, key=lambda r: -r[2]):
        if s == slug:
            print(f"  {d:>4}d  {t}  [{loc}] ({c})")
