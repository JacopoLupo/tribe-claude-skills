#!/usr/bin/env python3
"""Eval harness for the preflight gate.

Runs one fixed set of realistic cases against whichever preflight.py it is
pointed at, so the same cases can score the build before a change and the
build after it.

    python3 eval_gate.py /path/to/preflight.py

The cases exist because the shipped selftest is eleven FIRST TOUCHES. The
follow-up lane, which is where 58 of the desk's scheduled tasks live, was
never exercised at all.
"""
import datetime, importlib.util, json, sys

def load(path):
    spec = importlib.util.spec_from_file_location("pf", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def build(pf):
    T = pf.TODAY
    note = ("I sent you an email earlier, this is the second door. Building it "
            "in Paris instead of the city where the logos are is a contrarian "
            "choice and I like it. Would be glad to connect and follow how it "
            "goes.")
    base = {
        "company": "Testco",
        "screen": {"company_owner_id": "33687989",
                   "contact_lead_statuses": ["NEW"],
                   "this_contact_status": "NEW",
                   "touch_type": "first",
                   "agent_notes_count": 0, "last_touch_date": None,
                   "parked": False, "touches_spent": 0},
        "board": {"non_eu_fraction": 0.1, "scan_date": str(T)},
        "email": {"variant": "A", "to": "a@b.com", "address_verified": True,
                  "bcc": pf.BCC, "subject": "x",
                  "body": pf.RED_LINE + "\n" + ("word " * 80),
                  "legal_basis": pf.LEGAL_BASIS},
        "connect_note": note,
        "followup": {"due": str(T + datetime.timedelta(days=18)),
                     "what": "what the next touch carries that this one did not"}}

    def mk(**screen):
        L = json.loads(json.dumps(base))
        L["screen"].update(screen)
        return L

    eight = str(T - datetime.timedelta(days=8))
    three = str(T - datetime.timedelta(days=3))
    FU = dict(touch_type="followup", this_contact_status="ATTEMPTED_TO_CONTACT",
              contact_lead_statuses=["ATTEMPTED_TO_CONTACT"])

    cases = [
        # the follow-up lane, which is what Jacopo asked for on 25 Aug
        ("followup 1 of 3, a week after the send", mk(**FU, touches_spent=1,
         last_touch_date=eight), False),
        ("followup 2 of 3", mk(**FU, touches_spent=2, last_touch_date=eight), False),
        ("followup 3 of 3", mk(**FU, touches_spent=3, last_touch_date=eight), False),
        ("a fifth email to the same inbox", mk(**FU, touches_spent=4,
         last_touch_date=eight), True),
        ("followup inside the seven day floor", mk(**FU, touches_spent=1,
         last_touch_date=three), True),
        ("followup on a name never actually emailed", mk(
            touch_type="followup", this_contact_status="NEW",
            contact_lead_statuses=["NEW"], touches_spent=1,
            last_touch_date=eight), True),
        ("another agent's notes block a followup too", mk(**FU, touches_spent=1,
         last_touch_date=eight, agent_notes_count=318), True),

        # routing to a second name, which the skill mandates at +39
        ("route to a fresh second name at a worked account", mk(
            touch_type="second_name", this_contact_status="NEW",
            contact_lead_statuses=["ATTEMPTED_TO_CONTACT", "NEW"],
            touches_spent=0, last_touch_date=None), False),
        ("second name who was himself already worked", mk(
            touch_type="second_name",
            this_contact_status="ATTEMPTED_TO_CONTACT",
            contact_lead_statuses=["ATTEMPTED_TO_CONTACT"],
            touches_spent=0, last_touch_date=None), True),

        # first touches, regression: these must keep behaving
        ("first touch, clean account", mk(), False),
        ("first touch where a contact is already worked (amber)", mk(
            contact_lead_statuses=["ATTEMPTED_TO_CONTACT"]), True),
        ("first touch on a name with touches already spent", mk(
            touches_spent=2), True),
        ("first touch, another agent on the account (upvest)", mk(
            agent_notes_count=318), True),
    ]
    return cases

def main():
    pf = load(sys.argv[1])
    cases = build(pf)
    rows, passed = [], 0
    for label, lead, should_block in cases:
        bag = pf.run({"leads": [lead], "sends_already_scheduled": 0})
        blocked = any(s == "BLOCK" for s, _, _ in bag)
        ok = blocked == should_block
        passed += ok
        why = "; ".join(m for s, _, m in bag if s == "BLOCK")[:150]
        rows.append({"case": label, "expected": "block" if should_block else "pass",
                     "got": "block" if blocked else "pass", "ok": ok, "why": why})
        print(f"  {'pass' if ok else 'FAIL'}  {label}")
        if not ok and why:
            print(f"          gate said: {why}")
    print(f"\n  {passed}/{len(cases)} = {100*passed//len(cases)}%")
    json.dump({"passed": passed, "total": len(cases), "rows": rows},
              open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout, indent=2)
    return 0 if passed == len(cases) else 1

sys.exit(main())
