#!/usr/bin/env python3
"""Tribe Funding Radar. The free, same-day scaling-company finder.

Sweeps the RSS feeds of the European funding press (no paywalls, no credits),
extracts every company that announced a round in the last N days, then probes
the big ATS providers (Ashby, Lever, Greenhouse, Workable, Recruitee,
SmartRecruiters, Personio) for each company's LIVE job board. Scores what it
finds: total open roles, roles posted in the last 14 days, TA roles.

Money + many roles + roles posted this week + no recruiters = the lead.

Usage:
    python3 funding_radar.py            # last 3 days of rounds
    python3 funding_radar.py --days 7   # last week
"""
import json, re, sys, html, datetime, urllib.request
import concurrent.futures as cf
from xml.etree import ElementTree as ET

DAYS = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
NOW = datetime.datetime.now(datetime.timezone.utc)
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

FEEDS = [
    "https://www.eu-startups.com/feed/",
    "https://techfundingnews.com/feed/",
    "https://arcticstartup.com/feed/",
    "https://siliconcanals.com/feed/",
    "https://tech.eu/feed/",
    "https://startuprise.co.uk/feed/",
    "https://www.finsmes.com/category/europe/feed",
]

# "X raises/secures/lands/bags/closes €Y million/billion"
ROUND_RE = re.compile(
    r"^(?P<pre>.*?)\b(?P<verb>raises|raised|secures|secured|lands|landed|bags|"
    r"bagged|closes|closed|snags|grabs|gets|receives|announces)\b.*?"
    r"(?P<cur>[€$£])\s?(?P<amt>[\d.,]+)\s?(?P<unit>million|billion|[mb]\b)",
    re.I)
STRIP_PRE = re.compile(
    r"^(?:\w+-based\s+|(?:german|french|danish|dutch|swedish|spanish|italian|"
    r"austrian|swiss|belgian|finnish|norwegian|polish|czech|british|uk|irish|"
    r"portuguese|estonian|lithuanian|latvian|greek|icelandic|luxembourg)\s+)?"
    r"(?:ai\s+|fintech\s+|healthtech\s+|deeptech\s+|startup\s+|scaleup\s+|"
    r"unicorn\s+)*", re.I)

def fetch(url, timeout=12):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=timeout) as r:
            return r.read()
    except Exception:
        return None

# HOW FAR BACK THE FEEDS ACTUALLY REACH (25 Aug 2026 audit).
# --days 14 and --days 30 returned the identical 17 companies, because an RSS
# feed only carries its last ~10-20 items, which on these sites is about a
# week. The header printed "last 30 days" and delivered seven, which is the
# kind of number that ends up in an email. Every item age seen before the DAYS
# filter is recorded here so the header can state the REAL reach.
FEED_REACH = []


