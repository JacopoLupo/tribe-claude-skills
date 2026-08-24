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

**And never trust Jacopo's own report of what he sent either (rule earned 24 Aug 2026).** He said "I did everything apart from Zoe" and the Sent folder showed five of six: the Satispay follow-up had never left the drafts folder. He is not careless, sending six things across two channels in one sitting is simply easy to lose count of. So the reconciliation ALWAYS reads the Sent folder against the plan, item by item, and reports the gap plainly. That same check caught two other things the same morning: an address he had filled himself that did not match the pattern on file (kutylowski@deepl.com, so DeepL is lastname@, not firstname.lastname), and a send to an account owned by a colleague that was deliberate and fine (Filics, Kris's account, his email named her explicitly). None of those would have surfaced from asking him.

### 1b. Bounce check, named and daily

Search `from:mailer-daemon` since the last run, every day, no exceptions. Stricter rule for manually-sourced addresses (anything a human typed rather than an enrichment tool verifying it "valid"): they get checked the NEXT MORNING after the send, and the send task is not truly settled until that check passes. A bounce found late means a follow-up scheduled against an address that never worked.

### 1c. Tracking health check, now a hard gate

**This is no longer a nice-to-have (24 Aug 2026).** The Track box lapsed across the entire August cohort, which is exactly why thirty-plus sends producing zero replies was unreadable: three failure points (delivered, opened, replied) collapsed into one number that could not be diagnosed. Domain auth was checked and is clean, so the silence was never deliverability.

Every morning, check the previous day's sends for tracker keys on the EMAIL engagement objects. **A send with no tracker key is EXCLUDED from the A/B test rather than counted**, and gets reported as excluded, because an untracked send is a data point that cannot be read. If a whole batch went out untracked, say so plainly and tell Jacopo to fix "track by default" in the HubSpot Sales extension before the next batch.

One query against HubSpot's logged emails (the EMAIL engagement object) for the most recent sends: do they carry a tracker key? If the latest sends have none, the Track box in the Gmail extension has lapsed (signed out, unticked, or sent outside desktop Chrome) and the morning report says "Track box lapsed, opens are not being recorded" the same day. The BCC keeps logging regardless, so this is about open data, not CRM history. Found the hard way on 20 August 2026: six sends went out untracked and nobody knew until the day was over.

### 1d. The warming queue

Ask every morning: who in the warming queue is ready today? Open tasks with subject "WARMING:" become today's warm sends inside a FRESH-ONLY window (Jacopo, 20 Aug): within 72 hours of the comment, same day or next day if the person replied or reacted. Variant W per the Lead Engine in tribe-outbound-sequence, counted inside the same 2-outbound-tasks-per-day cap, and warm ALWAYS beats cold for a slot because warmth expires and cold leads keep. A WARMING task past 5 days without its send is flagged: window closed, lead falls back to the cold lane.

### 1e. The LinkedIn scan, 10:00

Who accepted since yesterday, who replied. Runs on its own schedule but read the result as part of the day: every acceptance is a same-day DM, every reply is a same-day answer and beats every cold email on the list. Full rules under "The 10:00 scanner" below.

**Read the whole inbox, not only the prospect threads.** Every unanswered message gets an answer or an explicit decision the same day, including the ones that are not leads. On 24 Aug 2026 three were sitting unread, two of them for three days with LinkedIn itself prompting "Reply?" on them: a recruiter connecting, a candidate following up on an old conversation, and a former Nexi colleague asking whether Tribe had work for her. None were sales leads and all three were reputational, and the last one was a delivery-capacity question that belonged with Kris or Salem. Non-leads get routed or answered in one line, never left. A desk that lets its inbox queue for three days cannot claim to be good at the conversation after first contact.

### 1f. The funding radar

Daily, not weekly: one sweep for EU funding rounds announced the previous day. A round announced yesterday is today's best cold lead and next week's worst one. Any hit goes through the Lead Engine (dedupe, Tribester check, board scan) the same morning.

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

**Task subjects are actions, in one fixed shape: `Company: what to do, who`.** "Satispay: send Emilia the draft, last touch before parking". Not "Satispay: NOT SENT YET, draft is waiting in Gmail", not "amber: touch 2, Philipp Reissel (VARIANT A sent 20 Aug)". No shouting, no status shoved in the title, no metadata trailing in brackets. Jacopo reads this list as a list of things to do, so it has to scan like one. Variant, address, dates and history all live in the body.

**Task bodies are short and structured, not narrative (Jacopo, 24 Aug 2026: "be brief and explain what we did and what to do next, not the entire story").** Three labelled lines, nothing else:
```
DONE: what has already happened.
NEXT: the exact next action, with the fact that decides it.
RULE: the constraint that must not be broken (ladder position, last touch, do not chase).
```
The temptation is to write everything down because future-Claude reads these. Resist it: a body nobody finishes is worse than three lines somebody acts on.

