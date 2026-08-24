# The operator's manual

Everything here is a phrase you type to Claude in a Cowork session, and what happens when you do. No coding, no setup beyond the checklist.

---

## One-time setup

| Connector | What it powers |
|---|---|
| **Gmail** | Draft creation, Sent-folder reconciliation, bounce checks |
| **HubSpot** | Contacts, companies, tasks, activity logging, the A/B scoreboard |
| **Google Calendar** | Meeting detection, because a booked call changes the play |
| **Vibe Prospecting** | Verified email addresses (~2 credits each) |
| **Claude in Chrome** | LinkedIn reading, boards with no ATS API, GitHub |

Two Gmail habits that make the whole thing work:

1. **The HubSpot BCC** goes on every outreach email: `146748263@bcc.eu1.hubspot.com`. Claude pre-sets it in every draft. It is what logs sends to the CRM automatically.
2. **The Track checkbox** (HubSpot Sales extension) must be ticked at send to record opens. The BCC logs the send; only Track records the open. Set "track by default" once and forget it.

**One HubSpot note:** the connection needs **notes write** scope, or LinkedIn activity cannot be logged where you'll find it.

---

## The golden rules

> **Claude never sends.** Every email is a draft until you press send.
>
> **No guessed addresses, ever.** Addresses get verified, written onto the HubSpot contact, and only then into a draft. An unverified address means the To line stays empty and the draft says so in red.
>
> **Every lead gets both channels.** Email and LinkedIn connect note, same day, always. A prep that gives you only an email is not finished.

---

## Daily driving

### Start the day

> **"prep my day"** · **"what's due today"**

Reconciles open tasks against the Sent folder so you never email someone twice, checks yesterday's bounces, checks tracking health, surfaces replies with no task behind them, and reports what is done, what needs you, what is scheduled.

### Find leads

> **"run the lead engine"** · **"fresh leads"** · **"harvest"**

Runs `funding_radar.py` across the funding press and probes every ATS for live boards, then cross-checks the index velocity diff for companies whose board jumped since the last scan. Everything is deduped against HubSpot and colleague-owned accounts are parked before you see the list.

What survives the screen: EU-based, money in the bank, roles opening fast, and nobody internal running the hiring.

### Turn leads into outreach

> **"prep the emails"** · **"add them to HubSpot and draft the outreach"**

Per target: company and contact created (duplicate-checked), address enriched and verified, email drafted in Gmail with BCC pre-set, **LinkedIn connect note written alongside it**, and a dated HubSpot task carrying the whole plan. Cold variants alternate A and B automatically.

### The commenting workflow (warm lane)

Tell Claude who you commented on:

> **"I commented on [name]'s post about [topic]"**

A WARMING task goes on that contact the same day. The window is **fresh only**: outreach goes within 72 hours, same day if they engaged back. Past 5 days the warmth is spent and the lead drops to the cold lane.

Warm leads get **variant W**, which opens from the exchange. Variant W needs your explicit go each time, and it stays out of the A/B scoreboard because warm replies would corrupt the cold test.

### After you send

> **"I sent them"** · **"check the sent folder and log everything"**

Claude verifies each send in the Sent folder, never trusting the plan or the report, closes each task with what actually went out, and creates the follow-up 2 to 3 weeks ahead in the same motion. It will tell you plainly if something you thought went out didn't.

### When someone replies

> **"someone replied"** · or just paste it

Same-day response is the standard. A reply creates nothing in HubSpot by itself, so the task comes first, then the answer, drafted by reply type: a question gets an answer with no pitch attached, "send me X" gets X the same day, "not now" gets a dated reopen, "no" gets a one-line ask about what tipped it and a clean close.

### Refresh the market data

> **"run the index"**

41 boards, ~1,600 roles, medians by category, percentile table, stuck recruiter roles, TA pressure, and the velocity diff against the last scan.

### Weekly

> **"run the weekly sweep"** · **"pipeline review"**

Seven checks: stale deals, past-due close dates, overdue tasks, the 14-day dead-or-real tripwire, contacts missing emails, colleague-owned accounts in the list, and the A/B scoreboard with days remaining.

---

## Running automatically

**LinkedIn to HubSpot sync**, weekday mornings. Reads your sent-invitations list and inbox, works out who accepted and who replied since yesterday, and writes it into HubSpot as notes. On a reply it logs the text, flips lead status, closes that account's email follow-up as superseded, and raises a same-day "answer today" task.

It exists because a LinkedIn reply reaches no inbox and no CRM. Without it, the most valuable signal in the pipeline is the one most likely to be missed.

---

## The ladder

**Touch 1** → **touch 2** two to three weeks later carrying something new, usually the index cut for their segment → then **not a third email**. Route to a second name at the company, openly, or park with a dated reopen condition.

Two people maximum per company. A reply at any rung voids the ladder and switches to the reply playbook.

**Parks carry an expiry.** Every park names what would reopen it, in testable terms, and gets re-checked on a date. A park that was right in August can be badly wrong by September.

---

## The A/B test

Live until end of September 2026.

| | Opens with |
|---|---|
| **Variant A**, the index email | Their stuck role against the market median |
| **Variant B**, the candor email | An AI test that doesn't mention Tribe, then the pivot |

Half of each batch gets each variant, every send tagged in its HubSpot task, metric is replies within 14 days. **Do not edit either variant mid-test.** An edit restarts that variant's count.

---

## What Claude refuses to do, on purpose

Send an email. Put a guessed address in a To field. Email an account a colleague owns. Send a third email to the same person. Quote an index number that wasn't computed that week. Invent the specifics of a past search.

Each of these exists because the mistake was made once, by hand, and cost something.

---

## When something looks wrong

Every decision is logged into HubSpot task bodies, dated. Open any closed task and it tells you what was sent, when, and which task succeeded it.

If the story and the CRM disagree, **trust the Sent folder**. The reconciliation rules exist precisely because plans lie and outboxes don't.