def parse_feed(url):
    raw = fetch(url)
    if not raw:
        return []
    out = []
    try:
        root = ET.fromstring(raw)
    except Exception:
        return []
    for item in root.iter("item"):
        title = html.unescape((item.findtext("title") or "").strip())
        pub = item.findtext("pubDate") or ""
        try:
            dt = datetime.datetime.strptime(pub[:25].strip(),
                                            "%a, %d %b %Y %H:%M:%S")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            dt = NOW
        FEED_REACH.append((NOW - dt).days)
        if (NOW - dt).days > DAYS:
            continue
        m = ROUND_RE.search(title)
        if not m:
            continue
        pre = m.group("pre").strip().rstrip(",:;")
        # headlines like "Beyond AI scribes: Aisel raises..." -> take after colon
        pre = pre.split(":")[-1].strip()
        # possessive geo prefixes: "Stockholm's Pixelgen" -> "Pixelgen"
        pre = re.sub(r"^.*?[’']s\s+", "", pre)
        # company = the leading words before the verb, minus geo/sector prefixes
        name = STRIP_PRE.sub("", pre).strip()
        # keep at most the first 4 words; names are short
        name = " ".join(name.split()[:4]).strip(" '\"")
        if not name or len(name) < 2:
            continue
        # JUNK GUARD, rewritten 24 Aug 2026 after an audit found it broken in
        # BOTH directions. The old condition was
        #     w0 in BIG_TUPLE and w0[0].islower() or w0 in SMALL_TUPLE
        # and `and` binds tighter than `or`, so islower() gated only the first
        # operand. Effects: "Year in review, Northvolt raises 200M" and
        # "After a brutal quarter Klarna raises 800M" both passed (the second
        # losing Klarna entirely), while the case-insensitive small tuple
        # silently dropped every company starting with The or A, including
        # The Exploration Company, which is in Tribe's own tracked board list.
        # A round for a company they actively follow could never have surfaced.
        parts = name.split()
        if not parts:
            continue
        # 1. Headlines title-case company names. A lowercase opener is prose.
        #    Kills "financial data startup Quartr" and "youngest IPO founder",
        #    both of which were live in the feed and both got ATS-probed.
        if parts[0][0].islower():
            continue
        # 2. A leading article is fine when it belongs to the name. Decide on
        #    the SECOND word, which is what tells The Exploration Company apart
        #    from "The round was led by".
        if parts[0].lower() in ("the", "a", "an"):
            if len(parts) < 2 or not parts[1][0].isupper():
                continue
        # 3. Words that do not appear inside a company name. Deliberately does
        #    NOT include "of", because The Bank of London is real.
        NEVER_IN_NAME = {"in", "after", "before", "that", "which", "who",
                         "when", "its", "their", "review", "report", "quarter",
                         "year", "how", "why", "what", "this", "youngest",
                         "oldest", "biggest", "latest"}
        if any(w.strip(",.:;").lower() in NEVER_IN_NAME for w in parts):
            continue

        # AMOUNT PARSING. The old line was amt.replace(",", ""), which treats a
        # comma as a thousands separator unconditionally. The European press
        # writes "EUR 1,5 million", which became "15" and was reported as a
        # 15M round instead of 1.5M. A 10x error, silent, in a field used to
        # rank leads.
        raw_amt = m.group("amt").strip(".,")
        if "," in raw_amt and "." in raw_amt:
            amt = raw_amt.replace(",", "")            # 1,234.5 -> 1234.5
        elif re.fullmatch(r"\d{1,3}(,\d{3})+", raw_amt):
            amt = raw_amt.replace(",", "")            # 1,200   -> 1200
        elif "," in raw_amt:
            amt = raw_amt.replace(",", ".")           # 1,5     -> 1.5
        else:
            amt = raw_amt
        unit = m.group("unit").lower()[0]
        try:
            meur = float(amt) * (1000 if unit == "b" else 1)
        except ValueError:
            continue
        out.append({"company": name, "title": title, "amount": meur,
                    "cur": m.group("cur"), "date": dt.date().isoformat(),
                    "src": url.split("/")[2]})
    return out

def slugify(name):
    base = re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()
    words = base.split()
    cands = []
    if words:
        cands += ["-".join(words), "".join(words), words[0]]
    # 'fonio.ai' style names: also try without a trailing ai/io/app word
    if len(words) > 1 and words[-1] in ("ai", "io", "app", "tech", "labs"):
        cands += ["-".join(words[:-1]), "".join(words[:-1])]
    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c); out.append(c)
    return out

TA_WORDS = ("recruit", "talent", "people", "hr ")

# LOCATION IS A GATE, NOT A DETAIL (rule of 24 Aug 2026, tooling added 25 Aug).
# The velocity diff once surfaced 1X as the best lead of the day: 82 roles, +6
# in four days, three stuck recruiter searches. Every role was in San Carlos
# and Hayward, California. The counts were real and the lead was worthless,
# because Tribe sells EMEA hiring. The rule said "any board probe that feeds a
# lead must print the location distribution" and nothing implemented it, so the
# rule could only ever be obeyed by remembering it. Now the probe carries it.
NON_EU = ("united states", "usa", " us)", "remote - us", "california", "new york",
          "san francisco", "san carlos", "hayward", "austin", "boston", "seattle",
          "chicago", "denver", "toronto", "vancouver", "canada", "singapore",
          "tokyo", "japan", "sydney", "australia", "bengaluru", "bangalore",
          "india", "dubai", "uae", "tel aviv", "israel", "sao paulo", "brazil",
          "mexico", "shanghai", "beijing", "hong kong", "seoul", "texas", ", ca",
          ", ny", ", ma", ", wa", ", il", ", co", ", tx", ", fl", ", ga",
          ", dc", ", us", ", usa", "washington d.c", "atlanta", "miami")


