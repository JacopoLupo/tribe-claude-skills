#!/usr/bin/env python3
"""Preflight gate. Nothing reaches Jacopo until this exits 0.

WHY THIS EXISTS
    On 25 August 2026 the desk broke three rules in one morning, and all three
    were rules that had been written down clearly, some of them the day before:

      1. Upvest was screened "clean" and prepped for a send. Another agent on
         the portal had been working it for weeks. The screen had looked at the
         COMPANY record's owner and notes_last_contacted, and the evidence was
         in notes written by that agent. HubSpot's notes_last_contacted does not
         move when a note is written, so the one property the rule named is the
         one property that cannot see the thing it was looking for.
      2. amber was screened "clean" the same way. Its CEO had been emailed the
         previous afternoon and sat at ATTEMPTED_TO_CONTACT on the CONTACT
         record, which the screen never opened.
      3. Three LinkedIn connect notes were improvised from the email's opening
         line instead of the documented four-beat template.

    Jacopo caught all three. The desk caught none of them. The common shape is
    not carelessness: it is that every one of those rules lived in prose with no
    moment where anything verified it. A rule with no gate is a wish.

WHAT THIS CAN AND CANNOT DO, STATED HONESTLY
    This script has no HubSpot credentials and never will. It cannot run the
    screening queries itself. What it CAN do is refuse to pass a batch until the
    ANSWERS to those queries are present and internally consistent, which means
    the queries cannot be skipped and then quietly forgotten. The text checks
    (connect note shape, reminder line, em-dashes, word counts, BCC, location
    gate) are fully mechanical and need nothing from anyone.

USAGE
    python3 preflight.py batch.json          # gate a batch, exit 1 on failure
    python3 preflight.py --template          # print a blank batch to fill in
    python3 preflight.py --selftest          # prove the gate catches what it claims

EXIT CODES
    0  every lead in the batch passed, safe to present
    1  at least one BLOCKER, do not present the batch
    2  the batch file itself is malformed
"""
import datetime
import json
import re
import sys

TODAY = datetime.date.today()

# The four-beat note, as settled from the Velatir/Sørensen note that Jacopo
# named the template. Beat 1 has exactly two permitted openings: the normal one,
# and the one used when no verified email exists so the note IS the channel.
BEAT1 = (
    r"^I sent you an email earlier, this is the second door\.",
    r"^LinkedIn is the front door here, I could not find a work address for you\.",
    r"^I tried reaching you by email and it bounced",
)
# Beat 2+3 run as one sentence: <choice> instead of <alternative> is a <adj>
# choice and I like it. The "instead of" is load-bearing: it is what makes the
# sentence name a trade-off rather than pay a compliment.
BEAT23 = r"\binstead of\b.{5,140}?\bis an? [a-z]+ choice and I like it\."
BEAT4 = r"(?:Would be glad|Glad) to connect and follow how it goes\.$"

NOTE_MAX = 300

# Phrases that mark the note doing the email's job, which is the exact failure
# of 25 August. Board facts belong in the email; the note carries the person.
NOTE_BANNED = (
    "i scan the job boards", "i track the job boards", "boards i track",
    "open roles", "days", "recruiter", "median", "%", "percent",
)

VARIANT_SPECS = {
    # variant: (min words, max words, subject rule, must contain, must not contain)
    "A": (55, 110, None, (), ("coffee chat", "this week i checked")),
    # B's subject follows the same fact-based convention as A and C. It used to
    # be "Tribe / [category] comparison"; the 24 Aug fix killed that pattern by
    # name and the two rules stood side by side for six days, which is how a
    # dead subject reached a real draft on 25 August.
    "B": (180, 320, None, ("Tribe was nowhere in the results",), ()),
    "C": (55, 95, None, (), ("first shortlist", "cost per hire", "4,300")),
    "W": (60, 120, None, (), ()),
}

