---
name: tribe-outbound-sequence
description: >-
  Turn identified prospects into sent-ready cold outreach for Jacopo at Tribe. Use
  this whenever he has names or companies he wants to contact and needs the CRM side
  handled properly, meaning checking HubSpot for existing records and duplicates
  before creating anything, drafting the email in his voice, and creating dated
  HubSpot tasks that carry the full draft. Trigger on "write cold emails to these
  people", "let's contact them", "add these to HubSpot and draft outreach", "prep the
  outbound", "give me the emails and the actions", or any moment he moves from
  finding prospects to writing to them. This is the outbound half of the workflow
  whose front half is the linkedin-engagement-radar skill, so it is the natural next
  step after that skill produces a list. Also use it when he asks to follow up on
  people already contacted, or to multi-thread into an account that has gone quiet.
---

# Tribe outbound sequence

The job: take people Jacopo wants to contact and get him to the point where he opens a HubSpot task, reads a finished draft, and hits send. Nothing half-finished, nothing he has to reconstruct.

Most of the value here is not the writing. It is the checks that happen before the writing, because his CRM has 8,500+ companies, a history of bad imports, and duplicates that multiply every time someone sends an email to a contact whose email field is blank.

## THE PREFLIGHT GATE. Nothing reaches Jacopo until it exits 0

On 25 August 2026 the desk broke three written rules in one morning and Jacopo caught all three: a company was prepped for a send while a colleague's agent was working it, a second was prepped a day after its CEO had already been emailed, and three connect notes were improvised instead of written from the template. None of it was carelessness. Every one of those rules lived in prose with no moment where anything verified it, and a rule with no gate is a wish.

So: **`python3 scripts/preflight.py batch.json` runs before any batch is presented, and a batch that does not exit 0 is not presented.** Not summarised in chat, not shown "for now", not sent with a caveat. Fixed and re-run.

`python3 scripts/preflight.py --template` prints the file to fill in. One entry per lead, and every field is required, because absent is exactly how the two bad leads passed: nobody had looked, and nothing distinguished not-looked-at from looked-at-and-clean.

The gate has no HubSpot credentials and never will. It cannot run the screening queries; it refuses to pass a batch until their ANSWERS are present, which is what stops a query being skipped and quietly forgotten. Everything textual it checks outright: connect-note skeleton and character count, red reminder line, BCC, em-dashes, per-variant word counts and banned phrases, subject convention, variant rotation, board scan freshness, the EMEA location fraction.

**The four queries whose answers the gate demands.** Run them, paste the answers in, and if one of them is uncomfortable that is the gate doing its job.

1. **Contact-level prior contact**, which is the check that would have caught amber. `search_crm_objects(CONTACT, associatedWith company X, properties [hs_lead_status, notes_last_contacted, hubspot_owner_id])`. Anything at ATTEMPTED_TO_CONTACT, IN_PROGRESS, CONNECTED or OPEN_DEAL means the account is live. **The company record is not enough and never was:** amber's company record had a blank last-contacted while its CEO sat at ATTEMPTED_TO_CONTACT from the previous afternoon.
2. **Another agent's notes**, which is the check that would have caught Upvest. `search_crm_objects(NOTE, associatedWith company X)`, then read the bodies. Martin's agent stamps its work `**Agent 4 — Company Intel**`. Upvest carried 318 of them. This is invisible to `notes_last_contacted`, which HubSpot only moves for calls, meetings, emails and messages, never for notes, so the one property the old screen named is the one property that cannot see a note.
3. **LinkedIn state from the CRM, not from a browser.** The portal carries HubLead properties that fill themselves: `hublead_last_linkedin_invitation_sent_date`, `hublead_last_linkedin_invitation_accepted_date`, `hublead_last_linkedin_message_sent_date`, `hublead_last_linkedin_message_received_date`. A pending invite on the contact means the second channel is already open and a new connect request is a duplicate. This is also the 10:00 scanner's real query: accepted-date since yesterday, rather than reading the LinkedIn UI.
4. **The park screen.** Any task on the company whose subject starts PARKED. Read the park's own reopen condition and say whether it is met, rather than obeying or ignoring the word.

**THE SUCCESSOR TASK IS PART OF THE BATCH, NOT PART OF THE FOLLOW-UP (added 25 Aug 2026).** The gate now demands a `followup` block on every lead: a date and what that touch has to carry. It refuses anything inside the seven-day floor and warns past four weeks. This closes the oldest hole in the desk: two rules said every send names its successor and nothing computed one, so the date was invented at the end of a long day or never, and forty overdue LinkedIn tasks piled up across three months with nothing forcing the question.

**Do not pick the date by hand.** `python3 scripts/followup_ladder.py <send date> --company=X --variant=A --channel=both` prints the whole ladder with real dates and the task body for each step: bounce check at +1 business day, connect check at +3, DM review at +14, then **three follow-ups at +7, +14 and +21** (Jacopo, 25 Aug 2026: "I want 3 follow up after the email that we sent... usually after 1 week and then after another week"), route-or-park at +39, park review at +60. `--check <proposed> <sent>` says whether a date someone typed is inside the window and why not if it is not.

**The failure paths get tasks too.** An account whose send BOUNCED still gets its bounce row and its route row. The successor task used to be created only when a send was confirmed, which meant the accounts most likely to be forgotten were exactly the ones the rule left out: Humanoid, the busiest board in the whole index, went two weeks with no dated task of its own because nothing about it had ever succeeded.

**When the gate blocks, the answer is never to loosen the gate.** If a check is wrong, it is wrong for a reason that can be written down, and the fix is a commit to `preflight.py` with that reason in a comment, not an override in the moment.

## The Lead Engine: one intake for cold and warm

Added 20 August 2026, Jacopo's design: every prospect enters through ONE pipeline with two feeds, and which feed they came through decides their opener. Trigger phrases: "run the lead engine", "fresh leads", "harvest".

**Parks carry an expiry, not just a reason (rule earned 24 Aug 2026).** Legora was parked on 12 Aug for a visible hiring slowdown: the board had shed 85 roles and "let me help you hire faster" lands badly on a team that just cut its plan. That call was correct on its data. Twelve days later the same board was at 269 roles with 54 posted in a fortnight and 22 open recruiter seats, and the press had them raising at a $10B valuation, reported the day AFTER the park was written. The park nearly cost the best lead of the month. So every park task NAMES ITS REOPEN CONDITION in testable terms ("removals stop and the count climbs again, or a funding round") and gets re-checked on a date, and any lead the engine surfaces is screened against parked accounts by reading the park's own condition rather than obeying the word "parked".

**Feed 1, market signals (COLD), the scaling detector.** The goal is to spot an EU company the WEEK it starts scaling, not the month after. Four signals, in order of timing value:

