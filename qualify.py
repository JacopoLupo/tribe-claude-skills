#!/usr/bin/env python3
"""The morning qualification pass: every recent round, sorted into three tiers.

WHY THIS EXISTS (Jacopo, 25 Aug 2026: "I think we should qualify the leads in
the morning with all the recent companies that received the investing round in
general, and then categorize them as tier 1 2 and 3")

    The radar was finding companies and then losing most of them. On the morning
    of 25 August it swept 14 funded companies and could score exactly 3 boards.
    The other 11 printed under "no public board found" and were never looked at
    again: MAASH at 12M, LITILIT at 8M, Neno at 6.6M. Those are not bad leads.
    They are leads the script could not open, because it was guessing ATS slugs
    from the company name in a press headline.

    That 21% resolution rate was the real ceiling on lead supply, and no new data
    source was needed to lift it. A human resolves a company in ten seconds: find
    the website, click Careers, read the ATS off the URL. So does this.

WHY TIERS RATHER THAN A SINGLE LIST
    The instinct to contact everyone who raised is right, and the desk's own
    numbers support it: 4 acceptances from 10 double-channel connects against 0
    replies from roughly 35 emails sent alone. But it is right for LinkedIn, not
    for email, and for one specific reason.

    The email works because it carries a number from the prospect's own board.
    "Your AE has been open 218 days, the market median is 32." Take the number
    away and what is left is a generic RPO pitch, which is exactly the shape of
    the cohort that got zero replies. Emailing an unresolvable company is not
    more outreach, it is worse outreach at higher volume. And volume is capped at
    two sends a day anyway, so more leads produce a longer backlog, not more mail.

    So the tiers split on what can actually be said to each company today:

      TIER 1  board resolved, EMEA, momentum, no recruiter of their own.
              Email plus connect. Takes one of the two daily send slots.
      TIER 2  funded and EMEA, but the board will not open, or they already
              have a TA function, or it is too small to argue from.
              CONNECT REQUEST ONLY, no email. Costs no send slot, which is why
              this tier can be fifteen a day instead of two. When they accept,
              the acceptance message re-scans the board, and by then there
              usually is one.
      TIER 3  resolved but not moving yet. Add to the board index and let the
              nightly velocity diff promote them the week they start hiring,
              which is before any competitor knows.
      OUT     outside EMEA, a staffing agency, or already in the CRM.

USAGE
    python3 qualify.py --days 3
    python3 qualify.py --days 7 --crm crm_domains.json     # dedupe against HubSpot
    python3 qualify.py --days 3 --json qualified.json      # machine-readable

    crm_domains.json is a flat list of domains and company names already on the
    portal, exported before the run. The script has no HubSpot credentials and
    will not pretend to: without --crm it says so in the header rather than
    printing a dedupe it did not do.
"""
import concurrent.futures as cf
import datetime
import json
import re
import sys

import funding_radar as fr

DAYS = 3
CRM_PATH = None
JSON_OUT = None
for i, a in enumerate(sys.argv[1:]):
    if a == "--days" and i + 2 <= len(sys.argv[1:]):
        DAYS = int(sys.argv[i + 2])
    if a == "--crm":
        CRM_PATH = sys.argv[i + 2]
    if a == "--json":
        JSON_OUT = sys.argv[i + 2]

TODAY = datetime.date.today()

# Companies that raise money and are not prospects. Staffing and recruitment
# firms raise rounds constantly and score beautifully on every signal this tool
# measures: lots of open roles, hiring fast, no internal TA function. They are
# competitors. The radar has flagged this in prose since 20 Aug and nothing
# checked it.
AGENCY = ("recruit", "staffing", "talent solutions", "headhunt", "rpo",
          "executive search", "job board", "hiring platform", "ats ")