RED_LINE = "DELETE THIS LINE BEFORE SENDING"
# The portal's option value, copied from get_properties. The en dash is real and
# the template used to print a hyphen, which writes an invalid enum silently.
LEGAL_BASIS = "Legitimate interest \u2013 prospect/lead"
BCC = "146748263@bcc.eu1.hubspot.com"


def fail(bag, lead, msg):
    bag.append(("BLOCK", lead, msg))


def warn(bag, lead, msg):
    bag.append(("WARN", lead, msg))


def check_screen(bag, name, s):
    """The three screening questions that were each missed once this week.

    Every field is required. A missing field is a blocker, not a default,
    because "absent" is exactly how amber and Upvest passed: nobody had looked,
    and nothing distinguished not-looked-at from looked-at-and-clean.
    """
    required = ("company_owner_id", "contact_lead_statuses", "agent_notes_count",
                "last_touch_date", "parked", "touches_spent")
    for k in required:
        if k not in s:
            fail(bag, name, f"screen.{k} missing. Run the query and record the "
                            f"answer; an unanswered screen is not a clean screen.")
    if not all(k in s for k in required):
        return

    owner = str(s["company_owner_id"] or "")
    if owner and owner != "33687989":
        fail(bag, name, f"company is owned by {owner}, not Jacopo. Park it and "
                        f"name whose it is.")

    worked = [x for x in s["contact_lead_statuses"]
              if str(x).upper() in ("ATTEMPTED_TO_CONTACT", "IN_PROGRESS",
                                    "CONNECTED", "OPEN_DEAL", "BAD_TIMING",
                                    "UNQUALIFIED")]
    if worked:
        fail(bag, name, f"a contact on this account is already at {worked[0]}. "
                        f"This is the amber failure: the company record looked "
                        f"clean and the contact record did not.")

    if s["agent_notes_count"]:
        fail(bag, name, f"{s['agent_notes_count']} notes from another agent on "
                        f"this account. This is the Upvest failure. Ask Jacopo "
                        f"before touching it.")

    spent = s.get("touches_spent")
    if spent is None:
        fail(bag, name, "screen.touches_spent missing. The four queries catch "
                        "ANOTHER agent's work and RECENT contact; they do not "
                        "catch our own finished ladder. Proxima Fusion's real "
                        "state, two touches spent and no third email to that "
                        "name, lived only in a task body.")
    elif spent >= 2:
        fail(bag, name, f"{spent} touches already spent on this name. The ladder "
                        f"is two per person, then route to a second name or "
                        f"park. Never a third email to the same inbox.")

    if s["parked"]:
        fail(bag, name, "account is parked. Read the park's own reopen "
                        "condition and say whether it is met, rather than "
                        "obeying or ignoring the word 'parked'.")

    if s["last_touch_date"]:
        try:
            d = datetime.date.fromisoformat(str(s["last_touch_date"])[:10])
            gap = (TODAY - d).days
            if gap < 7:
                fail(bag, name, f"last touch was {gap} days ago. The floor is "
                                f"seven days between touches on one person, "
                                f"warmth included.")
        except ValueError:
            fail(bag, name, f"last_touch_date '{s['last_touch_date']}' is not a "
                            f"date I can read.")


def check_board(bag, name, b):
    """A board fact is only as good as the scan it came from."""
    if not b:
        fail(bag, name, "no board block. Every first touch quotes the prospect's "
                        "own board, so a lead with no scan has nothing to say.")
        return
    scan = str(b.get("scan_date", ""))[:10]
    if scan != str(TODAY):
        fail(bag, name, f"board scan is dated {scan or 'never'}, not today. "
                        f"Boards move daily and a role that came down yesterday "
                        f"turns the opening line into a correction.")
    frac = b.get("non_eu_fraction")
    if frac is None:
        warn(bag, name, "no location distribution on the board. Print it before "
                        "this becomes another 1X, where every number was true "
                        "and every role was in California.")
    elif frac >= 0.5:
        fail(bag, name, f"{frac:.0%} of the roles are outside EMEA. Tribe sells "
                        f"EMEA hiring.")


