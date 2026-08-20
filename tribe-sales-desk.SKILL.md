---
name: tribe-sales-desk
description: >-
  Run Jacopo's sales desk: the daily reconciliation, the follow-up cadence, deal
  hygiene, and the weekly sweep that stops accounts going quiet unnoticed. Use this
  whenever he asks what is due, what he owes people, what he has forgotten, or wants
  HubSpot to reflect reality. Trigger on "what's due today", "check HubSpot", "prep my
  day", "what do I need to follow up", "clean up HubSpot", "pipeline review", "am I
  missing anything", "what's the state of play", "someone replied, what now", or any
  Monday-morning-style question about where things stand. This is the discipline half
  of the sales workflow. The writing half is tribe-outbound-sequence, and the
  prospect-finding half is linkedin-engagement-radar. Use this one before either,
  because it decides what deserves the effort.
---

# Tribe sales desk

The job: make sure nothing live goes quiet, nothing dead gets chased, and the CRM says what actually happened.

Writing a good cold email is the easy part. What loses deals is a warm reply sitting unanswered for three weeks while five finished tasks sit on the list marked due. Both of those happened in the first two weeks of August 2026, and both were invisible from inside HubSpot.

## The core problem this skill exists to solve

**HubSpot tracks what you planned to do. It does not track what happened.**

Three specific failures follow from that, and all three have been observed on this portal:

1. **A sent email does not close its task.** The BCC logs the send as an activity on the contact. The task stays `NOT_STARTED` until a human clicks Complete, and nobody clicks Complete, because the moment the email goes out the work feels done. On 4 August, five of the six tasks showing as due had already been sent on 28 and 29 July. Working that list top to bottom would have sent five people the same email twice.

2. **A reply creates nothing.** No task, no flag, no stage change. A live conversation with a price on the table can go silent and the CRM will look identical to an account nobody has ever touched. This is the expensive one.

3. **A closed deal leaves its tasks behind.** Optiml was marked closed lost on 7 August. Four days later the task on it still read "chase Magdalena on the interview slot, or go to the CEO".

Every routine below is built to catch one of these.

## The daily run

Fifteen minutes. Do it in this order, because each step changes what the next one should contain.

### 1. Reconcile the task list against Sent mail

Pull every open task due today or earlier. For each one, search Sent for the recipient.

If the email already went out: **close the task**, and rewrite the body to say what was sent, when, and whether a reply came. Do not draft it again.

**Never trust the message list `search_threads` returns.** It gives back a thread's messages and that list can be stale. On 4 August a thread matched a filter of `after:2026/08/02`, so the index knew a message existed in that window, yet the messages array stopped at 31 July and omitted the 3 August reply entirely. Acting on that produced a confident, twice-repeated, wrong claim that nothing had been sent. The same truncation appeared again on 11 August on the Optiml thread, hiding five messages including the prospect's no.

So: use `search_threads` to find candidate thread IDs, then call **`get_thread`** on each before concluding anything. If the output is too large, dump it and pull dates with `jq`. Never tell him an email was not sent on the strength of a search alone.

### 1b. Bounce check, named and daily

Search `from:mailer-daemon` since the last run, every day, no exceptions. Stricter rule for manually-sourced addresses (anything a human typed rather than an enrichment tool verifying it "valid"): they get checked the NEXT MORNING after the send, and the send task is not truly settled until that check passes. A bounce found late means a follow-up scheduled against an address that never worked.

### 1c. Tracking health check

One query against HubSpot's logged emails (the EMAIL engagement object) for the most recent sends: do they carry a tracker key? If the latest sends have none, the Track box in the Gmail extension has lapsed (signed out, unticked, or sent outside desktop Chrome) and the morning report says "Track box lapsed, opens are not being recorded" the same day. The BCC keeps logging regardless, so this is about open data, not CRM history. Found the hard way on 20 August 2026: six sends went out untracked and nobody knew until the day was over.

### 1d. The warming queue

