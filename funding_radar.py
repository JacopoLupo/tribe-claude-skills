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
        # junk guard: headline fragments, not names ("A year after their")
        w0 = name.split()[0]
        if w0.lower() in ("a", "an", "the", "this", "year", "after", "how",
                          "why", "what", "exclusive", "infrastructure",
                          "startup", "scaleup") and w0[0].islower() or \
           w0.lower() in ("a", "an", "the", "this", "how", "why", "what"):
            continue
        amt = m.group("amt").replace(",", "")
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
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS))}
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
                        "ta": sum(1 for j in jobs if any(k in (j.get("text") or "").lower() for k in TA_WORDS))}
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
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS))}
        # Workable
        raw = fetch(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=false", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("jobs", [])
            except Exception:
                jobs = []
            if jobs:
                return {"verify": risky, "ats": f"workable/{slug}", "roles": len(jobs), "recent": None,
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS))}
        # Recruitee
        raw = fetch(f"https://{slug}.recruitee.com/api/offers/", 8)
        if raw:
            try:
                jobs = json.loads(raw).get("offers", [])
            except Exception:
                jobs = []
            if jobs:
                return {"verify": risky, "ats": f"recruitee/{slug}", "roles": len(jobs), "recent": None,
                        "ta": sum(1 for j in jobs if any(k in (j.get("title") or "").lower() for k in TA_WORDS))}
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
                        "ta": sum(1 for j in jobs if any(k in (j.get("name") or "").lower() for k in TA_WORDS))}
        # Personio
        raw = fetch(f"https://{slug}.jobs.personio.de/xml", 8)
        if raw and b"<position>" in raw:
            n = raw.count(b"<position>")
            ta = sum(raw.lower().count(w.encode()) > 0 for w in ("recruit", "talent acquisition"))
            return {"verify": risky, "ats": f"personio/{slug}", "roles": n, "recent": None, "ta": ta}
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

print(f"FUNDING RADAR {NOW.date()} | last {DAYS} days | "
      f"{len(rounds)} companies from {len(FEEDS)} feeds")
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
    b = r["board"]
    return (b["roles"] + 3 * (b["recent"] or 0)) * (2 if b["ta"] == 0 else 1)

for r in sorted(hot, key=score, reverse=True):
    b = r["board"]
    rec = f", {b['recent']} posted <=14d" if b["recent"] is not None else ""
    ta = "NO TA ROLES" if b["ta"] == 0 else f"{b['ta']} TA roles"
    v = " [VERIFY SLUG]" if b.get("verify") else ""
    print(f"*{v} {r['company']:<24} {r['cur']}{r['amount']:.0f}M  {r['date']}  "
          f"{b['ats']}: {b['roles']} roles{rec}, {ta}")
    print(f"    {r['title'][:74]}")
print("-" * 78)
print("no public board found (check careers page by hand, or park):")
for r in cold:
    print(f"  {r['company']:<24} {r['cur']}{r['amount']:.0f}M  {r['date']}  [{r['src']}]")
