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
import json, sys, os, datetime, statistics as st, concurrent.futures as cf
import urllib.request

TODAY = datetime.date.today()
HISTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board_history.json")
TA_WORDS = ("recruit", "talent", "people", "hr ")

# Evergreen postings are permanently open by design (speculative applications,
# talent pools, "don't see your role?"). They are not stuck roles, and leaving
# them in inflates every median, the >300 club, and the TA-pressure count.
# Caught 24 Aug 2026: the "oldest role in the index" was a 1,852-day
# Initiativbewerbung at Flip, and n8n's "Leadership roles (Talent Pool)" was
# being counted as an open recruiter req.
EVERGREEN = ("initiativbewerbung", "talent pool", "talent community",
             "expression of interest", "general application", "open application",
             "speculative", "future opportunit", "perfect role", "spontan",
             "candidature spontan", "join our talent", "other roles",
             "didn't find", "did not find", "can't find", "cannot find")

def is_evergreen(title):
    t = (title or "").lower()
    return any(k in t for k in EVERGREEN)


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
            if is_evergreen(j.get("title")):
                continue
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

# --- TA PRESSURE: companies whose hiring function is visibly under strain ---
# High ratio of open TA roles to total roles = they cannot hire fast enough
# to hire. The best-qualified cold targets in the index.
print("--- TA PRESSURE (open TA roles vs board size) ---")
by_board = {}
for s, t, d, c, loc in rows:
    tot, ta = by_board.get(s, (0, 0))
    by_board[s] = (tot + 1, ta + (1 if c == "ta" else 0))
pressure = [(s, ta, tot, 100 * ta / tot) for s, (tot, ta) in by_board.items()
            if ta >= 2 or (ta >= 1 and tot >= 5 and 100 * ta / tot >= 10)]
for s, ta, tot, ratio in sorted(pressure, key=lambda x: -x[3]):
    print(f"  {s:<22} {ta} TA roles of {tot} total ({ratio:.0f}% of the board)")
if not pressure:
    print("  none above threshold this scan")

# --- VELOCITY: diff against the previous scan (the scaling detector) ---
current = {}
for s, t, d, c, loc in rows:
    current.setdefault(s, []).append(t)
prev, prev_date = {}, None
if os.path.exists(HISTORY):
    try:
        h = json.load(open(HISTORY))
        prev_date = h.get("date")
        prev = h.get("boards", {})
    except Exception:
        pass
if prev:
    print(f"--- VELOCITY vs previous scan ({prev_date}) ---")
    alerts = []
    for slug in sorted(current):
        if slug not in prev:
            alerts.append((slug, f"NEW BOARD with {len(current[slug])} roles"))
            continue
        added = [t for t in current[slug] if t not in prev[slug]]
        closed = [t for t in prev[slug] if t not in current[slug]]
        first_ta = [t for t in added
                    if any(k in (t or "").lower() for k in TA_WORDS)
                    and not any(any(k in (p or "").lower() for k in TA_WORDS)
                                for p in prev[slug])]
        if len(added) >= 3:
            alerts.append((slug, f"SCALING: +{len(added)} roles "
                                 f"({', '.join(added[:4])}{'...' if len(added) > 4 else ''})"))
        if first_ta:
            alerts.append((slug, f"FIRST RECRUITER ROLE posted: {first_ta[0]} "
                                 f"(they are building a hiring function NOW)"))
        if len(closed) >= 4:
            alerts.append((slug, f"slowdown or hiring freeze: -{len(closed)} roles"))
    if alerts:
        for slug, msg in alerts:
            print(f"  {slug:<22} {msg}")
    else:
        print("  no significant board movement since last scan")
else:
    print("--- VELOCITY: first scan recorded, diffs start next run ---")
json.dump({"date": str(TODAY), "boards": current}, open(HISTORY, "w"))

for slug in [a for a in args if not a.startswith("--") and not a.isdigit()]:
    print(f"--- full board: {slug} ---")
    for s, t, d, c, loc in sorted(rows, key=lambda r: -r[2]):
        if s == slug:
            print(f"  {d:>4}d  {t}  [{loc}] ({c})")