Ask every morning: who in the warming queue is ready today? Open tasks with subject "WARMING:" whose outreach-ready date has arrived become today's warm sends, variant W per the Lead Engine in tribe-outbound-sequence, counted inside the same 2-outbound-tasks-per-day cap, and warm beats cold when both compete for a slot (warmth expires, cold leads keep). A WARMING task past 10 days without its send is flagged: the window closed, the lead falls back to the cold lane.

### 2. Find replies with no task behind them

Search the inbox for replies from prospects, then check whether each one has an open task. Anything with a reply and no task is the top of today's list, ahead of every cold email.

Check open deals the same way. A deal in a live stage whose `notes_last_contacted` is more than 14 days old, or whose `closedate` is in the past, is the same failure wearing a different hat.

### 3. Read the drafts before writing new ones

If a task body carries a draft written days ago, re-check the fact it opens on. Job boards move. An email that opens "your Testing Architect has been open 40 days" is worse than useless if the role came off the board yesterday.

The Ashby public API is the fastest check: `https://api.ashbyhq.com/posting-api/job-board/<slug>` returns every live job with `title`, `location` and `publishedAt`. Days open is `today - publishedAt`, and that number has opened every email that got a reply this month.

### 4. Then draft what is genuinely left

Report in this order: what was already done, what is newly live, what still needs writing. He should see the reconciliation before the drafts.

## When someone replies

The reply is worth more than the next ten cold emails. Treat it that way.

**Same day, always.** A reply answered within the hour reads completely differently from one answered on Thursday.

**Create the task before writing the answer**, not after. The reply itself creates nothing in HubSpot, so if the answer gets interrupted there is no trace that anyone is mid-conversation.

**Set the deal stage to match what was actually said**, not what you hope. "Send me the agreement" is not the same as "we are interested".

Then, by reply type:

| They said | Do |
|---|---|
| A question | Answer it and nothing else. Do not attach a pitch to an answer. |
| "Send me X" | Send X the same day. If X is a document that does not exist yet, say when it will land and put a task on that date. |
| "Not now" | Ask what would change it, then set a dated task for that moment. A "not now" with a real date on it is a live account. |
| "No" | Ask what tipped it, in one line, with no pitch attached. Close the deal lost, close every open task on the account, and write the reason into the task body. |
| Silence after warmth | This is the dangerous one. See the cadence rules below. |

## Follow-up cadence

The single worst pattern in this pipeline is chasing a warm prospect harder than a cold one, because the warmth makes it feel safe.

**Optiml, 30 July to 7 August.** Discovery call, one-pager, then follow-ups on 31 July, 3, 5 and 7 August. Five emails in eight days to someone who had been replying inside twenty minutes. Her answer on 7 August was no. The service agreement she would have signed was never actually attached in any of those five.

The rules that come out of that:

**Minimum seven days between touches on the same person.** No exceptions for warmth. Someone replying quickly is not asking to be chased faster.

**Every follow-up must carry something the last one did not.** A timing consequence, a number with a source, a change on their job board, a piece of news. "Just following up" and "last follow up I promise" both burn a touch and buy nothing.

**Two emails per person, then switch.** The third touch goes to a different name at the same company, not a third attempt at the same inbox. Route it openly: "if this sits better with X, tell me and I will keep it with her" gets replies from people who would otherwise ignore it.

**Two emails per company, then stop.** After a People lead and a founder have both had their touches with no reply, the account is cold. Park it with a dated reopen condition rather than a third name.

**Never send an ask without the thing.** If the email asks them to sign, agree, or decide, the document has to be attached to that same email. Asking someone to move forward on something they have not seen is how a live deal dies quietly.

**Track what you promised.** If a follow-up said "I will write once and then leave you alone", do not schedule a third. Put a routing check instead.