def check_email(bag, name, e):
    if not e:
        return
    variant = str(e.get("variant", "")).upper()
    if variant not in VARIANT_SPECS:
        fail(bag, name, f"variant '{variant}' is not A, B, C or W.")
        return
    lo, hi, subj_rule, must, must_not = VARIANT_SPECS[variant]

    body = e.get("body", "") or ""
    subject = (e.get("subject", "") or "").strip()

    if RED_LINE not in body:
        fail(bag, name, "no red reminder line. It is what stops a send going "
                        "out untracked at the end of a long day.")
    if BCC not in (e.get("bcc") or ""):
        fail(bag, name, f"BCC is not {BCC}, so the send would never reach the CRM.")
    if not e.get("to"):
        fail(bag, name, "empty To. Never a guessed address, and never an empty one.")
    elif not e.get("address_verified"):
        # 25 Aug 2026, found by an integration test: the rule reads "never a
        # guessed address, and never an empty one" and the check only enforced
        # the second half. A fabricated firstname.lastname@ passed green.
        fail(bag, name, f"address_verified is not true for {e.get('to')}. An "
                        f"address is verified when an enrichment tool returned "
                        f"it as valid, it is already on the HubSpot record, or "
                        f"it came from something they published. A pattern "
                        f"inferred from a colleague's address is a guess: "
                        f"DeepL's Head of TA is firstname.lastname@ and the CEO "
                        f"is lastname@.")
    basis = (e.get("legal_basis") or "").strip()
    if basis and basis != LEGAL_BASIS:
        fail(bag, name, f"legal_basis is {basis!r}. This portal's option is "
                        f"{LEGAL_BASIS!r}, with an EN DASH, and a create call "
                        f"carrying the hyphen version writes an invalid enum on "
                        f"the one field that decides whether this account can "
                        f"ever be measured.")
    if not basis:
        fail(bag, name, "no GDPR lawful basis on the contact. The email will "
                        "send and can never register an open, which is the gap "
                        "that made a month of results unreadable.")

    # WORD COUNT, fixed 25 Aug 2026. The old version stripped bracketed text
    # (which already removes the reminder line) and THEN subtracted another 25
    # words for it. Double-discounted, so the skill's own canonical variant A
    # example, 72 words, scored 51 and tripped a warning: the template the skill
    # says to copy failed the gate the skill says to run. Strip the scaffolding
    # explicitly, count what is left, and do not subtract twice.
    prose = body
    for line in prose.splitlines():
        if RED_LINE in line:
            prose = prose.replace(line, "")
    prose = re.sub(r"\[.*?\]", "", prose)
    words = len([w for w in prose.split() if w.strip()])
    if not (lo <= words <= hi):
        warn(bag, name, f"variant {variant} runs {words} words, outside its "
                        f"{lo} to {hi} range.")

    low = body.lower()
    for phrase in must:
        if phrase.lower() not in low:
            fail(bag, name, f"variant {variant} is missing its defining line: "
                            f"'{phrase}'.")
    for phrase in must_not:
        if phrase.lower() in low:
            fail(bag, name, f"variant {variant} contains '{phrase}', which was "
                            f"deliberately removed from it.")
    if subj_rule and not subject.lower().startswith(subj_rule):
        fail(bag, name, f"variant {variant} subject should start '{subj_rule}', "
                        f"got '{subject}'.")
    if subject.lower().startswith("tribe /"):
        fail(bag, name, "'Tribe /' subject. Killed on 24 Aug 2026: it is a vendor "
                        "announcing itself, and every send in the zero-reply "
                        "cohort had one. Build the subject from the hardest "
                        "number in the email.")
    if len(subject) > 45:
        warn(bag, name, f"subject is {len(subject)} chars, over the 45 the "
                        f"convention asks for.")
    if "calendly.com" in body.lower():
        # Jacopo moved to a Google Calendar appointment schedule on 25 Aug 2026.
        # The old link still works, which is exactly why it survives in drafts
        # nobody re-reads, and it sends prospects to a booking page he has
        # stopped watching.
        fail(bag, name, "the signature still points at Calendly. It is the "
                        "Google Calendar appointment schedule now, and a dead "
                        "booking link is worse than no link.")
    if "—" in body or "–" in body:
        fail(bag, name, "em or en dash in the body. Jacopo does not use them "
                        "and they are the loudest tell that a machine wrote it.")