# Publisher and utility domains that appear in every article's outbound links.
# The company's own site is whatever is left after these are removed.
NOT_THE_COMPANY = (
    "eu-startups", "tech.eu", "techfundingnews", "arcticstartup", "siliconcanals",
    "startuprise", "finsmes", "twitter.com", "x.com", "linkedin.com",
    "facebook.com", "instagram.com", "youtube.com", "google.com", "gravatar",
    "wordpress", "gstatic", "doubleclick", "crunchbase.com", "wikipedia.org",
    "apple.com", "play.google", "medium.com", "github.com", "mailto:",
    # Page furniture, added after the first live run resolved eight of eleven
    # companies to w3.org or bsky.app. Counting links picks whatever the theme
    # repeats, which is never the company. Kept as a floor under the name match
    # below rather than as the mechanism.
    "w3.org", "bsky.app", "schema.org", "creativecommons", "wp.com", "wp-",
    "cloudflare", "jetpack", "fonts.", "adobe.com", "mozilla", "gmpg.org",
    "purl.org", "ogp.me", "feedburner", "paypal", "amazon.", "reddit.com",
    "tiktok.com", "threads.net", "whatsapp", "t.me", "mastodon", "substack.com",
    "cdn.", "static.", "gravatar.com", "pinterest", "vimeo.com", "spotify.com",
)

# Suffixes tried when the article does not link the company, before giving up.
# Cheap: one HEAD-ish fetch each, and it recovers the single-word names that
# press releases mention without linking.
TLDS = (".com", ".io", ".ai", ".eu", ".co", ".de", ".fr", ".nl", ".se", ".fi",
        ".dk", ".es", ".it", ".tech", ".app", ".xyz")


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


# ATS providers, read off a careers URL rather than guessed from a name. The
# order matters only for reporting; a company is on exactly one of these.
ATS_URL = [
    (r"jobs\.ashbyhq\.com/([a-z0-9\-\.]+)", "ashby"),
    (r"jobs\.lever\.co/([a-z0-9\-]+)", "lever"),
    (r"boards\.greenhouse\.io/([a-z0-9_\-]+)", "greenhouse"),
    (r"job-boards\.greenhouse\.io/([a-z0-9_\-]+)", "greenhouse"),
    (r"apply\.workable\.com/([a-z0-9\-]+)", "workable"),
    (r"([a-z0-9\-]+)\.recruitee\.com", "recruitee"),
    (r"careers\.smartrecruiters\.com/([a-zA-Z0-9\-]+)", "smartrecruiters"),
    (r"([a-z0-9\-]+)\.jobs\.personio\.de", "personio"),
    (r"([a-z0-9\-]+)\.join\.com", "join"),
    (r"([a-z0-9\-]+)\.teamtailor\.com", "teamtailor"),
]

CAREERS_HINT = re.compile(
    r'href=["\']([^"\']*(?:career|jobs|join-us|joinus|work-with-us|vacanc|'
    r'stellen|offres|hiring)[^"\']*)["\']', re.I)
HREF = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.I)


def company_domain(name, article_url):
    """Find the company's own site: match the article's outbound links against
    the company NAME, then fall back to constructing the domain.

    The first live run counted links instead and resolved eight of eleven
    companies to w3.org or bsky.app, because a WordPress theme links its own
    boilerplate on every page and the startup exactly once. Frequency measures
    the publisher's furniture. The name is what identifies the company, so match
    on the name and use frequency only to break ties among real candidates.
    """
    want = _norm(name)
    if len(want) < 3:
        return None
    candidates = {}
    raw = fr.fetch(article_url, 10) if article_url else None
    if raw:
        html = raw.decode("utf-8", "ignore")
        for url in HREF.findall(html):
            host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0].lower()
            if not host or "." not in host:
                continue
            if any(b in host for b in NOT_THE_COMPANY):
                continue
            reg = _norm(host.split(".")[0])
            if not reg:
                continue
            # The registrable label has to actually look like the company:
            # either it contains the name, or the name contains it. "maash"
            # matches maash.io; "solacecare" matches solace.health.
            if reg in want or want in reg or want.startswith(reg[:6] or "~"):
                candidates[host] = candidates.get(host, 0) + 1
    if candidates:
        return sorted(candidates, key=lambda h: (-candidates[h], len(h)))[0]

    # Nothing linked. Construct it, and verify the page actually mentions the
    # company, because plenty of short names resolve to somebody else's parked
    # domain and a wrong domain is worse than no domain.
    stem = _norm(name)
    for tld in TLDS:
        host = stem + tld
        raw = fr.fetch("https://" + host, 8)
        if raw and want[:8] in _norm(raw[:200000].decode("utf-8", "ignore")):
            return host
    return None


