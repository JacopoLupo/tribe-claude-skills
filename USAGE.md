# How to use the Tribe sales skills

This is the operator's manual. Everything here is a phrase you type to Claude in a Cowork session, and what happens when you do. No coding, no setup beyond the checklist below.

## One-time setup

Connect these in your Claude session (the skills degrade gracefully without them, but this is the full machine):

| Connector | What it powers |
|---|---|
| Gmail | Draft creation, Sent-folder reconciliation, bounce checks |
| HubSpot | Contacts, companies, tasks, send logging, the A/B scoreboard |
| Google Calendar | Meeting detection (a booked call changes the play) |
| Vibe Prospecting | Verified email addresses from LinkedIn profiles (~2 credits per email) |
| Claude in Chrome (optional) | Anything that needs your logged-in browser |

Two Gmail-side habits that make the whole system work:

1. **The HubSpot BCC** goes on every outreach email: `146748263@bcc.eu1.hubspot.com`. Claude pre-sets it in every draft. It is what logs sends to the CRM automatically.
2. **The Track checkbox** (HubSpot Sales extension in Gmail) must be ticked at send to record opens. The BCC logs the send; only Track records opens. Set "track by default" once in the extension settings and forget it.

## The golden rule

**Claude never sends.** Every email is a draft until a human presses Send. Claude also never guesses an email address into a To field: addresses get verified first (enrichment tool or a two-source pattern match), written onto the HubSpot contact, and only then into the draft.

## Daily driving: what to say

### Start the day

> "prep my day" or "what's due today"

Runs the sales-desk routine: reconciles open tasks against the Sent folder (so you never email someone twice), checks bounces from yesterday, checks email tracking health, surfaces replies that have no task behind them (the most expensive thing to miss), and reports: what is done, what needs you today, what is scheduled.

### Find new prospects

> "find new leads" or "deep search for recent funding rounds"

Claude hunts (funding announcements, job board scans), then for each candidate: checks HubSpot for existing records, duplicates, and accounts a colleague already owns (those get parked, always), scans the prospect's live job board, and reports which ones deserve an email.

### Turn prospects into drafts

> "prep the emails for these" or "add them to HubSpot and draft the outreach"

For each target: company and contact created in HubSpot (duplicate-checked), email address enriched and verified, draft written in Gmail with BCC pre-set, and a dated HubSpot task carrying the full plan, address status, variant tag, pre-send checklist. Drafts alternate between the two A/B variants automatically.

### After you hit send

> "I sent the emails, update the tasks" or "check the sent folder and log everything"

Claude verifies each send in the Sent folder (never trusts a plan), closes the task with what actually went out, subject, address, date, edits you made, sets the contact's lead status, and creates the follow-up task 2 to 3 weeks out in the same motion. This close-and-schedule pairing is the rule that stops accounts going silent.

### When someone replies

> "someone replied, what now" or just paste the reply

Same-day response is the standard. Claude creates the task first (a reply creates nothing in HubSpot by itself), then helps draft the answer by reply type: a question gets an answer with no pitch attached, "send me X" gets X the same day, "not now" gets a dated reopen, "no" gets a one-line ask about what tipped it and a clean close.

### Refresh the market data

> "run the index" or "re-run the board scan"

Executes `index.py`: 41 boards, ~1,600 roles, medians by category, the percentile table, and the list of stuck TA roles. Every number in every email comes from a scan run that week, never from memory. `python3 index.py monumental` also dumps one company's full board; `--probe 127` gives the percentile for a specific role age.

### Weekly, Friday or Monday

> "run the weekly sweep" or "pipeline review"

Seven checks: stale deals, past-due close dates, overdue tasks, the 14-day dead-or-real tripwire, contacts missing emails, colleague-owned accounts in the list, and the A/B scoreboard with days remaining until the verdict.

## The follow-up ladder (what the system enforces)

First email → follow-up 2 to 3 weeks later carrying something new (usually the index cut for their segment) → 2 to 3 weeks after that, NOT a third email to the same inbox: route to a second name at the company, openly, or park with a dated reopen condition. Two people maximum per company, then the account is cold until something changes. A reply at any rung voids the ladder and switches to the reply playbook.

## The A/B test (live until end of September 2026)

Variant A, "the index email": opens with the prospect's stuck role against the market median from the Board Index. Variant B, "the candor email": opens with an AI test that doesn't mention Tribe, then the pivot. Half of each batch gets each variant, every send is tagged in its HubSpot task, the metric is replies within 14 days. Do not edit either variant mid-test; an edit restarts that variant's count.

## Things Claude will refuse to do, on purpose

Send an email. Put a guessed address in a To field. Email an account a colleague owns. Send a third email to the same person. Quote an index number that wasn't computed that week. Invent the specifics of a past search. Each of these exists because the mistake was made once, manually, and cost something.

## When something looks wrong

The skills log every decision into HubSpot task bodies, dated. Open any closed task and it tells you what was sent, when, and which task succeeded it. If the story and the CRM disagree, trust the Sent folder, and tell Claude, the reconciliation rules exist precisely because plans lie and outboxes don't.