def check_followup(bag, name, lead):
    """Every send names its successor, with a date, at the moment it is prepped.

    Both skills say this and nothing checked it, which is how forty overdue
    LinkedIn tasks accumulated across three months and how the one account whose
    send bounced ended up with no dated task at all. A closed task with no
    successor is invisible to every overdue check by construction: nothing is
    overdue, because nothing exists.
    """
    f = lead.get("followup")
    if not f:
        fail(bag, name, "no followup block. A send with no dated successor is an "
                        "account that stops moving silently, and no overdue check "
                        "can see it because nothing is overdue.")
        return
    due = f.get("due")
    what = f.get("what")
    if not what:
        fail(bag, name, "followup.what is empty. 'Follow up' is not a next step; "
                        "name what the touch has to carry that the first did not.")
    if not due:
        fail(bag, name, "followup.due is empty. Run followup_ladder.py rather "
                        "than picking a date at the end of a long day.")
        return
    try:
        d = datetime.date.fromisoformat(str(due)[:10])
    except ValueError:
        fail(bag, name, f"followup.due '{due}' is not a date.")
        return
    gap = (d - TODAY).days
    if gap < 7:
        fail(bag, name, f"followup is {gap} days out. The floor is seven days "
                        f"between touches on one person. Optiml got five emails "
                        f"in eight days and the answer was no.")
    elif gap > 28:
        warn(bag, name, f"followup is {gap} days out. Past about four weeks the "
                        f"thread is cold and touch 2 reads as a new cold email.")


def check_note(bag, name, note, has_email):
    if note is None:
        fail(bag, name, "no connect note. The double channel is not optional: a "
                        "prep with an email and no note is unfinished.")
        return
    note = note.strip()
    n = len(note)
    if n > NOTE_MAX:
        fail(bag, name, f"note is {n} characters, over LinkedIn's {NOTE_MAX}. "
                        f"It would be truncated mid-sentence.")
    if not any(re.match(p, note) for p in BEAT1):
        fail(bag, name, "note does not open on one of the two permitted first "
                        "beats. This is the 25 August failure: the note was "
                        "written from the email's opening line instead of the "
                        "template.")
    if not re.search(BEAT23, note):
        fail(bag, name, "note has no '<choice> instead of <alternative> is a "
                        "<adjective> choice and I like it'. Without the 'instead "
                        "of' it praises an outcome rather than naming a "
                        "trade-off, which is flattery with a name filled in.")
    if not re.search(BEAT4, note):
        fail(bag, name, "note does not close on connect and follow. The email "
                        "carries the pitch; the note carries the person.")
    if "—" in note or "–" in note:
        fail(bag, name, "em or en dash in the connect note. The ban is not "
                        "email-only: it is the loudest tell that a machine "
                        "wrote it, and LinkedIn notes are read more carefully "
                        "than emails because they are shorter.")
    hits = [w for w in NOTE_BANNED if w in note.lower()]
    if hits:
        fail(bag, name, f"note contains {hits}, which is the email's evidence. "
                        f"Board numbers do not go in the note.")
    if has_email and not note.startswith("I sent you an email"):
        warn(bag, name, "there is an email for this lead, so the note should "
                        "name it in its first clause.")
    if not has_email and note.startswith("I sent you an email"):
        fail(bag, name, "the note claims an email that does not exist for this "
                        "lead.")


