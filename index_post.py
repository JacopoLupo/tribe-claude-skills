#!/usr/bin/env python3
"""Tribe Board Index, weekly public post.

Turns the same scan that powers the cold emails into the thing nobody else in
European recruiting has: a published benchmark. Run it every Monday, paste the
output into LinkedIn, keep the numbers moving week over week.

The strategic point (Jacopo, 24 Aug 2026): outbound is linear and the index
compounds. Founders who ignore a cold email will still read a benchmark about
their own market, and once they have seen it, "I track 41 boards" stops being
a claim in an email and becomes something they recognise.

Usage:
    python3 index_post.py            # this week's post
    python3 index_post.py --raw      # also dump the numbers for a page/table
"""
import json, sys, os, datetime, statistics as st
import concurrent.futures as cf
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today()
HISTORY = os.path.join(HERE, "board_history.json")
POST_HISTORY = os.path.join(HERE, "index_post_history.json")
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

SLUGS = """peec wordsmith aveni olix monumental jupus kittl choco kombo langdock
legora lovable taktile pleo the-exploration-company proxima-fusion tacto
black-forest-labs enpal pennylane alan deepl sereact n8n qonto dust photoroom
nabla forto juro sylvera 1x sanity multiverse nelly corti sorare ledger
knowunity upvest flip callosum dash0 amber humanoid""".split()

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



def get(slug):
    url = "https://api.ashbyhq.com/posting-api/job-board/" + slug
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=15) as r:
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
    if any(k in t for k in TA_WORDS):
        return "ta"
    return "other"


rows = []
with cf.ThreadPoolExecutor(20) as ex:
    for slug, jobs in ex.map(get, sorted(set(SLUGS))):
        for j in jobs:
            pub = (j.get("publishedAt") or "")[:10]
            if not pub:
                continue
            try:
                age = (TODAY - datetime.date(*map(int, pub.split("-")))).days
            except Exception:
                continue
            if is_evergreen(j.get("title")):
                continue
            rows.append((slug, j.get("title"), age, categorize(j.get("title"))))

if not rows:
    sys.exit("No data returned. Check network access.")

ages = sorted(r[2] for r in rows)
n = len(ages)
boards = len(set(r[0] for r in rows))
week = TODAY.isocalendar()[1]


def med(cat):
    a = sorted(r[2] for r in rows if r[3] == cat)
    return int(st.median(a)) if a else None


eng, sales, ta = med("eng"), med("sales"), med("ta")
club300 = sum(1 for x in ages if x > 300)
over90 = sum(1 for x in ages if x > 90)
fresh = sum(1 for x in ages if x <= 14)

# week-over-week movement, from the last post rather than the last scan
prev = {}
if os.path.exists(POST_HISTORY):
    try:
        prev = json.load(open(POST_HISTORY))
    except Exception:
        prev = {}


def delta(key, now):
    old = prev.get(key)
    if old is None or now is None:
        return ""
    d = now - old
    if d == 0:
        return " (flat)"
    return f" ({'+' if d > 0 else ''}{d} vs last week)"


# the standout: oldest role in the whole index
oldest = max(rows, key=lambda r: r[2])
# the board opening fastest this week
by_board_fresh = {}
for slug, title, age, cat in rows:
    if age <= 14:
        by_board_fresh[slug] = by_board_fresh.get(slug, 0) + 1
fastest = max(by_board_fresh.items(), key=lambda x: x[1]) if by_board_fresh else None

print(f"""=== PASTE INTO LINKEDIN ===

European Scaleup Hiring Index, week {week}.

{n:,} open roles across {boards} European scaleup job boards, scanned this morning.

Median time a role stays open:
Engineering {eng} days{delta('eng', eng)}
Sales {sales} days{delta('sales', sales)}
Recruiting {ta} days{delta('ta', ta)}

{over90} roles ({100*over90/n:.0f}%) have been open more than 90 days.
{club300} are past 300. The oldest is {oldest[2]} days.

{fresh} roles were posted in the last fortnight, so the market is still moving.

The number I keep coming back to: recruiting roles themselves take {ta} days to
fill. The companies that most need to hire are the slowest at hiring the people
who do the hiring.

Happy to send the cut for your sector, comment or DM and it is yours.

=== END POST ===
""")

print("--- notes for Jacopo, do not paste ---")
if fastest:
    print(f"Fastest-moving board this week: {fastest[0]} with {fastest[1]} roles posted in 14 days.")
print(f"Oldest role in the index: {oldest[2]}d, {oldest[1]} at {oldest[0]}.")
print("Anyone who comments is an inbound lead: check them against HubSpot before replying,")
print("and if they are clean, the reply IS the outreach, no cold email needed.")

if "--raw" in sys.argv:
    print("\n--- raw, for the public page ---")
    print(json.dumps({"week": week, "date": str(TODAY), "roles": n,
                      "boards": boards, "eng": eng, "sales": sales, "ta": ta,
                      "over90": over90, "club300": club300, "fresh14": fresh},
                     indent=2))

json.dump({"week": week, "date": str(TODAY), "roles": n, "boards": boards,
           "eng": eng, "sales": sales, "ta": ta, "over90": over90,
           "club300": club300}, open(POST_HISTORY, "w"), indent=2)