# Paths a careers page actually lives at. Tried directly when the homepage does
# not link one in plain HTML, which is most modern sites: the nav is rendered by
# JavaScript and a fetch of the homepage sees an empty shell. dust.tt and
# enpal.de both have boards and both returned nothing on the link-scrape alone.
CAREERS_PATHS = (
    "careers", "jobs", "career", "join-us", "joinus", "company/careers",
    "about/careers", "en/careers", "en/jobs", "karriere", "de/karriere",
    "work-with-us", "about-us/careers", "company/jobs", "vacancies",
    "offres-emploi", "recruitment", "team",
)


def ats_from_site(domain):
    """Homepage, then the usual careers paths, then any careers link in the
    HTML. Reads the ATS off the URL the way a person would.

    Scans the raw HTML rather than only href attributes, because plenty of sites
    embed the board in an iframe or hand the slug to a script, and both put the
    provider URL in the page source without ever writing an <a href> for it.
    """
    def scan(text):
        for pat, prov in ATS_URL:
            m = re.search(pat, text, re.I)
            if m:
                return prov, m.group(1)
        return None

    home = None
    for scheme in ("https://", "https://www."):
        home = fr.fetch(scheme + domain, 10)
        if home:
            break
    if home:
        hit = scan(home.decode("utf-8", "ignore"))
        if hit:
            return hit

    for path in CAREERS_PATHS:
        raw = fr.fetch(f"https://{domain}/{path}", 8)
        if not raw:
            continue
        hit = scan(raw.decode("utf-8", "ignore"))
        if hit:
            return hit

    if home:
        html = home.decode("utf-8", "ignore")
        for path in CAREERS_HINT.findall(html)[:6]:
            url = path if path.startswith("http") else (
                "https://" + domain.rstrip("/") + "/" + path.lstrip("/"))
            sub = fr.fetch(url, 8)
            if sub:
                hit = scan(sub.decode("utf-8", "ignore"))
                if hit:
                    return hit
    return None


def resolve(r):
    """Name -> domain -> careers -> ATS. Falls back to the old slug guessing,
    but records WHICH route found the board, because a board found by guessing
    still needs confirming by eye and a board found from the company's own
    careers link does not."""
    r["domain"] = company_domain(r["company"], r.get("link") or "")
    r["route"] = None
    r["ats_known"] = None
    if r["domain"]:
        hit = ats_from_site(r["domain"])
        if hit:
            prov, slug = hit
            # Knowing WHERE the board is matters even when it is empty today.
            # Neno has an Ashby account and zero live roles. "No board
            # reachable" and "board found, nothing posted yet" are opposite
            # facts: the first means we cannot see them, the second means we
            # can watch the exact address and will know the day they start.
            r["ats_known"] = f"{prov}/{slug}"
            r["route"] = "careers-link"
            r["board"] = probe_known(slug)
            if r["board"]:
                r["board"]["verify"] = False
                return r
    r["board"] = fr.probe_boards(r["company"])
    if r["board"]:
        r["route"] = "slug-guess"
    return r


def probe_known(slug):
    """Score a board whose address we already resolved. Reuses the radar's own
    probe so there is one implementation of 'what counts as a role' rather than
    two that drift."""
    return fr.probe_boards(slug, slugs=[slug])


def tier(r, known):
    b = r.get("board")
    name = (r["company"] + " " + r.get("title", "")).lower()
    dom = (r.get("domain") or "").lower()

    if any(k in name for k in AGENCY):
        return "OUT", "staffing or recruitment firm, a competitor not a client"
    if known and (dom in known or r["company"].lower() in known):
        return "OUT", "already on the portal, screen it there instead"
    if b:
        top, non_eu = b.get("locs", ("", None))
        if non_eu is not None and non_eu >= 0.5:
            return "OUT", f"{non_eu:.0%} of roles outside EMEA ({top})"

    if not b:
        if r.get("ats_known"):
            return "T3", (f"board found at {r['ats_known']} with nothing live "
                          f"yet, so watch that address")
        return "T2", "no board reachable, so there is no number to write an email around"
    if b["ta"]:
        return "T2", f"{b['ta']} TA role(s) of their own, so lead with the person not the gap"
    recent = b["recent"] if b["recent"] is not None else b["roles"] * 0.25
    if recent >= 3 or b["roles"] >= 10:
        return "T1", f"{b['roles']} roles, {b['recent'] if b['recent'] is not None else '~'} fresh, no recruiter"
    return "T3", f"only {b['roles']} roles and not moving yet, watch the diff"