1. **Board velocity (the index's own diff).** `scripts/index.py` snapshots every scan to `board_history.json` and diffs against the previous run. A board that added 3+ roles since last scan is scaling RIGHT NOW, before any press release. New boards appearing and roles closing also show in the diff.
2. **The first recruiter role.** When a company posts its first Talent/Recruiter/People role, they have just decided to build a hiring function and have nobody running it yet. This is the single best-timed signal Tribe can act on, the diff flags it explicitly.
3. **TA pressure (the highest-conversion signal).** The scan computes, per board, the ratio of open TA roles to total roles and prints a "TA PRESSURE" section: 2+ open recruiter roles, or one TA role making up 10%+ of a meaningful board, means the company publicly cannot hire fast enough to hire. They know they have the problem, they are paying to fix it, and Tribe's pitch ("a recruiter inside your team next week, while your recruiter search runs") lands on a prepared mind. These leads jump the queue and get the 4,300+/€3,300 numbers as primary proof, because for TA-strained companies the numbers ARE the pitch.
4. **Funding rounds: triangulated, never single-source (Jacopo's rule, 20 Aug 2026).** No single funding feed catches everything, so the sweep TRIANGULATES: (a) the funding press: EU-Startups homepage, Tech.eu homepage, Sifted, Crunchbase News; (b) web search for rounds announced in the last 48 hours; (c) VC-side announcements when a specific fund matters (Atomico, Index, Creandum, HV, Speedinvest and the like announce their investments before some press picks them up). Cross-checking sources also catches number discrepancies (the first test found the press reporting €172M for a round the founder's own post announced as $200M; the founder's number wins). Then, before ANY funding find becomes a lead, run the second leg: **check their live open roles** (Ashby first, then Lever `api.lever.co/v0/postings/<slug>?mode=json`, then Greenhouse `boards-api.greenhouse.io/v1/boards/<slug>/jobs`, then the careers page). Funding alone is press; funding + a live board opening roles is a scale-up that needs attention. A company that posts a batch of roles the same day it announces the round, with zero TA roles among them, is scaling with nobody to run the hiring, the single best cold lead the engine produces. The Flip send proved the daily timing: round announced the 19th, email referencing it sent the 20th, no cold email is warmer than "your round closed yesterday". A round older than a week has already been pitched by every agency in Europe, so late finds get the board-data opener, not the funding opener.
**Evergreen postings are excluded from every number (fix of 24 Aug 2026).** Speculative applications, talent pools and "don't see your perfect role?" listings never close, because they are not real reqs. Left in, they poisoned everything: the oldest role in the index read as a 1,852-day Initiativbewerbung at Flip, n8n's "Leadership roles (Talent Pool)" was counted as an open recruiter req in the TA-pressure ranking, and the >300 day club was inflated by six. Both `index.py` and `index_post.py` now filter them via a shared `EVERGREEN` list. Any number quoted in an email or a post comes from the filtered set, and if a new evergreen phrasing shows up, add it to the list rather than eyeballing it out.

5. **The free bulk net: `scripts/funding_radar.py` (built and proven 20 Aug 2026, the quickest single step the engine has).** One command, zero credits: it sweeps 7 European funding-press RSS feeds (EU-Startups, Tech Funding News, ArcticStartup, Silicon Canals, Tech.eu, Startup Rise, FinSMEs Europe) for rounds announced in the last N days, extracts company + amount from the headlines, then auto-probes 7 ATS providers per company (Ashby, Lever, Greenhouse, Workable, Recruitee, SmartRecruiters, Personio) and scores each live board: total roles, roles posted in the last 14 days, TA-role count. Money + a board opening many roles fast + no recruiters = the Fonio profile (calibration: Fonio raised a $17M seed and its Ashby board holds 71 roles). Run `python3 scripts/funding_radar.py --days 3` daily and `--days 7` on the Monday harvest. Two output sections: scored board hits ready to draft, and "no public board found" names for a by-hand careers-page check. Respect the `[VERIFY SLUG]` tag: a board matched only on the first word of a multi-word name can be a same-named stranger (first run: "singular" resolved to a Tel Aviv company, not Singular Photonics; the tag caught it). Screen out staffing/recruitment agencies, they raise rounds too but are competitors, not clients. **Vibe/Explorium credits are reserved for email enrichment only (Jacopo's rule, 20 Aug 2026)**, never for lead discovery; the radar does discovery for free. The Explorium events filter (`new_funding_round`, last 30 days, EU, 11-500 employees) remains documented as a fallback bulk net, but running or exporting it needs Jacopo's explicit ok.

**RANK BY URGENCY, NOT BY STALENESS (added 24 Aug 2026).** The engine was optimising for the wrong thing. A role stuck 350 days is a striking number, but it is a TA person's problem and it has been true for a year, so nothing about today forces a decision. Score leads on how soon the pain becomes the founder's:

1. **Funded in the last 30 days + board growing + zero recruiters.** Highest urgency that exists. They have money, a plan, and nobody to execute it, and they will feel it within a month. Callosum and Legora both scored here and were the best leads of the week.
2. **First recruiter req just appeared.** They have accepted the problem and are spending on it. Highest intent, because the budget conversation already happened internally.
3. **Board velocity spike with a thin TA function.** The problem is arriving.
4. **A single very old role, everything else static.** Lowest. Quotable, but nothing changed this week, so there is no reason for them to act now.

The old scoring inverted 1 and 4 because a 350-day role reads more dramatic than a fresh round. Sort by urgency first, then use the dramatic number as the subject line once they qualify.

Each signal flows to the outreach queue and gets variant A or B, chosen by fit. A company hitting TWO signals in the same week (round + board velocity, or velocity + first recruiter role) jumps the queue.

**Feed 2, the commenting radar (WARM).** Clarified by Jacopo on 20 Aug 2026, first live test of the engine: the warm feed runs on FRESH LEADS, not the account list. Every company the cold feed surfaces gets its decision-maker checked for recent LinkedIn activity, and a founder who announced a round this week has ALWAYS posted about it. That announcement post is the best commenting surface that exists: comment there first, cold email never, variant W within the window. The engine's first test proved it three for three: all three founders found by the funding sweep (Gravis, Oceanloop, amber) had posted their round in the previous 72 hours. The account-list sheet is NOT a harvest source; commenting on account-list people is relationship maintenance Jacopo does on the side, and it only produces outreach when he says he commented and wants the follow-through. Jacopo comments on 2 to 3 posts a day. EVERY comment gets logged the same day as a HubSpot task on that contact: subject "WARMING: [name]", body naming the post topic, the comment date, and the outreach-ready date. THE WINDOW IS FRESH ONLY (Jacopo tightened it 20 Aug): outreach goes out WITHIN 72 HOURS of the comment, and SAME DAY OR NEXT DAY if the person replied or reacted, while the exchange is still on their mind. Past 5 days the warmth is spent and the lead falls back to the cold lane. Fresh comment, fresh interaction, fresh email: the whole point is that they still remember the exchange when the email lands.

**Both feeds merge Monday.** One harvest list, deduped against HubSpot, Tribester-owned accounts parked, each lead tagged COLD or WARM in its task. Then the standard machine below runs on all of them: CRM checks, board scan, verified address, draft, task, ladder.

**The two hard rules that make the engine work:**

1. **Never cold-email someone mid-warm-up.** Before drafting ANY first touch, check the contact for an open WARMING task. If one exists, the email waits for the window and uses variant W. A cold index email landing two days after a friendly comment burns both.
2. **A warm lead gets VARIANT W, not A or B**, and variant W is EXCLUDED from the A/B scoreboard (different population, warm openers always outperform, counting them would corrupt the test). Tag tasks "VARIANT W".

**Variant W needs Jacopo's explicit go, every time (his rule, 20 Aug 2026).** Never draft or send variant W unless Jacopo has SAID, before the draft is built, that he commented on the person's post (or otherwise tells you to use W). A warm-lane lead without that confirmation gets variant A or B like everyone else, alternating per the A/B rule. **This does not contradict "comment there first, cold email never" in feed 2 above, and here is the boundary:** feed 2's rule governs a lead surfaced BY the commenting radar, where a fresh announcement post exists and commenting is the cheaper first move, so that lead waits for Jacopo rather than getting a cold email. A lead that reached the desk any other way and merely happens to have a recent post is a cold lead and is treated as one. The days between 72 hours and 5 days are still warm but degrading: send that day or let it fall to cold, do not sit on it. The first harvest got this wrong: six W drafts were built on the assumption he would comment, and all six were rewritten to A/B the same day. Default is always A/B; W is the exception he unlocks in words.

**The red reminder line (restored by Jacopo 20 Aug 2026, format extended same day).** Every draft carries a red bold first line inside the body, and it is his full pre-send checklist at the exact moment he needs it: `[DELETE THIS LINE BEFORE SENDING. VARIANT X. Track box ON, logo in. Check the record: LinkedIn <contact profile link> | HubSpot <contact record link, app-eu1.hubspot.com/contacts/146748263/record/0-1/ID>. After you send, tell Claude so the task closes and the follow-up gets scheduled. If you commented on their post, ask Claude for variant W first.]` Add the empty-To warning when the address is unverified. The two links let him verify the person and the record Claude created before anything goes out; the after-you-send sentence is what keeps the follow-up ladder alive, because the close-and-schedule motion only runs when he reports the send. Known risk, accepted: the Corti send went out with a red line still in, so the line always starts with DELETE.

**THE SEND WINDOW IS 17:00 TO 18:00 PRAGUE (Jacopo, 24 Aug 2026: "I'll try to send them later in the day, I'll do it between 17 and 18").**

Batches were going out mid-morning. They now go out at the end of the working day, so the email is at the top of the inbox when a founder opens it the next morning rather than competing with everything that arrived between nine and lunch.

**This reshapes the day, and the new shape is better than the old one.**

| When | What |
|---|---|
| 10:00 | The scanner runs. It catches every acceptance and reply from last night's batch, and the DMs go out mid-morning while the prospect is at their desk. |
| During the day | Prep. Scan the boards, verify addresses, write the emails and the connect notes, create the records. |
| 17:00 to 18:00 | Jacopo sends. Email and connect note together, same as always. |
| Overnight | Acceptances land. |

**The scanner stays at 10:00 and fits better than it did.** Under morning sending it was racing the same day; under evening sending it does exactly the job it was built for, which is to open the next morning with everything that moved while nobody was watching. A DM at 10:00 answering an acceptance from 18:00 the night before reads as normal human timing. Answering ten minutes after the accept, which is what morning sending allowed, reads slightly like being watched.

**What this costs, and it is worth saying out loud.** Switching wholesale rather than alternating means there is no internal control, and the August baseline it would be compared against was untracked because of the GDPR gap. So "did evening sending help?" will not have a clean answer. What CAN be answered, now that lawful basis is set on every contact, is whether the absolute open rate is healthy. If evening sends come back at 30 to 50%, that is a good number on its own terms and no comparison is needed. If they come back near zero, the problem was never the timing.

**One thing that must not slip.** Sending at the end of the day means the send happens when energy is lowest, and that is exactly when the red reminder line gets skipped, the Track box goes unticked and an address gets typed wrong. The post-send reconciliation the next morning is now MORE important, not less.

**THE DOUBLE CHANNEL IS MANDATORY, NOT OPTIONAL (Jacopo hardened this on 24 Aug 2026: "for every email I want the connection messages to go out in parallel, I want multiple touch points for every possible lead").** Every single email drafted for a lead ships WITH its LinkedIn connect note, written at the same time, in the same batch, handed over together. A prep that produces an email and no connect note is INCOMPLETE and must not be presented as finished. This applies to cold first touches, follow-ups, and any new name on an existing account. There is no seniority filter and no "worth it" judgement: if they are worth an email they are worth the second channel, because the whole point is that one prospect gets two chances to notice, on two surfaces, the same day.

Ship them as one deliverable: the email draft in Gmail, the connect note text ready to paste, and the HubSpot task naming both. When a lead has no email address at all, the connect note is not a supplement, it is the primary channel and says so in its own words.

**The mechanics.** The note is under 300 characters (the LinkedIn cap, count it before handing the text over). Two channels arriving together read as one person being persistent, which is human; two channels pretending not to know about each other read as a sequence, which is software. So the note always names the email in its first clause. Claude drafts, Jacopo sends, same as every other channel. When an email BOUNCES, the connect note becomes the live channel and says so plainly ("I tried reaching you by email and it bounced").

**THE CONNECT-NOTE FORMULA, taken from the Velatir note (Jacopo, 20 Aug 2026: "why, because is a good one, try to do all like this").** Michael Sørensen accepted within the hour and Jacopo named that note as the template. Four beats, in order:

1. **Name the email, no apology.** "I sent you an email earlier, this is the second door." Not "sorry about that", not "forgive the double knock". Apologising for reaching out concedes that it was an imposition; the second door is just a fact, stated.
2. **Name a CHOICE they made, not an achievement they got.** This is the beat that does the work. Funding, valuation and press are things that happened to them, and complimenting those is what everyone else in their inbox does. Instead find the decision that had a cheaper or easier alternative and point at it: "Building the control layer on European infrastructure instead of renting someone else's". The trade-off is the tell that Jacopo actually understood the company.
3. **Judge it, bluntly, in his own voice.** "is a stubborn choice and I like it." A slightly contrarian adjective plus a first-person verdict makes it peer-to-peer. Founders get admired constantly and read past it; being ASSESSED by someone who grasped the trade-off is rarer and lands as respect. Never superlatives ("the most ambitious robotics story in Europe" is the weakest note of the first six, it praises without understanding anything).
4. **Close with connect and follow, no pitch, no ask.** "would be glad to connect and follow how it goes." Nothing about recruiting. The email is already carrying the pitch; the note carries the person.

**THE NOTE IS WRITTEN FROM THIS TEMPLATE, NEVER FROM THE EMAIL (Jacopo, 25 Aug 2026: "please use always those messagges and not rendom first liner from the email, fix it in your workflow").** On 25 August three notes went over that opened on "I track the job boards of 45 European scaleups every morning" and one that listed 215 days and a role count. That is the EMAIL's opener and the EMAIL's evidence, pasted into the note. It fails both tests below and it was caught by Jacopo, not by the desk. The note has exactly one skeleton and it does not get improvised:

> I sent you an email earlier, this is the second door. [Choice, as a gerund phrase] instead of [the cheaper or easier alternative] is a [contrarian adjective] choice and I like it. Would be glad to connect and follow how it goes.

Only three things vary: the choice, the alternative, and the adjective (vary the adjective across a batch so two founders who compare notes do not see one template). Nothing from the email's opening line, nothing from the board, no day counts, no role counts. **The one permitted change to beat 1** is when the lead has no verified email, where it becomes "LinkedIn is the front door here, I could not find a work address for you."

**Before any note is handed over, three checks, in order:** the skeleton above is intact; the character count is under 300 and has actually been counted; and the choice names a decision with a visible cheaper alternative rather than an outcome. A note that fails any of the three is rewritten before it is shown to Jacopo, not after.

**The test before any note goes out:** could this sentence be written about any other company in their category? If yes, it is flattery with a name filled in, and it gets rewritten. "I admire what you do" fails instantly, which is why it never gets used even when Jacopo describes the play that way. Second test: does it praise an outcome (round, valuation, growth) rather than a decision? Rewrite.

**THE ACCEPTANCE MESSAGE. One spec, and it is NOT here (consolidated 24 Aug 2026).**

The full formula lives under **"The conversation after they accept" > Rung 1**, below. Go there. Do not write an acceptance message from memory or from this paragraph.

**Why this section is a pointer instead of a copy.** It used to be a second, independent description of the same message, and within a single day the two had drifted apart: this one listed four properties and never mentioned the `Ciao [name]` greeting or the practice line, both of which are mandatory in the real spec and both of which exist for mechanical reasons (the greeting is what survives LinkedIn's mobile truncation; the practice line is what stops a board fact reading as surveillance). Anyone who followed this section instead of Rung 1 would have written a message missing its two most load-bearing parts, and would have had no way to know. A rule described in two places is a rule that will disagree with itself.

**What belongs here, and only this:** an acceptance is not an admin event to be logged and filed. It is a stranger opening a door, and the door closes again. Through 24 August the score is 4 acceptances from 10 double-channel sends against 0 replies from roughly 35 emails sent alone, so the accept is currently the strongest signal this system produces and it gets answered the day it arrives. If a message was queued when the connect was written, send that. If nothing was queued, write one on the spot rather than deferring it to a task.

When a connect is accepted and the person engages in the thread, touch 2 moves to a LinkedIn DM instead of email, they chose the channel. Accepted in silence keeps the email ladder but lets touch 2 open warmer, they know the name now.

**LOG LINKEDIN NATIVELY THROUGH THE HUBSPOT UI. NOTES FOR LINKEDIN ACTIVITY ARE BANNED (Jacopo, 24 Aug 2026: "don't add anymore notes is creating a mess in every people hubspot").**

HubSpot HAS a native LinkedIn activity type. It sits on the contact record under the **More** button in the activity row, as **Log a LinkedIn message**, alongside Log SMS and Log a WhatsApp message. It renders on the timeline with a LinkedIn icon, it is filterable by channel, and it can be counted in reports. Notes can do none of that.

**How this was missed for a whole day, which is the lesson.** The MCP connector cannot see the `communications` object, so the conclusion drawn was "HubSpot cannot log LinkedIn". That was wrong and it cost an afternoon spent on a REST API route, a private app, a token handoff and a message to an admin, none of which were needed. The connector's blind spot was mistaken for the product's. **When a tool says a thing is impossible, look at what a human sees in the interface before believing it.** Jacopo found it by opening the menu.

**The mechanics, all verified working 24 Aug 2026:**

- Use the host **app-eu1.hubspot.com**. The Chrome extension is denied read permission on `app.hubspot.com` and every call fails with "Permission denied for reading pages on this domain"; the EU host works. `https://app-eu1.hubspot.com/contacts/146748263/record/0-1/{contactId}`
- Click **More** (aria-label matches `/More activities/`), wait ~1.3s, click **Log a LinkedIn message**, wait ~2.5s.
- The editor is `[aria-label="Create a Logged LinkedIn message"]`. Focus it and fill with `document.execCommand('insertText', ...)`. **Setting innerHTML does not register with React** and the Log button stays disabled.
- Element refs from `find` go stale because the menu closes on blur. Drive the whole sequence in ONE `javascript_tool` call instead of find-then-click.
- The dialog carries its own **"Create a To-do task to follow up in 3 business days"** checkbox. Tick it for PENDING connect requests, where a three-day acceptance check is exactly the right question. Skip it where the contact already has dated tasks, or the list fills with duplicates.
- **After ticking that checkbox, wait ~1.5s before clicking Log.** Clicking immediately lands mid-rerender and silently does nothing, and the dialog just sits there looking fine.
- Confirm success by checking the editor is gone from the DOM.
- The **Activity date defaults to now and React rejects programmatic changes**. If the real send time differs, put it in the body in square brackets rather than fighting the field.

**What goes in the body:** the message text verbatim, then one bracketed line carrying what the text does not say. When it was sent, the current status (pending, accepted, replied), and anything that decides what happens next.

**Connection requests are logged the same way**, as a LinkedIn message carrying the connect-note text plus the bracketed status line. There is no separate "log a connection request" type, and the `Engage on LinkedIn` submenu (Send InMail, Send connection request) sends through Sales Navigator rather than logging something already sent by hand.

`scripts/linkedin_to_hubspot.py` remains in the repo as the API route, and it is now the FALLBACK rather than the plan. It needs a private app token and an admin; this needs a browser. Prefer this.

**PARALLEL AT TOUCH 1, SEQUENTIAL AFTER IT (stated 25 Aug 2026 because it never was).** Two rules in this file read as opposites: the double channel is mandatory, and one channel runs at a time. Both are right and they govern different moments. **Touch 1 is both channels on the same day**, because the point is that one prospect gets two chances to notice on two surfaces and two arrivals together read as one person being persistent. **Every touch after that is one channel**, because two channels chasing the same silence reads as software. If they accepted and engaged, the channel is LinkedIn and email stops; if they accepted in silence or ignored both, the email ladder carries the account and LinkedIn goes quiet.

**Every LinkedIn touch gets a dated follow-up task too, same as an email.** An unanswered email still sits in a visible thread; an unanswered DM leaves no trace anywhere, so without a task it is simply forgotten. Two weeks out: one task to review DMs sent (if silent, do NOT nudge on LinkedIn, the email touch 2 is the next move, one channel at a time), and one to decide on connects never accepted (leave them pending, withdrawing and re-sending reads as pestering, unless LinkedIn is the only route in, in which case the account needs a verified address or it parks).

**Email patterns are per-company and must not be inferred from one record (24 Aug 2026).** DeepL's Head of TA is `amanda.johnson@deepl.com`, so firstname.lastname looked settled; the CEO is actually `kutylowski@deepl.com`, plain lastname. One address on file proves that address, never the pattern. Confirmed patterns so far: Mistral `firstname@`, Langfuse `firstname@`, ecoplanet `firstname.lastname@`, GitGuardian `firstname.lastname@`, DeepL `lastname@`. Record each one as it is confirmed, and treat an unconfirmed pattern as an empty To line.

**SET THE GDPR LAWFUL BASIS ON EVERY CONTACT AT CREATION, OR THE SEND IS INVISIBLE (24 Aug 2026, and this one explains a month of confusion).**

This portal has HubSpot's GDPR tools switched on. **A contact with no `hs_legal_basis` value is silently excluded from email tracking.** HubSpot shows a one-line banner at send time ("Because your HubSpot account has GDPR tools enabled, the following email recipient will not be tracked") and then sends the email perfectly normally, with no pixel and no way to ever know it was opened. The BCC still logs the send, so the CRM looks complete and the activity is there. Only the open data is missing, and nothing downstream flags it.

**The measured damage.** Of the ten leads in the August batch, exactly TWO carried a lawful basis: Ralf Gulde and Fabian Riedel, both of whom came in with the original October 2025 import. The eight created since, by enrichment or by hand, had none. So of fourteen cold sends, twelve could never register an open under any circumstances.

**What that did to the diagnosis.** The desk read "1 open in 14" as a catastrophic open rate and concluded the emails themselves were failing. The real denominator is 2, not 14. One of the two trackable sends was opened, which is an ordinary cold-email open rate and says nothing is wrong with the emails at all. **An entire redesign of the A/B test was argued on a number whose denominator was wrong.**

**The rule.** `hs_legal_basis` gets set at the moment the contact is created, in the same call, alongside the email address. It is not an optional field and it is not a compliance afterthought: it is the switch that decides whether anything about that account can ever be measured. A contact created without it is a contact whose outreach is unfalsifiable.

**The value to use is Jacopo's to choose, not Claude's.** It is a declaration about the legal ground for processing someone's data, so it is the controller's call. The value already established on this portal for cold prospects is "Legitimate interest – prospect/lead". NEVER use "Not applicable", which HubSpot documents as exempting the contact from GDPR protections entirely.

**The check that would have caught this in a day.** The daily tracking-health step must now compare, for the previous day's sends, the number of recipients carrying a lawful basis against the number sent. Untracked-by-GDPR is a different failure from Track-box-lapsed and needs naming separately, because the fix is on the contact record rather than in the Gmail extension.

**Screen boards by LOCATION, not just by size (24 Aug 2026).** The velocity diff surfaced 1X as the best lead of the day: 82 roles, +6 in four days, three recruiter searches stuck at 69 days. Every single role was in San Carlos and Hayward, California. The counts were real and the lead was worthless, because Tribe sells EMEA hiring. Any board probe that feeds a lead must print the location distribution, and a board that is majority non-EU gets dropped before anyone writes a word.

**Not every board is on an ATS API (24 Aug 2026).** Synera's careers page is a Webflow page at synera.**ai**/careers, invisible to `index.py` and to every provider probe. When the probes come back empty but the company is clearly hiring, open the careers page in the browser before concluding they have no roles. Record which companies need that treatment so future scans do not repeat the dead end.

**Empty-To drafts get a character-by-character check after the send (rule earned 20 Aug 2026).** The first batch of empty-To drafts produced the exact failure the address rule exists for: one send left with To filled as "1@thehumanoid.ai", an autocomplete or typing slip that bounces, and one with a pattern guess typed at send (jascha@callosum.com, bounce-watch). So whenever a draft went out that had an EMPTY To line, the post-send reconciliation must read the actual recipient from the Sent folder character by character, never assume the intended address was the one used. A slip send does NOT count as a touch and does not enter the A/B tally until it lands; the resend to the corrected address is touch 1. The BCC will also have auto-created a ghost contact for whatever address was actually used: rename it, queue the merge, and if the address was junk, ZZ-DELETE the ghost after the bounce confirms.

**Variant W, the warm opener.** First line references the exchange, second line goes straight to their board, then the standard skeleton (solvable line, role-matched proof, five-day shortlist, index cut give, coffee close):

> Hi [name], good exchange under your post on [topic] the other day.
>
> It got me looking at [company]'s board: your [role] has been open [X] days, and the median [category] role across the 45 scaleup boards I track closes in [Y].
>
> [continue with the variant A skeleton from the solvable line onward]

If the person REPLIED to Jacopo's comment (not just liked), the W touch goes as a LinkedIn DM instead of an email, same content compressed to four sentences, no signature block. They chose that channel by engaging there.

**Desk integration:** the daily run (tribe-sales-desk) asks "who in the warming queue is ready today?", open WARMING tasks whose ready-date has arrived become that day's warm sends, capped by the same 2-outbound-tasks-per-day rule, warm before cold when both compete.

## The order that matters

Do these in sequence. Skipping the CRM checks and going straight to drafting is the single most common way this goes wrong, because you end up writing to someone a colleague contacted last week, or creating a second record for a person who is already there.

### 0. Reconcile the task list against Sent mail first

Before drafting anything, before opening a single task, do this. It takes a minute and it is the difference between a task list he trusts and one he skims.

**HubSpot does not close a task when the email is sent.** There is no link between the two. The BCC logs the send as an activity on the contact, but the task stays `NOT_STARTED` until a human clicks Complete, and nobody clicks Complete because the moment the email goes out the work genuinely feels done. Snoozing makes it worse: a task pushed a week forward does not stop him sending today, and sending does not cancel the snooze. On 4 August 2026, five of the six tasks HubSpot showed as due had already been sent on 28 and 29 July. Working that list top to bottom would have sent five people a duplicate.

So:

1. Pull every open task due today or earlier.
2. Search Sent mail for each recipient. If the email in the task body has already gone out, **close the task**, do not draft it. Rewrite the body to say what was sent, when, and whether a reply came.

   **Two rules that live in tribe-sales-desk and were missing from this copy for a week (added 25 Aug 2026).** This step exists in both skills and the two had drifted, with the weaker version here, which is the one a reader entering through "write cold emails to these people" hits first. Both of these were earned the hard way: **read the actual recipient out of the Sent folder character by character**, never assume the address in the task body is the one used, and **do not trust Jacopo's own account of what he sent either** ("I did everything apart from Zoe" against a Sent folder showing five of six). The canonical version of this whole routine is tribe-sales-desk section 1; when the two disagree, that one wins.

   **Never trust the message list that `search_threads` returns.** It gives back a thread's messages, but that list can be stale and silently miss the most recent ones. On 4 August 2026 a thread was returned by a query filtered on `after:2026/08/02`, which means the search index knew a message existed in that window, yet the messages array stopped at 31 July and omitted the 3 August reply entirely. Acting on that produced a confident, twice-repeated, wrong claim that nothing had been sent.

   So: use `search_threads` to find candidate thread IDs, then call **`get_thread`** on each one before concluding anything about what was or was not sent. If `get_thread` output is too large, dump it and pull the dates and bodies with `jq` rather than skipping the call. Never tell him an email was not sent on the strength of a search alone.
3. Then search the inbox for replies from prospects **that have no task behind them**. This is the mirror-image failure and it is the expensive one. HubSpot creates nothing when someone replies, so a live conversation can go quiet with nothing tracking it. On the same day, Magdalena Maier had replied four days earlier on a deal with a proposal and a price on the table, and there was no task anywhere.
4. Only then draft what is genuinely left.

Report the reconciliation before the drafts. He should see what was already done, what is newly live, and what still needs writing, in that order.

### 1. Check whether they already exist

Search HubSpot contacts **twice**, by last name and by first name. Both, not one.

Surname spellings drift. A real example: Payhawk's VP of People was in the CRM as "Yana Panayatova" when her name is Panayotova. A last-name search alone would have created a duplicate.

Then check what you find:
- **Exact match on the person** → do not create. Update the existing record and note who contacted them and when.
- **Same name, different company** → different person, proceed.
- **Person exists but sits under the wrong company** → fix the association rather than creating a second record.

Also search contacts by the company's email domain (`*@company.com`). If anyone at that company already has an address, you have just learned the email pattern for free, which matters enormously in step 3.

**If another Tribester owns the company or any contact on it, stop.** This is a hard rule, not a judgement call. Run queries 1 and 2 of the preflight gate: `hubspot_owner_id` AND `hs_lead_status` on every associated contact, plus the notes on the company. **Owner alone is not the test.** Upvest had no owner on any record and was being worked; amber had a blank company last-contacted and a CEO emailed the day before. `notes_last_contacted` in particular does not move when a note is written, so it cannot see another agent's work at all. If someone else's ID is on it, the account is theirs. Park it, tell Jacopo whose it is and when they last touched it, and keep the research in case they want it. Two Tribesters landing in the same inbox is worse than not writing at all, and the prospect will notice before we do. On 11 August this rule removed Moss, Neko Health, NavVis, Quantum Systems and Dwelly from a batch of otherwise good leads, all inside one search.

### 2. Check the company record, and always set the domain

Search companies by name before associating anyone. Duplicate company records are common in this portal, usually one from an old CSV import and one created later with a domain.

**Never create a company with a blank domain.** The domain is the only field HubSpot dedupes companies on. A record saved without one cannot match anything created later, so the moment an email goes out and HubSpot auto-creates the company from the address, there are two.

This is not theoretical. On 5 August 2026 four companies were created with the domain left blank, on the reasoning that a wrong domain is worse than no domain. Fifty-five minutes later an enrichment run created the same four with domains attached, and nothing matched: Humanoid, ORE Energy, Aveni and Wordsmith all ended up doubled. The caution caused the exact damage it was meant to prevent.

So: take the domain off the company website, which is a fact rather than a guess, and write it in. If the website genuinely cannot be found, say so out loud and expect a duplicate rather than creating the record quietly.

Two traps when the domain comes from an enrichment CSV:

- **A LinkedIn URL is not a domain.** PhantomBuster columns put `uk.linkedin.com` and `de.linkedin.com` into the domain field on 11 August 2026 and produced two nameless orphan companies. Read the value before writing it. If it contains `linkedin.com`, it is the profile URL, not the employer.
- **Mail domain and web domain can differ.** ORE Energy's site is `oreenergy.com` and the address that works is `aytac@oreenergy.nl`. Where they split, use the web domain on the company and note the mail domain on the contact.

If duplicates exist, tell Jacopo which to keep and which to merge in, and pick the primary on this basis: most contacts, then most activity, then correct domain and country. Merging is UI-only, the API cannot do it, so hand him the record IDs rather than promising to fix it.

Associate new contacts to the **surviving** record. Associating to one that is about to be merged away scatters the activity history.

### 3. Get the email address before creating the contact

This is the rule that prevents the most damage.

If you create a contact with a blank email field and Jacopo then emails that person, HubSpot cannot match the send to the record and silently creates a **second, nameless contact** holding only the address. It happened within an hour of creating a batch. Every send against a blank-email contact spawns one.

So: address first, record second. Ways to get one, in order of reliability:

1. **Another contact at the same domain already in HubSpot.** Free, and confirms the pattern.
2. **A confirmed send.** Once one email to that domain lands, the pattern is known. Mistral turned out to be `firstname@mistral.ai`, not the `firstname.lastname` everyone assumes.
3. **An address published in a post or signature.** People put referral addresses in hiring posts.
4. **Jacopo's enrichment tool.** He uses PhantomBuster. Hand him the LinkedIn profile URLs as a paste-ready block, since that is the input it wants, and ask for the CSV back.

**If you cannot get an address, do not create the contact yet.** Hold the name in the chat, hand Jacopo the LinkedIn URL for enrichment, and create the record once the address comes back. An empty-email contact is not a neutral placeholder, it is a duplicate with a delay on it.

This kept happening even after the rule was written down. On 11 August 2026 four named contacts were created with blank emails at 08:41. By 08:54 the sends had spawned four nameless records holding only the addresses: Aytac Yilmaz, Joseph Twigg, Ross McNairn and Francesco Sciortino, each existing twice. Thirteen minutes.

If Jacopo overrules this and wants the record created anyway, create it, then say in the same message that a merge will be needed after the first send and name the two records he will be merging.

Do not write a guessed address into the record either. A wrong address in a CRM is worse than an empty one, because it looks verified.

**When a ghost record already exists**, merge the named record as primary and the email-only one into it. The named record's email field is blank, so it inherits the address, the title and name survive, and the send history comes across from both sides. Before handing the pair over, write the name and job title onto the ghost, so the merge screen shows a person rather than an email string.

### 4. Decide the channel

**1st degree connections get a LinkedIn message, not a cold email.** Emailing someone who is already a connection reads worse than messaging them, and it wastes the warmth.

Check the degree while researching. If the profile says 1st, write a short LinkedIn message instead of an email and say so.

### 5. One person per company at a time, and always at the top

**Seniority is a hard rule: CEO, founder, or Head-of level only. Never an individual contributor.** A Talent Partner, a recruiter, a sourcer, a People Ops specialist cannot buy this and cannot champion it upward without it reading as outsourcing their own job. On 13 August a draft went to a Talent Partner at Cambridge Aerospace and Jacopo rejected it flat: "she is just a TA, reach for the CEO or Head of every time." The individual contributors still matter, but as account intel in the task body (they are who executes after the yes), not as recipients.

So the recipient hierarchy is: **CPO or VP People or Head of People or Head of TA if one exists, otherwise the CEO or a founder.** If LinkedIn shows only individual-contributor TA people with nobody above them, that does not make the senior-most TA person the target. It makes the CEO the target, and the missing People leadership is usually the angle.

Two emails into the same company on the same day reads as a sequence rather than two people who happen to be interested. Pick a primary contact per company and name the backup.

Ordering that works when both exist: **People or TA leader (Head-of or above) first, founder or CEO two days later.** The CEO email should end by offering to route the conversation back to the People person, which gives them an easy non-awkward reply and stops the two threads competing. When writing to a CEO cold, close with a routing question ("is this sitting with you, or is there someone I should be talking to?") so the right owner surfaces without a second cold thread.

**Always carry the proof numbers when writing to a CEO or founder.** 4,300+ hires, average cost per hire of 3,300 euros, and the client name that matches their situation (Wolt across CEE, Germany and the Nordics for multi-country scaling, Upvest's Berlin tech team for engineering builds, Glovo in Italy for commercial). A CEO reads numbers before pitch. A Head of People reads the model before the numbers. Match the order to the reader.

## Writing the email

**The first touch leads with the Tribe Board Index, data nobody else has.** Candidate-profile teasers were tried by Martin and did not convert, so the primary hook is the index instead: a weekly scan of 45 European scaleup job boards via the Ashby posting API. THE SCAN IS BUNDLED: run `python3 scripts/index.py` from this skill's directory before every batch (add a company slug to also dump that board's roles, `--probe N` for a specific age's percentile). The slug universe lives in `scripts/board_common.py`, shared by index.py and index_post.py. Add new boards THERE and nowhere else, and note the change here so week-over-week numbers stay comparable. It was duplicated in both scripts until 24 Aug 2026 and they had drifted to 41 and 45, publishing two different role counts for the same index on the same morning. Never rebuild the scan from memory. **NO INDEX NUMBER IS WRITTEN DOWN IN THIS FILE ANY MORE (25 Aug 2026).** A block of 18 August figures lived here and was slotted into emails for a week after the evergreen filter changed every one of them: those medians counted talent pools and Initiativbewerbungen as open roles, which the file bans two hundred lines earlier. A number in a skill file is a number nobody re-checks. The scan prints today's figures in two seconds, and today's figures are the only ones that go in an email. The email states the prospect's number against the market: "Your AE role is at 140 days, older than 87 percent of the 1,613 roles I track." Nobody else can send that sentence, it is verifiable, and it makes the sender the person with the data rather than the person with the pitch. Offer the relevant index cut ("the Dutch robotics cut", "the German-speaking SaaS sales cut") as the give, it earns a reply that costs the prospect nothing. REFRESH THE NUMBERS before each batch, stale index numbers are worse than none, and never quote a percentile that was not computed from a real scan.

**THE FIVE-BEAT STRUCTURE IS DEAD, and this tombstone is deliberate (25 Aug 2026).** It was adopted on 19 August, retired by the 24 August rewrite below, and left standing here in full for six days. Anyone reading top to bottom hit it first and wrote the zero-reply email in good faith. The templates that are actually current are VARIANT A, B and C below, and nothing above this line specifies an email. What the five beats got wrong, in one line each, because knowing why keeps them from creeping back:

1. The "This week I checked [company]" opener put the sender in the first seven words.
2. The flat gap survives, it is the one beat that worked, and it is beat 1 of variant A now.
3. The "that's solvable" rescue sentence became the pitch line and is optional.
4. The artifact offer was one ask too many and is now rung 3 of the acceptance ladder.
5. The coffee close was the third ask in a three-ask email and is retired for first touches.

The dead text follows, indented, so nobody re-derives it by accident:

1. **The opener, always this exact shape, Jacopo's final call on 19 August**: "This week I checked [company] against the 45 European scaleup job boards I track, [total] open roles in total. The median [their role category] role closes in [X] days." The company name sits in the first sentence, and the median quoted is THEIR role category from this morning's scan, never the overall median and never a figure quoted from this file. Do not swap in portfolio phrasings like "out of all the boards and clients we track", that variant was tried on 19 August and Jacopo overruled it the same day. This opener, all the time.
2. **The result, stated flat**: their number against the market, no adjectives. "Your two autonomy roles are at 242 days. The median across the index is 46." The gap does the selling.
3. **"That's solvable, and it's exactly what we did for X, Y, Z"**: one sentence that turns the bad news into a fixed problem, with role-matched client names as the proof (proof rules below apply in full). This beat is why the email reads as help rather than criticism, do not soften the result in beat 2 to compensate, the rescue only works if the gap was stated plainly.
4. **The artifact, offered before any commitment**: a concrete piece of work they get whether or not they ever pay. The relevant index cut, or the first shortlist inside five days before any contract. Named specifically ("the Dutch robotics cut", "three profiles by Friday"), never "some insights".
5. **The close per the close rules below**: coffee line for founders, one soft concrete question for Heads of People. If a call is already booked or offered, beat 4 lands "ahead of our call", which gives the meeting a reason to exist before it starts.

## THE REWRITE OF 24 AUGUST 2026, and why

Thirty to forty cold first-touches went out across August. **Zero replies.** Not one, across every variant, sector and seniority. Domain auth was checked and is clean (SPF, DKIM, DMARC at p=reject), so delivery was never the problem. The diagnosis and Jacopo's approved fixes are below, and they OVERRIDE the earlier template rules wherever they conflict.

**Statistical honesty first.** Zero out of ~35 is consistent with a true reply rate anywhere between 0% and roughly 8%, so it is weak evidence on its own. What it does prove is that the measurement was useless: no open tracking meant three failure points (delivered, opened, replied) collapsed into one unreadable number.

**THE FIVE FIXES.**

**1. Subject lines carry a fact, never the company name.** The archive already proved this. "127 days against a market median of 33", "still 313", "8 roles in New York" are specific and about them. "Tribe / Legora" and "Tribe / RPO comparison" are a vendor announcing itself. THE `Tribe /` PATTERN IS DEAD, do not use it again. Build the subject from the single hardest number in the email, lowercase, no company name, under 45 characters so it survives a phone preview.

**2. The first seven words are about THEM.** "This week I checked Legora against the 45 boards I track" opens I, I, I. Flip it: "Your Talent Acquisition Partner has been open 278 days." The index is how Jacopo knows, not what the email is about, so it moves to the second clause or the second line.

**3. One ask. One.** The old template asked for the index cut, offered a five-day shortlist AND proposed a coffee, which is three asks and therefore none. **Close on a real question they can answer in one line**, the way the LinkedIn DMs do: "Who is covering the searches until that Director starts?" A question gets a reply; an offer gets ignored. The answer also qualifies the deal, which a coffee line never does.

**4. Eighty words, not two hundred.** Founders triage on a phone. Cut the paragraph that explains embedded recruiting, cut the second proof story, keep one client trio and one number.

**5. Founder framing, not TA framing.** A stuck role is a TA person's problem. Founders feel burn, slipped roadmap and board pressure. Translate the same fact: not "your AE has been open 146 days" but "that BeNeLux seat has been empty five months, which is two quarters of pipeline nobody built." Same data, their language. For Heads of People and TA leaders, keep the raw metric, it IS their language.

**THE TWO EMAILS. Every first-touch cold email is variant A or variant B, nothing else.**

**VARIANT A, the index email.** ONE specification, and it is THE VARIANT A TEMPLATE further down this section. Do not write A from this paragraph, from the JUPUS send, or from memory. This sentence used to carry a second, competing description of variant A that mandated the six things the rewrite had just banned, and the two sat 74 lines apart with nothing marking which was current.

**VARIANT B, the Claude candor email.** Jacopo's design, and the canonical text below is the version HE ACTUALLY SENT on 20 August (Alan, Corti, Medly), which supersedes every earlier draft. His final edits: the competitor-names line ("It surfaced Talentful, Join Talent and Chapter 2") is CUT, so "Tribe was nowhere in the results" lands directly after the test and the email never hands the prospect a shopping list. **Subject: the same fact-based convention as A and C, never `Tribe /` (resolved 25 Aug 2026).** B was designed in the `Tribe / [category] comparison` era and fix 1 above kills that pattern by name, quoting "Tribe / RPO comparison" as the example of a vendor announcing itself. For six days this line and fix 1 both stood, and on 25 August a B draft went out to Enpal carrying the dead subject because this line was the one read last. The body of B is unchanged and still Jacopo's; only the subject follows the newer rule. Never a competitor name in the subject either. The walk-through question is role-matched: "how it worked at Zalando?" for an engineering-heavy prospect, "at Wolt?" for GTM or general. SPACING RULE: each opening sentence on its own line with a blank line between. As sent:

> [name], I ran a quick test in Claude, asking which RPOs it recommends for companies scaling in Europe.
>
> Tribe was nowhere in the results.
>
> Fair enough; we put our budget into recruiters instead of Marketing.
>
> Good news is the exact work that we did in: Wolt's commercial teams across five markets, Glovo in Italy, engineering searches for Zalando and Spotify, each with one of our recruiters sitting inside the team, working in their ATS, owning every search to signed offer.
>
> For [company] concretely: [their board or funding fact, one sentence, what one recruiter inside would run].
>
> Want me to walk you through how it worked at [Zalando/Wolt, role-matched]? First shortlist within five days, before any contract is signed, so you judge the work before the name.
>
> I'll pinpoint the differences and where other RPOs are winning in our call and lay out the best possible service for [company]. I can send it over ahead of our call!
>
> I'm always happy to connect with other founders in [city], even if not for collaborations, just for a coffee chat.
>
> Best,
> Jacopo

**VARIANT B'S IDENTICAL BLOCK IS A LIABILITY, fixed 24 Aug 2026.** Roughly 80 words of B were byte-for-byte identical in every send: the Claude test, the "Tribe was nowhere", the budget line, the client list. Two problems. Mail providers cluster on repeated blocks even when SPF, DKIM and DMARC are perfect, and two founders in the same city who compare notes see a template instantly. **So the FIRST paragraph must now carry a per-recipient variable**, something only true of them, before the identical block starts: "I ran a quick test in Claude, asking which RPOs it recommends for companies scaling in Europe. Yours came up, mine did not." or a sector-specific framing of the question asked. If nothing recipient-specific can be woven into the opening, send variant A instead.

Rules for B: RUN THE PROMPT IN CLAUDE ONCE BEFORE EACH BATCH, if Tribe appears in the results the email is dead and the fact changes; [company] slots must never be wrong; and never use the same opening twice in overlapping networks (two Berlin founders who know each other get different emails). **UNRESOLVED FACT, and it is in sent mail.** The 20 August sends said "across five markets" (Alan) and "across 25 markets" (Medly) for Wolt. Both are out there. Until Jacopo confirms which is true, **variant B ships with "across five markets"** (the more conservative of the two, and the one in the canonical text above) and every batch report that includes a B send repeats this line until it is settled. A prospect who asks on a call must get the same answer the email gave, and right now two different answers exist.

(Parked for after the test, not to be used while it runs: diagnostic, weekly-scan-callout, 300 Club and competitor-pool openers.)

### The A/B test, started 19 August 2026

**RESCOPED 24 AUGUST 2026. The original design could never have concluded anything and was retired before it produced a false verdict.**

**Why it was broken.** To distinguish a 3% reply rate from a 6% one at any confidence you need several hundred sends per arm. The test was calling it at TEN. At Jacopo's volume, measuring whole emails on replies is decorative: the verdict would have been indistinguishable from a coin flip, and it would have been believed.

**The new design. Three rules.**

**1. Test ONE variable at a time, and test the subject line first.** Not two whole emails. The subject is the biggest single lever and the cheapest thing to change. Everything below the subject stays identical across the arms, or the comparison means nothing.

**2. Measure OPENS, not replies.** Open rates run 40 to 60%, so 40 sends per arm produces readable signal. **At this desk's real volume that is not two weeks, and saying so matters:** the cap is two cold sends a day, so 80 sends across two arms is roughly eight working weeks, i.e. a verdict around late October rather than early September. An earlier draft of this section promised two weeks, which would have had the test read as stalled or the cap quietly broken to make the date. The scoreboard is a running tally with no promised verdict date; the verdict comes when both arms reach 40. Reply rate stays the north star of the whole desk, it is simply not the test metric, because it is too rare to move a test at this volume.

**3. THE TRACK BOX IS NOW A HARD GATE.** It lapsed through the entire August cohort and that is precisely why zero replies was unreadable. No Track box means no open data means the test does not run at all. If a batch goes out untracked, it is EXCLUDED from the test rather than counted, and the daily run flags it.

**The first test, live from 25 August 2026:** subject line style. Arm 1 is the number-fact subject (`111 days for a head of people`). Arm 2 is the consequence subject (`forty-five roles waiting on one hire`). 40 sends per arm, alternating, everything below the subject identical. Metric: open rate. Verdict when both arms reach 40, not on a calendar date.

**A AND B ALTERNATE ACROSS THE DAY'S BATCH (Jacopo, 25 Aug 2026: "why there is no variant B also in the Mail I want both A/B so we can test it").** This overrides the earlier "choose by fit, not by alternation" line, which was written when A and B had stopped being test arms and which produced a day where both sends were the same body. When the day has two cold sends, one is A and one is B. When it has one, alternate with yesterday. Fit still breaks ties: if a prospect's board gives no hard number, B is the one that survives without it. **Variant C runs only when Jacopo asks for it**, and it displaces one arm rather than being added as a third.

**The scoreboard, every daily run:** report sends, opens and replies per arm in one line ("subject A: 12 sends 7 opens, subject B: 11 sends 4 opens, 0 replies either"). Untracked sends are reported separately as excluded. The tally lives in the HubSpot tags and the inbox, so it can always be rebuilt from scratch.

**THE VARIANT A TEMPLATE, rewritten 24 Aug 2026. Target 80 words. Four beats.**

> **Subject:** [the hardest number, lowercase, no company name, under 45 chars]
> Examples that work: `111 days for a head of people` / `278 days to hire a recruiter` / `350 days for one AE seat` / `12 roles posted, no recruiter`
>
> [First name], your [role] has been open [X] days. Across the 45 European scaleup boards I track that is [the percentile fact: "the slowest ten percent of all recruiting hires" / "older than 98% of every role I see"].
>
> [The consequence in THEIR language. Founder: "that is two quarters of pipeline nobody built" / "forty-five roles are waiting on that person". Head of People: the raw second metric.]
>
> We put a recruiter inside teams in exactly that spot, working in your ATS, first shortlist in five days. [One client trio, role-matched: Zalando, Spotify and Kayak for engineering; Wolt and Glovo for commercial.]
>
> [ONE question, answerable in a line: "Who is covering the searches until that Director starts?" / "Is the plan to hire a recruiter or bring in outside capacity?"]

**Worked example (Sereact, 24 Aug), 72 words:**

> **Subject:** 111 days for a head of people
>
> Ralf, your Director People & Culture has been open 111 days. Across the 45 European scaleup boards I track that is the slowest ten percent of all recruiting hires.
>
> Forty-five roles are waiting on that person, twenty-six in Stuttgart.
>
> We drop a recruiter inside teams in exactly that spot, working in your ATS, first shortlist in five days. Zalando, Spotify and Kayak while they scaled.
>
> Who is covering the searches until that Director starts?

**What was deliberately removed and must not creep back:** the "This week I checked" opener, the paragraph explaining what embedded recruiting is, the index-cut offer, the coffee-chat close, the second proof story, and the `Tribe /` subject. Every one of them was in the zero-reply cohort.

**What survives:** the signature block (always), the BCC (always), the red reminder line (always), and the rule that every number comes from a scan run that week.

**What carries over from the JUPUS era, and nothing else does:** paragraph two ends on a short verified punch from their board; the one-line efficiency proof ("Across our clients: 4,300+ hires at an average cost per hire of 3,300 euros") rides in engineering and founder emails, and for TA and recruiter roles those numbers ARE the main proof; every slot is filled from a scan run that morning. The JUPUS *shape* is retired with the five beats. There is no coffee line in a first touch to swap out.

**VARIANT C, THE CHOICE EMAIL. Added 24 August 2026 on Jacopo's instruction ("add variant C now, run alongside").**

**The hypothesis, stated plainly so the test can kill it.** The connect note is accepted by 40% of the people who receive it. The email is replied to by none of them. The notes and the emails go to the same people on the same day, so the difference is not the audience and not deliverability. The structural difference is this: **the note opens on a choice they made and judges it, and asks for nothing. The email opens on a problem they have, diagnoses it, and pitches.** Founders engage with being understood and ignore being diagnosed by a stranger.

So variant C is variant A with the pitch removed and the connect note's opener bolted on. **The variable under test is the pitch itself**, not the wording around it.

> **Subject:** [same convention as A, the assigned subject arm, lowercase, under 45 chars]
>
> [First name], [the CHOICE they made, named specifically, with the cheaper or easier alternative visible in the sentence].
>
> [The judgment. First person, one clause, slightly contrarian, never a superlative.]
>
> [The pivot, and the ONLY number in the email, from their own board, scanned this week.]
>
> [ONE question about their operation, answerable in a line.]
>
> [Signature]

**Worked example (Dash0, 24 Aug), 74 words:**

> Mirko, you built Dash0 OpenTelemetry-native, which gives up exactly the lock-in that made the last generation of observability profitable.
>
> That is an expensive thing to walk away from on purpose and I think it is the right call.
>
> The hiring version is less comfortable. Your Commercial AE in Amsterdam has been open 350 days, older than 98% of every role across the 45 European boards I track.
>
> Is that a candidate supply problem, or does nobody have the hours to run it?

**What C must NOT contain:** what Tribe does, the client trio, the cost-per-hire line, the shortlist promise, the index-cut offer, a call to action of any kind. All of it moves to rung 3 of the conversation ladder below, where it is earned rather than assumed. If writing C feels uncomfortably like giving something away for nothing, that is the point of the test.

**Running C alongside.** C is not a standing third arm, it runs on Jacopo's say-so and displaces A or B for that send. It is judged on REPLIES over a long window rather than on the subject test's open metric, and the daily scoreboard reports it as its own line. The subject-line test continues underneath, unaffected, because the subject convention is held identical across all three bodies.

## The conversation after they accept

**This is the half the system has never had, and Jacopo named it on 24 August 2026: "people are accepting, at least we have the first point of contact, we have to push on that duality of connections, we need to get better in speaking after with them".**

### What an acceptance is actually worth

An acceptance is permission, not interest. People accept connections freely because it costs nothing and risks nothing, so 4 out of 10 does not mean 4 people want to buy. Treating an accept as buying intent and pitching into it is the fastest way to waste it.

But it produces two assets, and the desk has only ever used one:

1. **A thread.** One conversation, and it decays in days.
2. **A subscriber.** They now see everything Jacopo posts, permanently, and that does not decay at all.

The second is the bigger prize and it pairs exactly with the weekly index post. **Every acceptance widens the distribution of the index, and the index is what produces inbound.** So an accept that never turns into a conversation is still a win, banked, as long as the index actually gets published. This is why acceptances compound and cold emails do not.

The practical consequence: **stop trying to convert the thread, and let the feed do the middle of the funnel.** The DM opens, the index post keeps him in front of them for weeks, and the ask comes when they have seen the benchmark three times and it is no longer a claim.

### The three rungs

**Rung 1 is the acceptance message, and it carries the model (Jacopo overrode the original design on 24 Aug 2026: "I really would like the message after the connection is accepted that we explain...").**

The first draft of this ladder held the commercial model back until they had engaged twice. He was right to move it forward, and the reasoning matters more than the change:

**What burns an acceptance is the ASK, not the mention of Tribe.** They accepted a connection from a man whose headline says Head of Talent Acquisition at Tribe. Nobody is surprised he sells. A message that explains what Tribe is and asks for nothing is a disclosure, and disclosure is disarming in a way that a soft-shoe approach is not. Holding it back reads as technique the moment they notice it.

It is also differentiated in the only place that counts. Almost every competitor opens with what they do ("we embed recruiters in scaling teams"). Opening with **how you charge** is rare, and it is a filter: people who want that arrangement answer, people who do not, do not, and both outcomes beat silence.

**THE SHAPE, SETTLED 24 AUGUST 2026 AFTER TWO ROUNDS OF JACOPO'S EDITS. Do not re-litigate it.**

He asked "is not too long the message itself?", was shown a 90-word cut, and chose the LONG version back with one addition: **it opens `Ciao [First name], thanks for accepting.` on its own line.** That greeting is the whole reason the length works, and the reason is mechanical. LinkedIn truncates the preview after roughly the first line. With the greeting on top, the visible line is a warm personal hello that costs nothing to read, which is what earns the tap on "see more". With a dense line of board numbers on top, the preview is a wall and gets scrolled past. **The greeting buys back the length. Never merge it into the paragraph below it, and never drop it to save words.**

So the message runs six short paragraphs and roughly 180 words, in this fixed order:

> Ciao [First name], thanks for accepting.
>
> [THE PRACTICE LINE: that he reads the job boards of 45 European scaleups every week, and why. Wording varied per person.] [THEN the observation from their board, scanned that morning, unique to them always. Around 55 words for the pair.]
>
> [A bridge line, VARIED per person, saying he would rather be plain than dance around it.]
>
> Tribe is a startup and we only work with scaleups. Most RPOs are built for enterprise hiring and priced that way, a big retainer that gets paid whether or not anyone joins. We do the opposite. A low fixed fee, then a fee on each hire we make.
>
> The fixed part is small on purpose. I have spent years making our recruiters genuinely good rather than merely available, so I would rather be paid when people start than paid for the attempt. It puts us on the same side of the problem as you, and it is the only version of this I have seen work at your stage.
>
> No ask attached. If it is the wrong shape, tell me and I will leave it.

**NEVER OPEN ON THE BARE FACT. Say how he knows it first (Jacopo, 24 Aug 2026: "I like more I'm monitoring the startups website bla bla bla and I noticed etc, like this is too direct").**

"Three roles went up on your board this morning" stated cold is a fact about a stranger's company with no explanation of where it came from, and that reads as surveillance. The same fact behind "I track the job boards of 45 European scaleups every week, mostly so I know how the market is moving instead of guessing at it" reads as a person with a systematic view of the market who happened to notice them.

**This is the index earning its keep inside the DM.** The practice line is the only place in the whole first message where Tribe's genuine advantage appears, and it appears as a credential rather than a pitch. It also makes the later "happy to send you the cut for your segment" land as an obvious next step instead of a bribe, because he has already told them the data exists.

**The practice line varies in wording every time.** It describes the same habit for every recipient, so sent identically it becomes the next "59 days" line. Two that worked on 24 Aug: "I track the job boards of 45 European scaleups every week, mostly so I know how the market is moving instead of guessing at it" and "Part of my week goes on reading the job boards of 45 European scaleups, which is how I keep an honest picture of the market rather than a guessed one." The habit is fixed. The sentence is not.

**Bridge into the observation, do not just append it.** "Sereact stood out this morning" and "Dash0 caught my eye for an odd reason" both hand over the fact as something noticed rather than something compiled. The second is stronger where the observation contains a contrast, because it promises the reader a small payoff.

**"Ciao" is his, not a translation error.** It is how he opens LinkedIn messages to people of every nationality and it has been in his sent invitations for months. Keep it in English-language messages to Germans, Danes and Swedes alike.

**The lesson from being wrong about this.** The 90-word cut was defended with a real mechanic (mobile truncation) and it still lost, because it treated word count as the variable when the variable was what sits in the truncated line. **Shorten the FIRST line, not the message.** A long message with a warm opening line outperforms a short message that opens on data, and no word count survives contact with that.

**"No ask attached" is load-bearing and must not be softened into an ask.** No Calendly, no "worth a chat?", no "happy to explore". The whole reason this message can carry pricing is that it demands nothing in return. The moment it asks, it becomes the cold email that got zero replies, only now on a channel where he was welcome.

**The two claims that get demonstrated rather than asserted.** Jacopo's own words are "the only RPO made for real scaleups" and a fixed fee that is "one of the lowest in the market". Both are true to him and both are unfalsifiable to a stranger, so the draft above converts them: the structural contrast (built for enterprise and priced that way, versus this) makes the exclusivity claim without stating it, and "small on purpose" plus the REASON beats a ranking, because a ranking invites a comparison while a reason invites a question. He has been offered the assertive versions and can swap them in on any send; do not swap them in unasked.

**The carve-out to the no-repeated-sentence ban.** The two model paragraphs ARE near-identical across recipients, necessarily, because they describe how the company charges and a price that changed per reader would be worse than a repeated one. **The ban applies to the observation and the bridge, which must be unique every time.** A recipient-specific opener in front of a shared model paragraph reads as a person explaining their business. A shared opener in front of anything reads as a mail merge.

**Rung 2, they answer, and this is where the discipline moves to.** The model is already out, so the reply to their first answer must NOT re-sell it. Answer what they actually asked, add one concrete thing that costs them nothing, and stop. Same day, inside the hour where possible, because a LinkedIn thread has a far shorter half-life than an inbox.

**Rung 3, the call, and only now.** It comes as a consequence of the model having been read and not argued with, never as the ask that carried it. "Easier to walk you through how the per-hire part works than to type it, fifteen minutes?" A call proposed after the model is a logistics question. A call proposed before it is a request for free time from a stranger.

### The live experiment, and how to know if it worked

**Everything above is a hypothesis until it has replies behind it. Do not let it harden into folklore.**

**What actually went out, 24 August 2026 at 14:22 Prague.** Ralf Gulde at Sereact and Mirko Novakovic at Dash0, both verified in the LinkedIn threads, both carrying the commercial model in the first message after an acceptance. On the Dash0 account the whole sequence ran cold to pricing in under four hours on a record nobody at Tribe had ever touched: transferred from an inactive owner that morning, email at 10:36, connect note at 13:00, accepted inside the hour, model at 14:22.

**The hypothesis under test, in one sentence.** That naming the price in the first message after an acceptance, while asking for nothing, produces replies where thirty-five pitched cold emails produced none.

**What would prove it wrong.** Silence on both. Or worse, a polite "thanks, we are covered" that a softer opener might not have triggered, which would mean the model closed the door rather than opened it.

**What would prove it right.** Any reply engaging with the STRUCTURE rather than the service. "How low is low", "what counts as a hire", "what happens if someone leaves in three months" are all buying questions dressed as arithmetic, and none of them can be asked of a message that never mentioned pricing.

**Read it on 7 September, not before, and not from one reply.** Two sends decide nothing. The honest read needs six or eight acceptance messages of this shape, which is roughly what the six pending invitations will produce if the acceptance rate holds. Until then it is the current best guess, not a finding.

**The comparison sitting right next to it, free.** Michael Blicher Soerensen and Fabian Riedel got the OLD shape on the same day: generic market median, an offer of a data cut, a question, no pricing. Same channel, same week, same sender. If the four threads diverge, that is the closest thing to a controlled read this desk will ever get without waiting a year for volume.

### When they do not answer

**No nudge on LinkedIn. Ever.** The email ladder carries the account, and one channel runs at a time. The connection is kept, they go on the index distribution, and the account waits for a better pretext than persistence: their next round, one of their roles crossing 90 or 180 days, or their own comment on an index post.

### Two bans, both earned on 24 August 2026

**No sentence may appear in two people's DMs.** The DMs to Michael Blicher Soerensen and Fabian Riedel both carried the identical clause "the median engineering role across the 45 European boards I track takes 59 days", in the same position. Two founders comparing notes see a mail merge. The market median may appear at most once per person and NEVER as the opening fact. **The opening fact always comes from their own board.**

**No inbound message waits.** Anything that arrives in the LinkedIn inbox gets an answer or a decision the same day, including messages that are not sales leads. On 24 August three sat unanswered, two of them for three days with LinkedIn itself prompting "Reply?": a recruiter networking, a candidate following up, and a former Nexi colleague asking whether Tribe had work for her. None were prospects and all three were reputational. The desk cannot claim to be good at the conversation after first contact while the inbox has a three-day queue in it.

## The follow-up lifecycle

Every send moves the account one rung down a fixed ladder, and closing a task ALWAYS creates its successor in the same motion. A closed task without a successor task ID in its body is the failure mode this section exists to prevent.

**Touch 1, the first email.** On confirmed send (verified in Sent, never from the plan): close the send task, rewrite its body with what actually went out (address, subject, variant, date, edits made), and create the touch-2 follow-up task 2 to 3 weeks out (2 in normal periods, 3 over summer and holidays). The touch-2 task carries the promised give (the index cut), the instruction to re-scan their board first, and "void if replied, close with outcome".

**Touch 2, the follow-up.** Same motion on send: close the task with the log, then create the touch-3 task 2 to 3 weeks after THIS send. Touch 3 is NOT a third email to the same person, the cadence rules forbid it: it is the route to a second name at the company, sent openly ("if this sits better with X, tell me and I will keep it with her"), or, when no second name makes sense, a PARK task with a dated reopen condition (a new funding round, a new stuck role crossing 90 days, a recruiter posting).

**Touch 3 and after.** The second person gets at most the same two-touch ladder. When both names have had their touches with no reply, the account is cold: park it with the reopen condition, close everything else on it, and say so in the report. No third names, no "one last try".

**A reply at any rung voids the ladder.** Close the pending follow-up task with the outcome and switch to the reply playbook in tribe-sales-desk, the reply is worth more than the next ten cold emails.

**Scheduling mechanics:** maximum 2 outbound tasks due per day, so batch follow-ups across consecutive days; every new task names the exact give it must carry (never "follow up"); and every closed task names its successor by task ID and date, so opening any closed task tells you where the account went next.

**The risk reversal rides in every first email and every follow-up:** "First shortlist within five days, before any contract is signed." It is Tribe's free trial, it costs nothing to say because the team can actually do it, and it converts a reply from a commitment into a no-risk yes.

**The call follows the email.** The day after a first touch lands, a 40 second phone call: "I sent you three profiles yesterday, did they land, are they the right shape?" Heads of Talent answer unknown numbers, it is their job, and no other recruiting firm in Europe calls. The task carrying the email names the phone number when enrichment found one.

**The content loop feeds the top.** The board data gathered for these emails (roles open 300+ days, recruiter searches for recruiters, TA hires posted in the wrong city) becomes a weekly anonymized LinkedIn post in Jacopo's voice. Prospects recognise themselves without being named, and the next cold email lands warm. Use the jacopo-linkedin-voice skill to write it.

**THE SHAPE OF A FIRST TOUCH IS SPECIFIED ONCE, IN THE VARIANT TEMPLATES ABOVE.** What follows in this section is the PROOF LIBRARY, the signature, the pricing and the language rules, all of which are current and none of which specify a shape. The three paragraphs that used to open this section described a fourth, pre-rewrite email shape (open on a fact, name the problem, then the model, close on coffee, 150 to 200 words) and they sat at the END of the file, which is exactly where a linear reader arrives last and believes what they read. They are gone. Two of their rules survive and are stated here properly, because they were never about shape:

**Open on something verifiable, never a compliment.** A board count, a round, a headcount trajectory, a post they wrote. This is beat 1 of A and the pivot of C, and it is the reason either works.

**Name something only a person who runs searches would notice.** Notice periods, local salary norms, req load per recruiter, the gap before a new TA hire starts. That sentence is where the credibility lives.

**Historic note, kept for the proof rules that follow.** The old opening beat read:

**Open with something specific and verifiable about them.** A job board count, a funding round, a headcount trajectory, a post they wrote. Not a compliment, a fact. "PORTA plus 30,000 customers is a strong year. Your job board shows the cost of it: 19 open roles, 14 of them go-to-market."

**Name the hiring problem that follows from that fact.** This is where the credibility lives. It should be something only someone who runs searches would notice. Notice periods, local salary norms, req load per recruiter, the gap before a new TA hire starts.

**Then the model, in his words:**
> We place a recruiter directly inside your team. We don't send CVs. They work in your ATS, report to you, and own each search from sourcing to signed offer.

**Proof, matched to the ROLES they have open first, city second.** This is the rule that overrides everything else about proof, and Jacopo has enforced it twice: tech client names for tech jobs, commercial names for commercial jobs. Read their board before picking the names.

- **Engineering and tech roles open** → "the deep engineering teams at Zalando, Spotify and Kayak as they scaled". MOST RECOGNIZABLE NAMES ONLY, Jacopo's rule from 20 August: never lead with Upvest or any lesser-known client, a founder should recognize every name in the proof line instantly. The frame is scale and efficiency, so the proof paragraph closes with the one-line efficiency proof: "Across our clients: 4,300+ hires at an average cost per hire of 3,300 euros." (This overrides the earlier no-numbers note for engineering and founder emails; keep it to that single line.)
- **Sales, GTM, RevOps, operations roles open** → Wolt's commercial and operations teams across CEE, Germany and the Nordics, Glovo's commercial org in Italy. Nexi for fintech and Italy.
- **Recruiter and TA roles open** → the 4,300+ hires at €3,300 average IS the proof, plus whichever client name matches what those recruiters would be hiring.
- **Mixed board** → match the roles the EMAIL is about, since that is what the reader checks the claim against.

The failure this rule exists to prevent: on 18 August a commercial-roles email to Choco went out carrying "Zalando, Kayak and Spotify", tech names against an all-GTM board. A Head of Sales reads that and concludes we do engineers, not sellers. City localisation stays (a Berlin founder reads Berlin names as neighbours), but role match comes first when the two conflict.

**A real search story beats a client name list.** Where the library below has a story matching their open roles, use it as the hook instead of bare names, because "we ran exactly this search" is the thing a name list only implies. Verified stories, safe to use:

- **Nexi, August 2026**: placed a Talent Acquisition Partner covering the German and Polish markets into Nexi's TA team, deal to signed onboarding documents inside three weeks. Use for: TA and recruiter searches, fintech, multi-market roles.
- **Upvest, Berlin**: built their tech team from inside their ATS, engineer by engineer. Use for: supporting detail on a call or in a follow-up ONLY, never as a name in a cold email proof line (Jacopo, 20 Aug: recognizable names only, nobody knows Upvest).
- **Wolt**: commercial and operations teams stood up across CEE, Germany and the Nordics as they entered new markets. Use for: GTM builds, market entries, ops scaling.
- **Glovo, Italy**: commercial org. Use for: southern Europe GTM.

**Never invent the specifics of a search.** No made-up time-to-fill, no invented candidate counts, no "filled in four weeks" unless the number is in this library or Jacopo supplied it. A fabricated specific in a sales email is worse than a bare name, because the prospect asks about it on the call. When a good story is missing for a segment, ask Jacopo for the real one and add it here, that is how this library grows.

**The coffee line is retired from first touches (24 Aug rewrite, restated here 25 Aug because this copy outlived the decision).** "I'm always happy to connect with other entrepreneurs in [their city], even if not for collaborations, just for a coffee chat" was the third ask in a three-ask email. It survives in exactly two places: inside variant B, where it is part of the text Jacopo actually sent and where it is the only ask that is not a time-ask, and in follow-ups after a reply. Never in A, never in C.

**Pricing, plainly.** 4K a month fixed, plus 2K per person hired. No percentage fees. No lock-ins. Being open about price this early is deliberate and it is part of the brand.

**The close, one rule for every variant.** ONE question they can answer in a line, and no time-ask. "Worth 15 minutes?" was pulled on 18 August and the coffee close on 24 August. For a CEO written to cold the question doubles as routing ("is this sitting with you, or is there someone I should be talking to?"), which surfaces the right owner without a second cold thread. For Heads of People it is the soft concrete one ("would it help to have Bordeaux carried while your two searches run?"). Never a paragraph of next steps.

**Sign:** `Best, Jacopo` in English, `Un saluto, Jacopo` in Italian, ALWAYS followed by his Tribe signature block. Drafts created through the Gmail API do not get his Gmail auto-signature (Gmail only appends it in the UI compose window, and not to existing drafts), so every draft must carry it explicitly, in the htmlBody so it renders. The block, copied from his real sent mail: "Jacopo Lupo Ferrari" (grey Verdana 9pt), "Head of Delivery @ Tribe.xyz" linking https://tribe.xyz/, "Book a meeting with me!" linking the Google Calendar appointment schedule https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ0ucyiz8Z7z9UGvfNyNXeEh6YJjDHs8Dk02uscgg0swol9OVf5cpWu8u9tSpWTLPU5_AvajhK3y (Jacopo moved off Calendly on 25 Aug 2026, the old link must not appear in a new draft), then the Tribe logo, which Jacopo pastes in manually before sending (remote image URLs do not render reliably in API-created drafts, so the drafts carry the text part of the signature and he adds the logo himself). A draft without the signature was how the 20 Aug JUPUS email went out, do not repeat it.

**Length is set per variant in the templates above** (A around 80 words, C around 75, B longer because its structure is Jacopo's own), and the preflight gate checks it. The 150 to 200 words that used to sit here belonged to the retired shape and contradicted the rewrite by a factor of two.

### Language

He is Italian, based in Prague, writes fluent English. Write in Italian to Italian recipients, it lands differently and it is a real differentiator in a market where everyone else sends English. He has sent Italian emails to Satispay and Bending Spoons and they read noticeably warmer.

For French, German or Dutch recipients, English unless he says otherwise.

### Hard rules on style

**No em dashes anywhere.** This is a standing personal preference, not a stylistic suggestion. Use a period, a comma, a colon, or parentheses.

**No tricolons of abstract nouns**, no rhetorical closing questions, no arrows, no "Here's what I've learned:" framings.

### The five banned sentence shapes

These are the shapes that make a cold email read as written by a machine or by a LinkedIn growth account. A prospect who reads one of them stops reading. Never use them, in any email, in any language, including in a follow-up. If a draft contains one, delete the sentence and write the plain fact instead.

**1. "That's not X. That's Y."**
The reframe. Rejecting one description to sound insightful about a second one.
Bad: "That's not a hiring problem. That's a capacity problem."
Fix: delete the rejected half and state the claim. "Two recruiters are carrying 19 reqs."
The ban covers every variant of the shape, including softer ones: "not just X, but Y", "less X, more Y", "the real issue isn't X, it's Y", "it was never about X". It also applies across a sentence boundary, which is how it usually sneaks in.

**2. "In a world where [scary change], [virtue] becomes [advantage]."**
Invented context, then a vague pay-off. It says nothing about the prospect.
Bad: "In a world where every AI lab is fishing in the same pool, speed becomes the differentiator."
Fix: name the specific thing that is true about them. "Your Staff ML role has been open since March. Anthropic and Mistral posted the same title in Paris in June."

**3. "Most people [lazy thing]. The few who win [disciplined thing]."**
The double-most contrarian opener. It tells the reader they are probably in the lazy group, which is a strange way to open a first email to a stranger.
Bad: "Most founders hire a recruiter too late. The ones who scale hire before they need to."
Fix: cut the judgement, keep the observation, attach it to them. "Your first People hire starts in September. The 14 GTM roles are open now."

**4. "Here's the truth: [obvious statement]."**
Announcing a revelation and then delivering something everyone already knows. Also covers "the reality is", "let's be honest", "the hard truth".
Bad: "Here's the truth: hiring senior engineers in Berlin is hard."
Fix: say the specific thing, or say nothing. "Two of the five Berlin engineering roles have been live since October."

**5. "If you're not doing [X], you're already behind."**
Manufactured urgency and a threat. It is the fastest way to get a cold email deleted by a senior person, because they can tell it would have been sent to anyone.
Bad: "If you're not building your talent pipeline now, you're already behind."
Fix: state the consequence with real numbers and let them draw the conclusion. "A November start means notice periods land the hire in Q1."

The test for all five: could this sentence have been sent to 500 other companies without changing a word? If yes, cut it. What earns the reply is the fact only someone who read their job board would know.

**Avoid the corporate register:** align, leverage, journey, ecosystem, landscape, unpack, at the end of the day.

Prefer a concrete scene to an abstraction. "The hiring manager and the recruiter want different things and neither has said so out loud" beats "stakeholder misalignment" every time.

### When there is an objection in public

If the prospect or their founder has publicly said something that cuts against the pitch, write around it openly rather than ignoring it. Peec AI's founder posted "no recruiters" on a hiring post. The email that worked opened by naming that, conceding the point about that specific role, and pivoting to what comes after it. Pretending not to have seen it reads worse than addressing it.

## Creating the tasks

Every email becomes a dated HubSpot task associated with the contact, and **the task body carries the entire draft**. The point is that on the day, he opens the task and sends. He should never have to come back to a chat transcript to find the words.

Each task body should contain:
- The subject line and the full email text
- Whether the address is verified or not
- Any decision he has to make first, stated as a check rather than a suggestion. "CHECK FIRST: Grégory Leyne contacted 10 July, no reply. Decide if this is deliberate multi-threading."
- Who the backup contact is at that company

Spacing: two per day at most, and check what is already on his calendar before scheduling. Piling nine tasks onto one morning guarantees they get bulk-snoozed.

Set `hs_lead_status` to `ATTEMPTED_TO_CONTACT` on anyone he has emailed, so the CRM reflects reality without him touching it.

## Follow-ups

A follow-up must add something the first email did not say. "Bumping this" wastes the second contact.

Angles that have worked: a timing consequence he did not raise (notice periods pushing a start into Q4), a cost figure with a source (Kienbaum puts a leadership mis-hire at 1.5x to 3x salary), or a piece of news since the first email.

Give an easy out. "If this sits better with Victoria, tell me and I will keep it with her." It gets replies from people who would otherwise ignore it, and it routes you to the right person.

**Track what you promised.** If a follow-up said "I'll write once and then leave you alone", do not schedule a third. Put a routing check instead: if no reply by date X, switch to the other contact at that company rather than chasing this one.

## What you cannot do, and should say so

Jacopo's HubSpot connection is read-mostly for some objects. Do not promise these:

- **Sending email.** Neither HubSpot nor the Gmail connector can send. Gmail can create drafts, and Gmail requires a recipient, so use `jacopo@tribe.xyz` as a placeholder rather than a guessed prospect address, and open the body with a bracketed line naming the real recipient. **Every draft, placeholder or not, carries `146748263@bcc.eu1.hubspot.com` in the BCC field already**, exactly that string, checked character for character, because a mistyped BCC means the send never reaches HubSpot and the CRM goes blind on the thread. The only edit at send time is the To field.
- **Open tracking is NOT the BCC.** The BCC logs the email onto the contact record, nothing more. Whether the prospect OPENED it comes from the HubSpot Sales extension in Gmail, which injects the tracking pixel at send time when the Track box is ticked in the compose window. A draft created here cannot carry that pixel. So the send routine for tracked opens is: open the draft in Gmail, confirm the Track checkbox is on (HubSpot Sales extension), then send. If Track was off, the activity still logs via BCC but opens show nothing, which reads as "not opened" and is really "not tracked". Never report open data on an email without confirming it was sent tracked.
- **Writing HubSpot notes is a RULE, not a restriction (corrected 25 Aug 2026).** The portal grants note read and write. What happened is that Jacopo banned them on 24 August ("don't add anymore notes is creating a mess in every people hubspot") because 182 notes landed on contact records in a day. So: notes are not written, and notes ARE read, because another agent on this portal records its work in them and that is how an account gets screened. Calling this a permission limit is what stopped anyone reading them, which is how Upvest was prepped for a send while a colleague's agent was working it.
- **Merging records.** Companies and contacts both, UI only. Hand over record IDs and which to keep.
- **Deleting records.** No delete tool, and deleting CRM data is his call regardless.

Say what you cannot do at the moment it becomes relevant, not after he has waited for it.

## Reporting back

Give him the emails in the chat, not as a file, unless he asks for a file. He works from the thread.

Structure: the drafts first, grouped by company, then a short list of decisions that are actually his. Flag the things he cannot see from where he sits: an existing thread at the same company, a contact who has changed jobs, an address that is a guess, a public objection.

Be specific about what is uncertain. "Address unverified" on every guessed address, every time, is more useful than a general disclaimer at the end.
