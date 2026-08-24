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
from collections import Counter
import urllib.request

TODAY = datetime.date.today()
HISTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board_history.json")

# SLUGS, EVERGREEN, TA_WORDS, categorize() and the filter version now live in
# board_common.py, shared with index_post.py. They used to be duplicated here
# and had drifted: this file tracked 41 boards, the public post tracked 45, and
# the two published different role counts for the same index on the same
# morning. Do not redefine any of them locally again.
from board_common import (SLUGS, EVERGREEN, TA_WORDS, FILTER_VERSION,
                          is_evergreen, categorize, age_days)

def get(slug):
    url = "https://api.ashbyhq.com/posting-api/job-board/" + slug
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return (slug, json.load(r).get("jobs", []))
    except Exception:
        return (slug, None)   # None = the board FAILED, [] = genuinely empty


rows, failed = [], []
with cf.ThreadPoolExecutor(20) as ex:
    for slug, jobs in ex.map(get, sorted(set(SLUGS))):
        if jobs is None:
            failed.append(slug)
            continue
        for j in jobs:
            # age_days returns None rather than raising. A single malformed
            # publishedAt used to kill the whole run with a ValueError.
            age = age_days(j.get("publishedAt"), TODAY)
            if age is None:
                continue
            if is_evergreen(j.get("title")):
                continue
            rows.append((slug, j.get("title"), age, categorize(j.get("title")),
                         j.get("location")))

if not rows:
    sys.exit("No data returned at all. Check network access.")
if failed:
    print(f"!!! {len(failed)} boards failed to respond and are MISSING from every "
          f"number below: {', '.join(failed)}")
    print("!!! Do not quote these figures in an email until a clean scan runs.\n")

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
prev, prev_date, prev_filter = {}, None, None
if os.path.exists(HISTORY):
    try:
        h = json.load(open(HISTORY))
        prev_date = h.get("date")
        prev = h.get("boards", {})
        prev_filter = h.get("filter_version")
    except Exception:
        pass

# A history file written under a different filter version cannot be diffed.
# Found 24 Aug 2026: board_history.json predated the evergreen filter, so its
# stored titles still contained 14 talent pools. Diffing against it reported
# "n8n slowdown or hiring freeze: -5 roles" when n8n had closed ZERO roles.
# All five "closures" were talent pools the new filter had simply stopped
# counting. The mirror-image failure is worse: first_ta suppresses the
# highest-value signal in the whole script, "FIRST RECRUITER ROLE posted", for
# any board whose stored history contains a "Talent Pool" title, because those
# match TA_WORDS and make the role look like it was never the first.
if prev and prev_filter != FILTER_VERSION:
    print(f"--- VELOCITY SKIPPED: history was written under filter version "
          f"{prev_filter}, this scan is version {FILTER_VERSION}. Diffing across "
          f"a filter change reports filter edits as hiring activity. Baseline "
          f"rewritten now, diffs resume next run. ---")
    prev = {}
elif prev:
    print(f"--- VELOCITY vs previous scan ({prev_date}) ---")
    alerts = []
    for slug in sorted(current):
        if slug not in prev:
            alerts.append((slug, f"NEW BOARD with {len(current[slug])} roles"))
            continue
        # MULTISET, not list membership (24 Aug 2026 audit). 14 of 45 boards
        # carry duplicate titles: legora had 269 roles under 207 distinct
        # titles, enpal 144 under 119. With `t not in prev`, going from one
        # copy of "Legal Engineer" to seven registered as zero added, and
        # legora's true movement of +1/-2 was reported as +1/-0, hiding two
        # closures. It also printed the same duplicated title four times in a
        # single alert, which is how it was spotted.
        cur_c, prev_c = Counter(current[slug]), Counter(prev[slug])
        added_c, closed_c = cur_c - prev_c, prev_c - cur_c
        n_added, n_closed = sum(added_c.values()), sum(closed_c.values())
        added_titles = sorted(added_c)
        prev_has_ta = any(any(k in (p or "").lower() for k in TA_WORDS)
                          for p in prev[slug])
        first_ta = [t for t in added_titles
                    if any(k in (t or "").lower() for k in TA_WORDS)
                    and not prev_has_ta]
        if n_added >= 3:
            shown = ", ".join(added_titles[:4])
            alerts.append((slug, f"SCALING: +{n_added} roles "
                                 f"({shown}{'...' if len(added_titles) > 4 else ''})"))
        if first_ta:
            alerts.append((slug, f"FIRST RECRUITER ROLE posted: {first_ta[0]} "
                                 f"(they are building a hiring function NOW)"))
        if n_closed >= 4:
            alerts.append((slug, f"slowdown or hiring freeze: -{n_closed} roles"))
    if alerts:
        for slug, msg in alerts:
            print(f"  {slug:<22} {msg}")
    else:
        print("  no significant board movement since last scan")
else:
    print("--- VELOCITY: first scan recorded, diffs start next run ---")

# Never write a baseline from a scan with missing boards: every absent board
# would look like it closed its entire req list on the next run.
if failed:
    print(f"\n!!! History NOT written, {len(failed)} boards were missing. "
          f"Next run still diffs against {prev_date}.")
else:
    json.dump({"date": str(TODAY), "filter_version": FILTER_VERSION,
               "boards": current}, open(HISTORY, "w"))

for slug in [a for a in args if not a.startswith("--") and not a.isdigit()]:
    print(f"--- full board: {slug} ---")
    for s, t, d, c, loc in sorted(rows, key=lambda r: -r[2]):
        if s == slug:
            print(f"  {d:>4}d  {t}  [{loc}] ({c})")