## Deal hygiene

**Create the deal when they engage, not when they sign.** Cold outreach with no deal record means the pipeline number is invented. As of 11 August 2026 there were 3 deals on this portal, 2 already closed, against 11 open outbound tasks. The pipeline was not empty, it was unrecorded.

**A close date in the past on a live-stage deal is an alarm, not a detail.** It means either the deal moved and nobody said so, or it stalled and nobody noticed.

**When a deal closes, close its tasks in the same motion.** Both directions: closing the deal without closing the tasks leaves ghosts, and closing tasks without moving the deal leaves a phantom number in the forecast.

## The merge queue

HubSpot merges and deletions are UI-only, so ghosts and duplicates accumulate. They are NOT to be scattered across task bodies: one standing HubSpot task titled "UI merge queue" holds the complete list, updated IN PLACE the moment a new ghost or duplicate appears (each line: what to merge into what, IDs, which record wins, and why). Jacopo clears it in one sitting when he has ten minutes; whoever updates it removes lines that were done. If the task does not exist, create it, due date far in the future, never marked complete, only rewritten.

## Logging LinkedIn in HubSpot

LinkedIn reaches HubSpot through nothing automatic, so every connect request and every DM has to be written in by hand or it never existed.

**Use NOTES, associated to the contact.** `objectType: "notes"`, with `hs_note_body` and `hs_timestamp` set to when it actually happened. Notes land on the contact's Activity feed, which is where Jacopo looks. Do NOT use tasks for this: on 24 Aug 2026 ten LinkedIn touches were logged as completed tasks, they were attached correctly and he still could not find them, because completed tasks sit on the Tasks tab and not the activity timeline. All ten had to be redone as notes and the task versions renamed ZZ DELETE.

**Communications do not work on this connector.** `objectType: "communications"` with `hs_communication_channel_type: LINKEDIN_MESSAGE` is HubSpot's own native object for exactly this, and it returns "Requested object type is not supported". That is a server limitation, not a permissions one, and re-authorising does not fix it (tested 24 Aug 2026, before and after a reconnect). Notes write fine once the connection carries notes scope. Try communications first anyway on any future run, in case it starts working, then fall back to notes.

**What each note says:** what was sent (the full text, because the exact wording is what gets reused), the date, the current status (pending, accepted, replied), and the profile URL. For an accepted connect, say when it was accepted and whether they wrote anything.

## The 10:00 scanner, and why an acceptance is the whole point

**Scheduled task `trig_01HJEYEZvfTx6EBWtB4uCdVj`, weekdays 10:00 Prague, `requires_local_device`.** It reads the sent-invitations list and the LinkedIn inbox through Jacopo's Chrome, works out who accepted and who replied since the last run, and writes the notes itself. It checks for existing entries first so it never duplicates.

It runs at 10:00 rather than 08:00 for one reason: acceptances cluster in the two or three hours after the morning batch goes out, so an 08:00 scan reads a list that has not moved yet. Both acceptances on 24 August landed inside four hours of the send.

**An acceptance is the opening of a conversation, not an admin event.** This is the rule the whole scanner exists to serve. The failure it prevents is the quiet one: a connect gets accepted, the scanner logs it neatly, lead status moves to CONNECTED, and nothing is ever said to the person. The accept was the reply, and it went unanswered.

So when the scan finds an acceptance, the DM goes out the same day. If a message was queued when the connect was written, send that. **If none was queued, write one on the spot rather than deferring it**, because the acceptance decays like any other warm signal.

The message has four properties and no others:

1. **Thank them in half a sentence.** Not a paragraph, not gratitude with a subordinate clause hanging off it.
2. **Do not repeat the email.** They have it. Repeating the hook tells them both channels are the same automation wearing two coats, which is exactly what the double-channel play is trying not to be.
3. **One new observation, specific to them, computed that day.** Re-scan the board before writing. On 24 August that meant Sereact opening in four countries at once with three roles posted that morning, and Dash0 posting sixteen Solutions Engineer reqs on a single day while an Amsterdam AE sat at 350 days. Neither number was in either email.
4. **Close with one real question.** Not "would you be open to a chat". A question about their operation that a founder would answer for free, because answering it is more interesting than ignoring it.

Then log it: a note carrying the full DM text and the facts behind it, and a LinkedIn review task about two weeks out.

**On a reply**, the job logs the text, sets lead status to CONNECTED, closes that account's email follow-up as superseded, and raises a same-day "REPLIED, answer today" task. A LinkedIn reply reaches no inbox and no CRM, so without this the most valuable signal in the pipeline is also the one most likely to be missed.