**Standard spacing that works here (updated 20 Aug 2026):** first email, follow-up 2 to 3 weeks later (3 over summer or quiet periods), then 2 to 3 weeks after the second touch comes the route to a second name or the park with a dated reopen condition, never a third email to the same inbox. Closing any send task and creating its successor happen in the same motion; the full ladder lives in tribe-outbound-sequence under "The follow-up lifecycle". A follow-up task is only marked complete when the send is confirmed in Sent and the body carries what actually went out; a reply at any point voids the pending task, close it with the outcome and switch to the reply playbook above.

## Task hygiene

**Every send becomes a closed task with what actually went out.** Subject line, angle used, date, time, whether the address is now verified. Six weeks later that body is the only record of why the account went the way it did.

**Every closed task names what happens next**, by task ID and date. Opening a closed task should tell you where the account went, not leave you hunting.

**Two tasks per day, maximum.** Nine tasks on one morning get bulk-snoozed, and a snoozed task is worse than no task because it looks handled.

**Set `hs_lead_status` to `ATTEMPTED_TO_CONTACT`** on everyone emailed, at the moment of sending.

## Deal hygiene

**Create the deal when they engage, not when they sign.** Cold outreach with no deal record means the pipeline number is invented. As of 11 August 2026 there were 3 deals on this portal, 2 already closed, against 11 open outbound tasks. The pipeline was not empty, it was unrecorded.

**A close date in the past on a live-stage deal is an alarm, not a detail.** It means either the deal moved and nobody said so, or it stalled and nobody noticed.

**When a deal closes, close its tasks in the same motion.** Both directions: closing the deal without closing the tasks leaves ghosts, and closing tasks without moving the deal leaves a phantom number in the forecast.

## The merge queue

HubSpot merges and deletions are UI-only, so ghosts and duplicates accumulate. They are NOT to be scattered across task bodies: one standing HubSpot task titled "UI merge queue" holds the complete list, updated IN PLACE the moment a new ghost or duplicate appears (each line: what to merge into what, IDs, which record wins, and why). Jacopo clears it in one sitting when he has ten minutes; whoever updates it removes lines that were done. If the task does not exist, create it, due date far in the future, never marked complete, only rewritten.

## The weekly sweep

Friday, or Monday before anything else. Seven checks:

1. **Live deals with no activity in 14 days.** Each one gets an action or a stage change. Neither is optional.
2. **Deals whose close date has passed.** Move it or close it.
3. **Open tasks more than 5 days overdue.** Either it is not real work, or it is a decision he has been avoiding. Name which.
4. **The overdue tripwire: any task more than 14 days overdue gets named in the report as dead-or-real, and decided.** Not snoozed, not carried, decided: closed as dead with one line of why, or given a real date this week. This rule exists because a pile of 40 overdue LinkedIn follow-up tasks accumulated between May and August 2026 with nothing forcing the question.
5. **Contacts with a send but no email on the record.** Every one is a duplicate waiting to happen. See the blank-email rule in tribe-outbound-sequence.
6. **Accounts owned by another Tribester that appear in his list.** Park them and say whose they are.
7. **The A/B scoreboard** (per tribe-outbound-sequence): sends and replies per variant, one line, and the days remaining until the end-of-September call.

## What cannot be done, and should be said early

- **Sending email.** Neither HubSpot nor the Gmail connector can send. Drafts only, and a human clicks send.
- **Merging records.** Companies and contacts, UI only. Hand over record IDs and which to keep as primary.
- **Deleting records.** No delete tool. Rename junk records with a `ZZ DELETE` prefix and a date so they sort to the bottom.
- **Writing HubSpot notes.** Permission is off on this portal. Meetings, tasks, calls and deals all work.

Say each of these at the moment it becomes relevant, not after he has waited for it.

## Reporting

Give it in the chat, not as a file. He works from the thread.

Order: what is already done, what is newly live and needs him today, what is scheduled, then the decisions that are genuinely his. Flag what he cannot see from where he sits: an existing thread at the same company, a contact who changed jobs, an address that is a guess, a public objection, a colleague already in the account.

Be specific about uncertainty. "Address unverified" on every guessed address, every time, beats one general disclaimer at the end.
