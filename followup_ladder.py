#!/usr/bin/env python3
"""The follow-up ladder, computed rather than remembered.

WHY THIS EXISTS
    Two rules in these skills say the same thing from opposite ends: "every
    closed task names what happens next, by task ID and date", and "closing a
    send task and creating its successor happen in the same motion". Neither had
    anything computing the date, so the date came out of someone's head at the
    end of a long day, and the desk accumulated forty overdue LinkedIn tasks
    between May and August 2026 with nothing forcing the question.

    Worse, the accounts most likely to be forgotten were the ones this rule was
    built to protect. The successor task is created when a send is CONFIRMED, so
    an account whose send bounced never got one at all. Humanoid, the busiest
    board in the whole index, had no dated task of its own for two weeks.

    So: the ladder is arithmetic, and arithmetic belongs in a script. Give it
    the send date and it returns every downstream step with a real date, in the
    order they happen, including the ones for the failure paths.

USAGE
    python3 followup_ladder.py 2026-08-25                    # the ladder
    python3 followup_ladder.py 2026-08-25 --company Dust \\
        --contact 852374952132 --variant A --channel both    # task bodies too
    python3 followup_ladder.py --check 2026-09-15 2026-08-25  # is that date sane
    ... add --dm-sent when a DM actually went out, not just a connect request

THE LADDER, and why each gap is what it is
    +1 day    bounce check. Manually-sourced addresses get checked the next
              morning, because a bounce found late means a follow-up scheduled
              against an address that never worked.
    +3 days   connect acceptance check, only when a connect went out and is
              still pending. Three business days is the dialog's own default.
    +14 days  review the DM if one was sent. If silent, do NOT nudge on
              LinkedIn: the email ladder carries the account from here, one
              channel at a time.
    +18 days  touch 2, the second email to the same person. The floor is 7 days
              between touches and the range that works here is 2 to 3 weeks;
              18 days sits inside it and clears summer quiet periods.
    +39 days  route to a second name at the same company, or park. Never a
              third email to the same inbox.
    +60 days  the park review, if it parked. A park with no review date is a
              deletion with extra steps, and one nearly cost the best lead of
              the month.
"""
import datetime
import json
import signal
import sys

# Piping this into `head` is the normal way to read it, and an unhandled SIGPIPE
# prints a traceback that looks exactly like a crash.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

STEPS = [
    (1,  "bounce", "Bounce check: {company}",
     "Search from:mailer-daemon since the {sent} send. A manually sourced "
     "address is not settled until this passes. If it bounced, the connect note "
     "becomes the live channel and says so, and this account still gets a dated "
     "task rather than falling out of the batch."),
    (3,  "connect", "Connect check: {company}",
     "Did they accept? Accepted means the acceptance message goes out the same "
     "day, from Rung 1 of the ladder, not from memory. Still pending is fine, it "
     "stays pending; withdrawing and resending reads as pestering."),
    (14, "dm", "Review the DM: {company}",
     "If the DM is unanswered, do NOT nudge on LinkedIn. Touch 2 by email is the "
     "next move and it is already dated below. One channel at a time after touch 1."),
    (18, "touch2", "{company}: touch 2 to the same name",
     "Second and last email to this person. It must carry something the first "
     "did not: a change on their board, a timing consequence, a number with a "
     "source. 'Just following up' burns the touch and buys nothing."),
    (39, "route", "{company}: route to a second name, or park",
     "Two touches are spent on this person. Go to a different name at the "
     "company, openly ('if this sits better with X, tell me and I will keep it "
     "with her'), or park with a testable reopen condition. Never a third email "
     "to the same inbox."),
    (60, "park_review", "{company}: park review",
     "Only if it parked. Re-read the park's OWN reopen condition against this "
     "week and say whether it is met. Parks were created weekly and reviewed by "
     "nothing, which nearly cost the best lead of the month."),
]


def business_days_after(d, n):
    """Calendar days for the long gaps, business days for the short ones. A
    bounce check that lands on a Sunday is a bounce check nobody runs."""
    out = d
    while n > 0:
        out += datetime.timedelta(days=1)
        if out.weekday() < 5:
            n -= 1
    return out


def ladder(sent, channel="both", dm_sent=False):
    """channel: email, linkedin or both. dm_sent: whether an actual DM went out.

    At touch 1 only a connect REQUEST goes out, so there is no DM to review
    until they accept. The +14 DM row used to appear on every both-channel
    ladder, which put a task on the list for a message that did not exist.
    It appears when a DM was actually sent, and the connect check at +3 is what
    creates it later if they accept.
    """
    rows = []
    for offset, key, subject, body in STEPS:
        if key == "connect" and channel == "email":
            continue
        if key == "dm" and (channel == "email" or not dm_sent):
            continue
        due = (business_days_after(sent, offset) if offset <= 3
               else sent + datetime.timedelta(days=offset))
        rows.append({"offset_days": offset, "key": key, "due": due.isoformat(),
                     "subject": subject, "body": body})
    return rows


def check(proposed, sent):
    """Is a hand-written follow-up date sane? Catches the two real mistakes:
    inside the seven-day floor, and so far out the account has gone cold."""
    gap = (proposed - sent).days
    if gap < 7:
        return False, (f"{gap} days after the send. The floor is seven days "
                       f"between touches on one person, warmth included. The "
                       f"Optiml account got five emails in eight days and the "
                       f"answer was no.")
    if gap > 28:
        return False, (f"{gap} days after the send. Past about four weeks the "
                       f"thread is cold and touch 2 reads as a new cold email "
                       f"rather than a follow-up.")
    return True, f"{gap} days after the send, inside the 2 to 3 week window."


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a.split("=")[0]: (a.split("=")[1] if "=" in a else True)
             for a in sys.argv[1:] if a.startswith("--")}

    if "--check" in flags:
        if len(args) < 2:
            sys.exit("usage: followup_ladder.py --check <proposed> <sent>")
        ok, why = check(datetime.date.fromisoformat(args[0]),
                        datetime.date.fromisoformat(args[1]))
        print(("OK    " if ok else "BLOCK ") + why)
        return 0 if ok else 1

    if not args:
        sent = datetime.date.today()
    else:
        sent = datetime.date.fromisoformat(args[0])

    def val(name, default=""):
        v = flags.get("--" + name, default)
        return default if v is True else v

    company = val("company", "[company]")
    contact = val("contact", "")
    variant = val("variant", "?")
    channel = val("channel", "both")

    rows = ladder(sent, channel, dm_sent=bool(flags.get("--dm-sent")))
    print(f"Send date {sent} | variant {variant} | channel {channel}\n")
    for r in rows:
        print(f"  {r['due']}  (+{r['offset_days']:>2}d)  {r['subject'].format(company=company)}")

    if flags.get("--json"):
        print("\n" + json.dumps(
            [{**r, "subject": r["subject"].format(company=company),
              "body": r["body"].format(company=company, sent=sent),
              "contact_id": contact} for r in rows], indent=2))
    else:
        print("\n--- task bodies, ready to paste ---")
        for r in rows:
            print(f"\n[{r['due']}] {r['subject'].format(company=company)}")
            print("  " + r["body"].format(company=company, sent=sent))
        print(f"\nEvery one of these is created the moment the send is confirmed, "
              f"not later.\nAn account whose send FAILED still gets the bounce "
              f"row and the route row: the\naccounts most likely to be forgotten "
              f"are exactly the ones a success-only rule\nleaves out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