def check_daily_cap(bag, batch, leads):
    """Two outbound sends a day, counting what is ALREADY on the list.

    Added 25 Aug 2026, after the gate passed a two-lead batch for a day that
    already carried four follow-up sends dated weeks earlier. The gate could not
    see them because nothing told it, which is the same shape as every other
    failure this file exists for: the rule was real, and no step supplied the
    number. So the batch has to declare it.

    The cap counts cold first touches, warm first touches and follow-up SENDS.
    It does not count the desk's own bookkeeping: bounce checks, park reviews,
    connect checks, "find an address". Nine tasks on one morning get
    bulk-snoozed, and a snoozed task is worse than no task because it looks
    handled.
    """
    already = batch.get("sends_already_scheduled")
    new_sends = sum(1 for l in leads if l.get("email"))
    if already is None:
        fail(bag, "batch", "sends_already_scheduled missing. Count the send "
                           "tasks already dated for the same day before adding "
                           "to them, or the cap is enforced against an empty "
                           "list and means nothing.")
        return
    total = already + new_sends
    if total > 2:
        fail(bag, "batch", f"{already} send(s) already scheduled that day plus "
                           f"{new_sends} new = {total}. The cap is two. Move the "
                           f"newest cold sends rather than the follow-ups: a "
                           f"follow-up has a live thread behind it and a cold "
                           f"send does not.")


def check_rotation(bag, leads):
    """Variant C is opt-in only, and one variant twice in a day is not a test."""
    variants = [str((l.get("email") or {}).get("variant", "")).upper()
                for l in leads if l.get("email")]
    for v, l in zip(variants, [l for l in leads if l.get("email")]):
        if v == "W" and not l.get("variant_authorised"):
            fail(bag, l.get("company", "?"), "variant W needs Jacopo's explicit "
                                             "say-so before it is used.")
        if v == "C" and not l.get("variant_authorised"):
            warn(bag, l.get("company", "?"), "variant C is running. Confirm that "
                                             "is what Jacopo wants today.")
    if len(variants) >= 2 and len(set(variants)) == 1:
        warn(bag, "batch", f"every email in this batch is variant {variants[0]}. "
                           f"Two arms on the same day is what makes the day "
                           f"readable.")


def run(batch):
    bag = []
    leads = batch.get("leads", [])
    if not leads:
        return [("BLOCK", "batch", "no leads in the file.")]
    for lead in leads:
        name = lead.get("company", "unnamed")
        check_screen(bag, name, lead.get("screen") or {})
        check_board(bag, name, lead.get("board"))
        check_email(bag, name, lead.get("email"))
        if lead.get("email") or lead.get("connect_note"):
            check_followup(bag, name, lead)
        check_note(bag, name, lead.get("connect_note"), bool(lead.get("email")))
    check_rotation(bag, leads)
    check_daily_cap(bag, batch, leads)
    return bag


TEMPLATE = {
    "batch_date": str(TODAY),
    "sends_already_scheduled": 0,
    "leads": [{
        "company": "Example GmbH",
        "company_id": "0000",
        "variant_authorised": False,
        "screen": {
            "company_owner_id": "33687989",
            "contact_lead_statuses": ["NEW"],
            "agent_notes_count": 0,
            "last_touch_date": None,
            "parked": False,
            "touches_spent": 0
        },
        "board": {"roles": 0, "fresh14": 0, "ta": 0, "top_locations": "",
                  "non_eu_fraction": 0.0, "scan_date": str(TODAY)},
        "email": {"variant": "A", "to": "", "address_verified": False,
                  "bcc": BCC, "subject": "", "body": "",
                  "legal_basis": LEGAL_BASIS, "contact_id": ""},
        "connect_note": "",
        "followup": {"due": str(TODAY + datetime.timedelta(days=18)),
                     "what": "what touch 2 must carry that touch 1 did not"}
    }]
}


