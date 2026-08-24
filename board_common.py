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

# The board universe. ONE list. Adding a company means adding it here.
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

# Bump this whenever EVERGREEN or categorize() changes. board_history.json
# stamps it, and index.py refuses to diff across a version boundary rather than
# reporting filter changes as hiring activity. See the velocity note in index.py.
FILTER_VERSION = 2


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
    if any(k in t for k in TA_WORDS):
        return "ta"
    if any(k in t for k in ("engineer", "developer", "scientist", "devops",
                            "architect", "physicist", "technician")):
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