def main():
    fr.DAYS = DAYS
    rounds = []
    with cf.ThreadPoolExecutor(8) as ex:
        for lst in ex.map(fr.parse_feed, fr.FEEDS):
            rounds.extend(lst)
    by_name = {}
    for r in rounds:
        k = r["company"].lower()
        if k not in by_name or r["amount"] > by_name[k]["amount"]:
            by_name[k] = r
    rounds = sorted(by_name.values(), key=lambda r: -r["amount"])

    with cf.ThreadPoolExecutor(10) as ex:
        rounds = list(ex.map(resolve, rounds))

    known = set()
    if CRM_PATH:
        known = {str(x).lower().strip() for x in json.load(open(CRM_PATH))}

    for r in rounds:
        r["tier"], r["why"] = tier(r, known)

    buckets = {k: [r for r in rounds if r["tier"] == k]
               for k in ("T1", "T2", "T3", "OUT")}
    resolved = sum(1 for r in rounds if r.get("board"))
    by_careers = sum(1 for r in rounds if r.get("route") == "careers-link")

    print(f"QUALIFICATION PASS {TODAY} | last {DAYS} days | "
          f"{len(rounds)} funded companies")
    print(f"boards resolved: {resolved}/{len(rounds)} "
          f"({resolved * 100 // max(len(rounds), 1)}%), "
          f"{by_careers} from the company's own careers link")
    if not CRM_PATH:
        print("!!! NO CRM FILE GIVEN, so nothing here is deduped against HubSpot.")
        print("    Export the portal's domains and pass --crm, or screen every")
        print("    name by hand before writing. Do not read this list as new.")
    print("=" * 78)
    print(f"  TIER 1  email + connect, uses a send slot   {len(buckets['T1']):>3}")
    print(f"  TIER 2  connect request only, no send slot  {len(buckets['T2']):>3}")
    print(f"  TIER 3  watch, promote on the velocity diff {len(buckets['T3']):>3}")
    print(f"  OUT     excluded, with a reason each        {len(buckets['OUT']):>3}")
    print("=" * 78)

    for key, head in (("T1", "TIER 1, write the email today"),
                      ("T2", "TIER 2, connect request only"),
                      ("T3", "TIER 3, watch list"),
                      ("OUT", "EXCLUDED")):
        rows = buckets[key]
        if not rows:
            continue
        print(f"\n--- {head} ({len(rows)}) ---")
        for r in rows:
            amt = f"{r['amount']:.1f}" if r["amount"] < 10 else f"{r['amount']:.0f}"
            dom = r.get("domain") or "domain not found"
            print(f"  {r['company'][:26]:<26} {r['cur']}{amt}M  {dom}")
            print(f"      {r['why']}")
            if r.get("board"):
                b = r["board"]
                tag = " [VERIFY SLUG]" if b.get("verify") else ""
                print(f"      {b['ats']}{tag}, via {r['route']}, "
                      f"locations: {b.get('locs', ('', None))[0]}")
            elif r.get("ats_known"):
                print(f"      {r['ats_known']}, empty today, add to the watch list")

    print(f"\nSend slots are 2 a day and tier 1 has {len(buckets['T1'])}. "
          f"Tier 2 costs no slot,\nbut LinkedIn throttles invitations at roughly "
          f"100 a week, so 15 to 20 a day is\nthe real ceiling there. Tier 3 goes "
          f"into board_common.SLUGS and costs nothing\nuntil the nightly diff "
          f"promotes it.")

    if JSON_OUT:
        json.dump([{k: v for k, v in r.items() if k != "board"} |
                   {"board": r.get("board")} for r in rounds],
                  open(JSON_OUT, "w"), indent=1, default=str)
        print(f"\nwrote {JSON_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