def selftest():
    """Prove the gate catches the three failures it was built for."""
    good_note = ("I sent you an email earlier, this is the second door. Building "
                 "it in Paris instead of the city where the logos are is a "
                 "contrarian choice and I like it. Would be glad to connect and "
                 "follow how it goes.")
    base = {
        "company": "Testco", "screen": {
            "company_owner_id": "33687989", "contact_lead_statuses": ["NEW"],
            "agent_notes_count": 0, "last_touch_date": None, "parked": False,
            "touches_spent": 0},
        "board": {"non_eu_fraction": 0.1, "scan_date": str(TODAY)},
        "email": {"variant": "A", "to": "a@b.com", "address_verified": True,
                  "bcc": BCC, "subject": "x",
                  "body": RED_LINE + "\n" + ("word " * 80),
                  "legal_basis": LEGAL_BASIS},
        "connect_note": good_note,
        "followup": {"due": str(TODAY + datetime.timedelta(days=18)),
                     "what": "touch 2 carrying whatever their board did in the "
                             "meantime"}}

    cases = []
    clean = json.loads(json.dumps(base))
    cases.append(("clean batch passes", clean, False))

    amber = json.loads(json.dumps(base))
    amber["screen"]["contact_lead_statuses"] = ["ATTEMPTED_TO_CONTACT"]
    cases.append(("amber: contact already worked", amber, True))

    upvest = json.loads(json.dumps(base))
    upvest["screen"]["agent_notes_count"] = 318
    cases.append(("upvest: another agent on the account", upvest, True))

    note = json.loads(json.dumps(base))
    note["connect_note"] = ("I track the job boards of 45 European scaleups every "
                            "morning and your board stood out. Happy to connect.")
    cases.append(("note improvised from the email", note, True))

    gdpr = json.loads(json.dumps(base))
    gdpr["email"]["legal_basis"] = ""
    cases.append(("no lawful basis", gdpr, True))

    nofu = json.loads(json.dumps(base))
    nofu.pop("followup")
    cases.append(("no dated successor task", nofu, True))

    soon = json.loads(json.dumps(base))
    soon["followup"]["due"] = str(TODAY + datetime.timedelta(days=3))
    cases.append(("successor inside the seven-day floor", soon, True))

    guessed = json.loads(json.dumps(base))
    guessed["email"]["address_verified"] = False
    cases.append(("guessed address in the To field", guessed, True))

    spent = json.loads(json.dumps(base))
    spent["screen"]["touches_spent"] = 2
    cases.append(("two touches already spent on this name", spent, True))

    hyphen = json.loads(json.dumps(base))
    hyphen["email"]["legal_basis"] = "Legitimate interest - prospect/lead"
    cases.append(("lawful basis with a hyphen instead of an en dash", hyphen, True))

    stale = json.loads(json.dumps(base))
    stale["board"]["scan_date"] = "2026-08-18"
    cases.append(("stale board scan", stale, True))

    ok = True
    for label, lead, should_block in cases:
        bag = run({"leads": [lead], "sends_already_scheduled": 0})
        blocked = any(sev == "BLOCK" for sev, _, _ in bag)
        good = blocked == should_block
        ok &= good
        print(f"  {'pass' if good else 'FAIL'}  {label}")
        if not good:
            for sev, who, msg in bag:
                print(f"          {sev} {who}: {msg}")
    print("\nselftest", "passed" if ok else "FAILED")
    return 0 if ok else 1


def main():
    if "--template" in sys.argv:
        print(json.dumps(TEMPLATE, indent=2))
        return 0
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    try:
        batch = json.load(open(args[0]))
    except Exception as e:
        print(f"cannot read {args[0]}: {e}")
        return 2

    bag = run(batch)
    blockers = [b for b in bag if b[0] == "BLOCK"]
    warns = [b for b in bag if b[0] == "WARN"]

    for sev, who, msg in blockers:
        print(f"BLOCK  {who}: {msg}")
    for sev, who, msg in warns:
        print(f"warn   {who}: {msg}")

    n = len(batch.get("leads", []))
    if blockers:
        print(f"\n{len(blockers)} blocker(s) across {n} lead(s). "
              f"Do NOT present this batch. Fix and re-run.")
        return 1
    print(f"\nPREFLIGHT GREEN: {n} lead(s), {len(warns)} warning(s). "
          f"Safe to present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