def _loc_of(job):
    """Pull a location string out of whatever shape the provider returns."""
    for key in ("locationName", "location", "city", "office"):
        v = job.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            parts = [v.get(k) for k in ("city", "region", "country", "name")]
            parts = [p for p in parts if isinstance(p, str) and p.strip()]
            if parts:
                return ", ".join(parts)
    cats = job.get("categories")
    if isinstance(cats, dict) and isinstance(cats.get("location"), str):
        return cats["location"].strip()
    return ""


def loc_summary(jobs):
    """Return (top-3 string, non_eu_fraction). Empty locations are ignored in
    the fraction rather than counted as European, so a board that exposes no
    location reads as 'unknown' instead of quietly passing the gate."""
    locs = [_loc_of(j) for j in jobs]
    locs = [l for l in locs if l]
    if not locs:
        return "location not exposed by this provider", None
    from collections import Counter as _C
    top = ", ".join(f"{l} x{n}" for l, n in _C(locs).most_common(3))
    non_eu = sum(1 for l in locs if any(k in l.lower() for k in NON_EU))
    return top, non_eu / len(locs)

def probe_boards(name):
    """Try every ATS provider for every slug candidate. Return best hit.
    A hit found only via the FIRST-WORD slug of a multi-word name is tagged
    verify=True: it can be a same-named stranger (a board called 'singular'
    is not necessarily Singular Photonics). Always confirm those by eye."""
    today = datetime.date.today()
    def age_days(iso):
        try:
            return (today - datetime.date(*map(int, iso[:10].split("-")))).days
        except Exception:
            return None
    words = re.sub(r"[^a-z0-9 ]", "", name.lower()).split()
    risky_slug = words[0] if len(words) > 1 else None
    for slug in slugify(name):
        risky = (slug == risky_slug)
        # Ashby
        raw = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("jobs", [])
            except Exception:
                jobs = []
            if jobs:
                ages = [age_days(j.get("publishedAt", "")) for j in jobs]
                return {"verify": risky, "ats": f"ashby/{slug}", "roles": len(jobs),
                        "recent": sum(1 for a in ages if a is not None and a <= 14),
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # Lever
        raw = fetch(f"https://api.lever.co/v0/postings/{slug}?mode=json", 8)
        if raw:
            try:
                jobs = json.loads(raw)
            except Exception:
                jobs = []
            if isinstance(jobs, list) and jobs:
                now_ms = NOW.timestamp() * 1000
                return {"verify": risky, "ats": f"lever/{slug}", "roles": len(jobs),
                        "recent": sum(1 for j in jobs if now_ms - j.get("createdAt", 0) < 14 * 86400000),
                        "ta": sum(1 for j in jobs if any(k in (j.get("text") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # Greenhouse
        raw = fetch(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("jobs", [])
            except Exception:
                jobs = []
            if jobs:
                ages = [age_days(j.get("updated_at", "")) for j in jobs]
                return {"verify": risky, "ats": f"greenhouse/{slug}", "roles": len(jobs),
                        "recent": sum(1 for a in ages if a is not None and a <= 14),
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # Workable
        raw = fetch(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=false", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("jobs", [])
            except Exception:
                jobs = []
            if jobs:
                return {"verify": risky, "ats": f"workable/{slug}", "roles": len(jobs), "recent": None,
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # Recruitee
        raw = fetch(f"https://{slug}.recruitee.com/api/offers/", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("offers", [])
            except Exception:
                jobs = []
            if jobs:
                return {"verify": risky, "ats": f"recruitee/{slug}", "roles": len(jobs), "recent": None,
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # SmartRecruiters
        raw = fetch(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings", 8)
        if raw:
            try:
                d = json.loads(raw)
            except Exception:
                d = {}
            if d.get("totalFound", 0) > 0:
                jobs = d.get("content", [])
                return {"verify": risky, "ats": f"smartrecruiters/{slug}", "roles": d["totalFound"], "recent": None,
                        "ta": sum(1 for j in jobs if any(k in (j.get("name") or "").lower() for k in TA_WORDS)),
                        "locs": loc_summary(jobs)}
        # Personio
        raw = fetch(f"https://{slug}.jobs.personio.de/xml", 8)
        if raw and b"<position>" in raw:
            n = raw.count(b"<position>")
            ta = sum(raw.lower().count(w.encode()) > 0 for w in ("recruit", "talent acquisition"))
            # Personio's XML feed is parsed for counts only, so say so rather
            # than returning an empty string that reads like "no locations".
            return {"verify": risky, "ats": f"personio/{slug}", "roles": n,
                    "recent": None, "ta": ta,
                    "locs": ("not parsed from the Personio feed, check by hand", None)}
    return None

# ---- run ----
rounds = []
with cf.ThreadPoolExecutor(8) as ex:
    for lst in ex.map(parse_feed, FEEDS):
        rounds.extend(lst)

# dedupe by lowercase company name, keep biggest amount
by_name = {}
for r in rounds:
    k = r["company"].lower()
    if k not in by_name or r["amount"] > by_name[k]["amount"]:
        by_name[k] = r
rounds = sorted(by_name.values(), key=lambda r: -r["amount"])

reach = max(FEED_REACH) if FEED_REACH else 0
window = min(DAYS, reach)
print(f"FUNDING RADAR {NOW.date()} | last {window} days | "
      f"{len(rounds)} companies from {len(FEEDS)} feeds")
if DAYS > reach:
    print(f"!!! YOU ASKED FOR {DAYS} DAYS AND THE FEEDS ONLY REACH BACK {reach}.")
    print("    RSS carries a fixed number of recent items, so anything older is")
    print("    simply not in the file and no flag can retrieve it. This is NOT")
    print("    'no rounds were announced': it is 'this tool cannot see them'.")
    print("    For older rounds use the weekly recaps (tech.eu, EU-Startups)")
    print("    by hand, and never report a quiet fortnight off this output.")
print("=" * 78)

def enrich(r):
    r["board"] = probe_boards(r["company"])
    return r

with cf.ThreadPoolExecutor(10) as ex:
    rounds = list(ex.map(enrich, rounds))

hot, cold = [], []
for r in rounds:
    (hot if r["board"] else cold).append(r)

def score(r):
    """Rank a lead. Workable, Recruitee, SmartRecruiters and Personio do not
    expose a per-role publish date, so `recent` is None for them. Treating that
    as 0 (the old `b["recent"] or 0`) meant those four providers could never
    outrank an Ashby board, regardless of how good the lead was. Estimate from
    the board size instead, and mark it so the operator knows it is an estimate."""
    b = r["board"]
    recent = b["recent"]
    if recent is None:
        recent = b["roles"] * 0.25   # neutral assumption, not a zero penalty
    return (b["roles"] + 3 * recent) * (2 if b["ta"] == 0 else 1)

for r in sorted(hot, key=score, reverse=True):
    b = r["board"]
    rec = f", {b['recent']} posted <=14d" if b["recent"] is not None else ""
    ta = "NO TA ROLES" if b["ta"] == 0 else f"{b['ta']} TA roles"
    v = " [VERIFY SLUG]" if b.get("verify") else ""
    amt_s = f"{r['amount']:.1f}" if r['amount'] < 10 else f"{r['amount']:.0f}"
    print(f"*{v} {r['company']:<24} {r['cur']}{amt_s}M  {r['date']}  "
          f"{b['ats']}: {b['roles']} roles{rec}, {ta}")
    top, non_eu = r["board"].get("locs", ("", None))
    if non_eu is not None and non_eu >= 0.5:
        print(f"    LOCATION GATE: {non_eu:.0%} of these roles are outside EMEA "
              f"({top}). Tribe sells EMEA hiring, so drop this unless the EU "
              f"slice alone justifies it.")
    else:
        print(f"    locations: {top}")
    print(f"    {r['title'][:74]}")
print("-" * 78)
print("no public board found (check careers page by hand, or park):")
for r in cold:
    amt_s = f"{r['amount']:.1f}" if r['amount'] < 10 else f"{r['amount']:.0f}"
    print(f"  {r['company']:<24} {r['cur']}{amt_s}M  {r['date']}  [{r['src']}]")
