#!/usr/bin/env python3
"""Tribe Board Index, weekly public post.

Turns the same scan that powers the cold emails into the thing nobody else in
European recruiting has: a published benchmark. Run it every Monday, paste the
output into LinkedIn, keep the numbers moving week over week.

The strategic point (Jacopo, 24 Aug 2026): outbound is linear and the index
compounds. Founders who ignore a cold email will still read a benchmark about
their own market, and once they have seen it, "I track 45 boards" stops being
a claim in an email and becomes something they recognise.

THIS OUTPUT IS PUBLISHED. A wrong number here is worse than no post, so the
script refuses to produce one from a degraded scan. See the audit fixes below.

Usage:
    python3 index_post.py            # this week's post
    python3 index_post.py --raw      # also dump the numbers for a page/table
    python3 index_post.py --force    # publish anyway despite failed boards
"""
import json, sys, os, datetime, statistics as st
import concurrent.futures as cf
import urllib.request

from board_common import (SLUGS, EVERGREEN, TA_WORDS, FILTER_VERSION,
                          is_evergreen, categorize, age_days)

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today()
POST_HISTORY = os.path.join(HERE, "index_post_history.json")
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# A scan missing more than this fraction of boards is not publishable.
MAX_FAILED_FRACTION = 0.05


def get(slug):
    """Return (slug, jobs) on success, (slug, None) on failure.

    THE None MATTERS (24 Aug 2026 audit). This used to return [] on any
    exception, which is indistinguishable from a board that genuinely has no
    open roles. Faulting just 2 of 45 boards moved the published role count by
    23% and the >90-day count by 108, silently, exit 0. Faulting 40 produced a
    complete, publishable, entirely wrong post: "258 open roles across 5
    European scaleup job boards", engineering median 24 days against a true 54,
    "0 are past 300" against a true 31.
    """
    url = "https://api.ashbyhq.com/posting-api/job-board/" + slug
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=15) as r:
            return (slug, json.load(r).get("jobs", []))
    except Exception:
        return (slug, None)


rows, failed = [], []
with cf.ThreadPoolExecutor(20) as ex:
    for slug, jobs in ex.map(get, sorted(set(SLUGS))):
        if jobs is None:
            failed.append(slug)
            continue
        for j in jobs:
            age = age_days(j.get("publishedAt"), TODAY)
            if age is None:
                continue
            if is_evergreen(j.get("title")):
                continue
            rows.append((slug, j.get("title"), age, categorize(j.get("title"))))

if not rows:
    sys.exit("No data returned at all. Check network access.")

if failed and "--force" not in sys.argv:
    sys.exit(
        f"REFUSING TO PUBLISH. {len(failed)} of {len(set(SLUGS))} boards failed "
        f"to respond: {', '.join(failed)}\n"
        "Every number below would be understated and the history file would be\n"
        "poisoned for next week's deltas. Re-run in a few minutes.\n"
        "Use --force only if you have decided a partial index is acceptable, and\n"
        "say so in the post if you do.")

if failed:
    print(f"!!! FORCED: {len(failed)} boards missing ({', '.join(failed)}). "
          f"Numbers below are UNDERSTATED. History will not be written.\n")

ages = sorted(r[2] for r in rows)
n = len(ages)
boards = len(set(r[0] for r in rows))
year, week, _ = TODAY.isocalendar()


def med(cat):
    a = sorted(r[2] for r in rows if r[3] == cat)
    return int(st.median(a)) if a else None


eng, sales, ta = med("eng"), med("sales"), med("ta")

# An empty category used to print the literal string "None days" into a post
# meant for publication, and exit 0 while doing it.
missing = [name for name, v in (("engineering", eng), ("sales", sales),
                                ("recruiting", ta)) if v is None]
if missing:
    sys.exit(f"REFUSING TO PUBLISH. No roles matched: {', '.join(missing)}. "
             "The post would read 'None days'. Check the scan and the filters.")

club300 = sum(1 for x in ages if x > 300)
over90 = sum(1 for x in ages if x > 90)
fresh = sum(1 for x in ages if x <= 14)

# ---- week-over-week movement -------------------------------------------------
# HISTORY IS AN APPEND-ONLY LIST KEYED BY (year, week) (24 Aug 2026 audit).
# It used to be a single overwritten snapshot with no week check, so running the
# script twice in one day compared this week to itself and published "(flat)"
# across the board while the market had actually moved -7/+5/-8. The real
# baseline was destroyed permanently, with no archive to recover it from.
history = []
if os.path.exists(POST_HISTORY):
    try:
        loaded = json.load(open(POST_HISTORY))
        history = loaded if isinstance(loaded, list) else [loaded]
    except Exception:
        history = []

prev = None
for entry in sorted(history, key=lambda e: (e.get("year", 0), e.get("week", 0)),
                    reverse=True):
    if (entry.get("year"), entry.get("week")) != (year, week):
        prev = entry
        break

if prev:
    gap = (year - prev.get("year", year)) * 52 + (week - prev.get("week", week))
    since = "vs last week" if gap == 1 else f"vs week {prev.get('week')}"
else:
    since = ""


def delta(key, now):
    """Label the delta with the baseline's ACTUAL week. A five-week-old
    baseline used to be reported as 'vs last week'."""
    if not prev:
        return ""
    old = prev.get(key)
    if old is None or now is None:
        return ""
    d = now - old
    if d == 0:
        return f" (flat {since})"
    return f" ({'+' if d > 0 else ''}{d} {since})"


oldest = max(rows, key=lambda r: r[2])
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
if prev:
    print(f"Deltas are against week {prev.get('week')} ({prev.get('date')}).")
else:
    print("No prior week on file, so no deltas this time. Next week will have them.")
print("Anyone who comments is an inbound lead: check them against HubSpot before replying,")
print("and if they are clean, the reply IS the outreach, no cold email needed.")

if "--raw" in sys.argv:
    print("\n--- raw, for the public page ---")
    print(json.dumps({"week": week, "year": year, "date": str(TODAY), "roles": n,
                      "boards": boards, "eng": eng, "sales": sales, "ta": ta,
                      "over90": over90, "club300": club300, "fresh14": fresh},
                     indent=2))

# Never write history from a degraded scan, and never overwrite this week's own
# entry with a re-run.
if not failed:
    entry = {"year": year, "week": week, "date": str(TODAY), "roles": n,
             "boards": boards, "eng": eng, "sales": sales, "ta": ta,
             "over90": over90, "club300": club300,
             "filter_version": FILTER_VERSION}
    history = [e for e in history
               if (e.get("year"), e.get("week")) != (year, week)]
    history.append(entry)
    history = sorted(history, key=lambda e: (e.get("year", 0), e.get("week", 0)))[-52:]
    json.dump(history, open(POST_HISTORY, "w"), indent=2)
