#!/usr/bin/env python3
"""Shared definitions for index.py and index_post.py.

WHY THIS FILE EXISTS (24 Aug 2026 audit)
    index.py tracked 41 boards and index_post.py tracked 45. Same morning,
    index.py said "1,617 roles across 41 boards" and index_post.py said
    "1,806 roles across 45". One of those numbers goes in cold emails and the
    other gets published on LinkedIn. A prospect who read the post and then got
    an email saw two different figures for the same index.

    Four boards (amber, callosum, dash0, humanoid) existed only in the post.
    funding_radar.py surfaced a Callosum round that the internal index could
    not see at all.

    Anything both scripts rely on lives here now. Do not redefine it locally.
"""
import datetime
import re

# The board universe. ONE list. Adding a company means adding it here.
SLUGS = """peec wordsmith aveni olix monumental jupus kittl choco kombo langdock
legora lovable taktile pleo the-exploration-company proxima-fusion tacto
black-forest-labs enpal pennylane alan deepl sereact n8n qonto dust photoroom
nabla forto juro sylvera 1x sanity multiverse nelly corti sorare ledger
knowunity upvest flip callosum dash0 amber humanoid""".split()

# TA matching, tightened 25 Aug 2026. Bare "people" and "talent" swept in roles
# that are not recruiting at all: Qonto's "Full-Stack Engineer - People
# Products" was being counted as a recruiter req, and the TA-pressure count is
# what jumps a lead to the front of the queue. TA_WORDS stays as the loose list
# other code imports; categorize() uses the patterns below.
TA_WORDS = ("recruit", "talent", "people", "hr ")

TA_PATTERNS = ("recruit", "talent acquisition", "talent partner",
               "talent associate", "talent manager", "talent operations",
               "talent lead", "sourcer", "people operations", "people partner",
               "people & culture", "people and culture", "head of people",
               "chief people", "people team", "hr ", "hrbp", "human resources",
               # 25 Aug 2026, second pass: the first tightening over-corrected
               # and dropped genuine HR roles that do not use the words
               # "operations" or "partner". Photoroom's "Snr People Generalist"
               # disappeared from the TA list entirely, and a freelance People
               # Generalist covering a permanent gap is exactly the signal the
               # TA-pressure rule exists to catch.
               "people generalist", "people manager", "people lead",
               "people advisor", "people specialist", "people business partner",
               "people & talent", "people experience", "hr business partner",
               "head of talent", "vp people", "people officer")

ENG_NOUNS = ("engineer", "developer", "scientist", "devops", "architect",
             "physicist", "technician")

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
             "didn't find", "did not find", "can't find", "cannot find",
             # Caught 25 Aug 2026: Knowunity's "Don't see your dream role?
             # Convince us to create it." was counted as a real 337-day role.
             # It was both the oldest role on that board and the reason its
             # median read 125 days.
             "dream role", "convince us", "see your role", "your dream job",
             # 25 Aug 2026, found by an integration test: the 24 Aug fix added
             # the German "initiativbewerbung" and missed its English twin. A
             # 634-day "Unsolicited Application - Permanent" was the SECOND
             # oldest role in the whole index, and two of the thirty-one roles
             # in the published ">300 day club" were speculative postings.
             "unsolicited application", "unsolicited applications")

# Bump this whenever EVERGREEN or categorize() changes. board_history.json
# stamps it, and index.py refuses to diff across a version boundary rather than
# reporting filter changes as hiring activity. See the velocity note in index.py.
FILTER_VERSION = 4


def is_evergreen(title):
    t = (title or "").lower()
    return any(k in t for k in EVERGREEN)


def categorize(title):
    """Bucket a job title.

    TA IS TESTED FIRST, ON PURPOSE (24 Aug 2026 audit). When engineering was
    tested first it swallowed every recruiting role with "Engineering" in the
    title: "Engineering Recruitment Lead", "Senior Talent Acquisition Partner,
    Engineering", "HR Business Partner - Engineering, Product, Design". That
    dragged the published recruiting median from 38 days down to 36, and 36 is
    the exact number the weekly post's closing line quotes. The punchline was
    wrong by two days because of an ordering accident.
    """
    t = (title or "").lower()
    # The HEAD of the title decides what the job is. "Senior Talent Acquisition
    # Partner, Engineering" is a recruiter (head: talent acquisition);
    # "Full-Stack Engineer - People Products" is an engineer (head: engineer).
    # Testing engineering nouns across the whole string got the first one wrong,
    # testing TA words across the whole string got the second one wrong, and
    # both errors moved published medians.
    head = re.split(r"[,\-\u2013|(/]", t)[0]
    if "recruit" in t or "sourcer" in t:
        return "ta"
    if any(k in t for k in TA_PATTERNS) and not any(k in head for k in ENG_NOUNS):
        return "ta"
    if any(k in t for k in ENG_NOUNS):
        return "eng"
    if any(k in t for k in ("sales", "account executive", "sdr", "bdr",
                            "revenue", "business development", "gtm",
                            "partnership")):
        return "sales"
    return "other"


def age_days(iso, today=None):
    """Days since an ISO date. Returns None on anything unparseable rather than
    killing the run. index.py used to crash on a single malformed publishedAt."""
    today = today or datetime.date.today()
    try:
        return (today - datetime.date(*map(int, (iso or "")[:10].split("-")))).days
    except Exception:
        return None