**Acceptance rate is now a tracked number.** Through 24 August 2026 it is 4 of 10 on the double-channel batches (Michael Blicher Soerensen, Fabian Riedel, Ralf Gulde, Mirko Novakovic), against zero replies from roughly thirty-five emails sent alone. Whatever else that says, it says the connect note is currently outperforming the email by an enormous margin, and the acceptances are the conversations worth spending the day on.

## Follow-ups exist for BOTH channels

A sent email always gets a dated touch 2. So must a sent LinkedIn message, and the reason is asymmetric: an unanswered email still sits in a thread Jacopo can see, while an unanswered DM leaves no trace anywhere at all. Without a task it is simply forgotten while the email ladder runs on regardless.

Two LinkedIn tasks, both dated about two weeks out:

1. **Review the DMs sent.** If still silent, do NOT nudge on LinkedIn. The email touch 2 is the next move. One channel at a time, never both at once.
2. **Decide on connects never accepted.** An invite ignored for two weeks is an answer. Leave it pending, do not withdraw and re-send, that reads as pestering, and let the email ladder carry the account. The exception is anyone where LinkedIn is the ONLY route in (no verified address): there, a dead invite means the account needs an address or it parks, and that has to be decided rather than left to drift.

## Publish the index, every Monday

The highest-leverage thing on this desk is not another email. It is that **nobody else in European recruiting has the index**, and until 24 Aug 2026 it existed only as a private script used to write cold emails to twenty people at a time.

Every Monday, run `scripts/index_post.py`. It produces a paste-ready LinkedIn post from that morning's scan: role count, boards, medians by function with week-over-week movement, the >90 and >300 day counts, and the line that does the work ("recruiting roles themselves take 36 days to fill, so the companies that most need to hire are the slowest at hiring the people who do the hiring").

**Why this matters more than the outbound.** Outbound is linear: one email, one prospect, one chance. The index compounds. Founders who delete a cold email will still read a benchmark about their own market, and once they have seen it, "I track 41 boards" stops being a claim in an email and becomes something they recognise. It is also the only part of this system a competitor cannot copy without building the scanner first.

**Anyone who comments or DMs about the index is an inbound lead and gets handled as one:** check them against HubSpot before replying, and if they are clean, the reply IS the outreach. No cold email, no variant, no ladder. Someone who asked for the cut has already opted in, so send it, and follow up on the conversation rather than on a schedule.

The script prints an operator note under the post with the fastest-moving board and the oldest role in the index. Those are the week's two best cold-lead tips, free, as a side effect of publishing.

## The funnel scoreboard

**One reply-rate number was hiding four separate problems.** Through August the desk reported "35 sends, 0 replies", which is a single unreadable figure covering a chain of five conversions, each with its own failure mode and its own fix. From 24 Aug 2026 the report carries the whole chain, every stage as its own line with its own denominator:

```
connects sent      ->  accepted        (10 -> 4, 40%)
accepted           ->  message sent    (4 -> 4, all verified in thread)
message sent       ->  answered        (4 -> 0 so far, read on 7 Sep)
answered           ->  call booked
emails sent        ->  opened          (needs the Track box)
opened             ->  replied
```

**Two shapes are in the field at once and must be scored separately.** Michael Blicher Soerensen and Fabian Riedel got the old acceptance message (market median, offer of a data cut, a question, no pricing) on 24 Aug at 12:41. Ralf Gulde and Mirko Novakovic got the new one (their own board, then the commercial model, no ask) at 14:22 the same day. Same channel, same week, same sender, four threads. Report them as two rows, never as one, because collapsing them throws away the only controlled comparison this desk has.

**Read it as a diagnosis, not a report.** Acceptance at 40% says the connect note works and needs nothing. The next unknown is the DM answer rate, so that is the only stage worth optimising until it has a number. Email opens are still unmeasurable while the Track box is off, which is why that check is a hard gate and not a nicety.

**The rule this exists to enforce: fix the earliest broken stage, never the loudest one.** Rewriting emails when the real gap is that nobody answers the DMs is motion, not progress.

## The weekly sweep

Friday, or Monday before anything else. Seven checks:

1. **Live deals with no activity in 14 days.** Each one gets an action or a stage change. Neither is optional.
2. **Deals whose close date has passed.** Move it or close it.
3. **Open tasks more than 5 days overdue.** Either it is not real work, or it is a decision he has been avoiding. Name which.
4. **The overdue tripwire: any task more than 14 days overdue gets named in the report as dead-or-real, and decided.** Not snoozed, not carried, decided: closed as dead with one line of why, or given a real date this week. This rule exists because a pile of 40 overdue LinkedIn follow-up tasks accumulated between May and August 2026 with nothing forcing the question.
5. **Contacts with a send but no email on the record.** Every one is a duplicate waiting to happen. See the blank-email rule in tribe-outbound-sequence.
6. **Accounts owned by another Tribester that appear in his list.** Park them and say whose they are.
7. **The funnel scoreboard, five stages, not one number** (see below).

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
