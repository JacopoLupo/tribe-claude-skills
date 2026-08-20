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

## The Lead Engine: one intake for cold and warm

Added 20 August 2026, Jacopo's design: every prospect enters through ONE pipeline with two feeds, and which feed they came through decides their opener. Trigger phrases: "run the lead engine", "fresh leads", "harvest".

**Feed 1, market signals (COLD).** Funding rounds announced that week, plus index scan anomalies: roles crossing 90 days, reposted roles, a hiring wave after a raise, a recruiter role appearing. These flow straight to the outreach queue and get variant A or B, alternating, counted in the A/B test.

**Feed 2, the commenting radar (WARM).** The linkedin-engagement-radar skill surfaces EU people from the ICP who posted in the last 4 weeks. Jacopo comments on 2 to 3 posts a day. EVERY comment gets logged the same day as a HubSpot task on that contact: subject "WARMING: [name]", body naming the post topic, the comment date, and the outreach-ready date. The window: outreach goes out 3 TO 7 DAYS after the comment, sooner if the person replied or reacted to it. Past 10 days the warmth is spent and the lead falls back to the cold lane.

**Both feeds merge Monday.** One harvest list, deduped against HubSpot, Tribester-owned accounts parked, each lead tagged COLD or WARM in its task. Then the standard machine below runs on all of them: CRM checks, board scan, verified address, draft, task, ladder.

**The two hard rules that make the engine work:**

1. **Never cold-email someone mid-warm-up.** Before drafting ANY first touch, check the contact for an open WARMING task. If one exists, the email waits for the window and uses variant W. A cold index email landing two days after a friendly comment burns both.
2. **A warm lead gets VARIANT W, not A or B**, and variant W is EXCLUDED from the A/B scoreboard (different population, warm openers always outperform, counting them would corrupt the test). Tag tasks "VARIANT W".

**Variant W, the warm opener.** First line references the exchange, second line goes straight to their board, then the standard skeleton (solvable line, role-matched proof, five-day shortlist, index cut give, coffee close):

> Hi [name], good exchange under your post on [topic] the other day.
>
> It got me looking at [company]'s board: your [role] has been open [X] days, and the median [category] role across the 40 scaleup boards I track closes in [Y].
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

**If another Tribester owns the company or any contact on it, stop.** This is a hard rule, not a judgement call. Check `hubspot_owner_id` on the company and on every associated contact, and check `notes_last_contacted`. If someone else's ID is on it, the account is theirs. Park it, tell Jacopo whose it is and when they last touched it, and keep the research in case they want it. Two Tribesters landing in the same inbox is worse than not writing at all, and the prospect will notice before we do. On 11 August this rule removed Moss, Neko Health, NavVis, Quantum Systems and Dwelly from a batch of otherwise good leads, all inside one search.

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

**The first touch leads with the Tribe Board Index, data nobody else has.** Candidate-profile teasers were tried by Martin and did not convert, so the primary hook is the index instead: a weekly scan of ~40 European scaleup job boards via the Ashby posting API. THE SCAN IS BUNDLED: run `python3 scripts/index.py` from this skill's directory before every batch (add a company slug to also dump that board's roles, `--probe N` for a specific age's percentile). The slug universe lives at the top of that script; add new boards there and note the change here, so week-over-week numbers stay comparable. Never rebuild the scan from memory. On 18 August 2026 the index held 1,613 live roles, median age 46 days, engineering median 57, sales median 36, TA median 41, with 27% of all roles past 90 days, 9% past 180, and 30 roles past 300. The email states the prospect's number against the market: "Your AE role is at 140 days, older than 87 percent of the 1,613 roles I track." Nobody else can send that sentence, it is verifiable, and it makes the sender the person with the data rather than the person with the pitch. Offer the relevant index cut ("the Dutch robotics cut", "the German-speaking SaaS sales cut") as the give, it earns a reply that costs the prospect nothing. REFRESH THE NUMBERS before each batch, stale index numbers are worse than none, and never quote a percentile that was not computed from a real scan.

**The five-beat structure.** Adopted 19 August 2026 from a cold email Jacopo flagged (203K views on X, the recipient called it the best pitch he got all year). The beats, in order, none skipped and none reordered:

1. **The opener, always this exact shape, Jacopo's final call on 19 August**: "This week I checked [company] against the 40 European scaleup job boards I track, [total] open roles in total. The median [their role category] role closes in [X] days." The company name sits in the first sentence, and the median quoted is THEIR role category (engineering 57, sales 36, TA 41 on the 18 Aug scan), never the overall median. Do not swap in portfolio phrasings like "out of all the boards and clients we track", that variant was tried on 19 August and Jacopo overruled it the same day. This opener, all the time.
2. **The result, stated flat**: their number against the market, no adjectives. "Your two autonomy roles are at 242 days. The median across the index is 46." The gap does the selling.
3. **"That's solvable, and it's exactly what we did for X, Y, Z"**: one sentence that turns the bad news into a fixed problem, with role-matched client names as the proof (proof rules below apply in full). This beat is why the email reads as help rather than criticism, do not soften the result in beat 2 to compensate, the rescue only works if the gap was stated plainly.
4. **The artifact, offered before any commitment**: a concrete piece of work they get whether or not they ever pay. The relevant index cut, or the first shortlist inside five days before any contract. Named specifically ("the Dutch robotics cut", "three profiles by Friday"), never "some insights".
5. **The close per the close rules below**: coffee line for founders, one soft concrete question for Heads of People. If a call is already booked or offered, beat 4 lands "ahead of our call", which gives the meeting a reason to exist before it starts.

**THE TWO EMAILS. Locked by Jacopo on 19 August 2026: every first-touch cold email is variant A or variant B, nothing else.**

**VARIANT A, the index email.** The JUPUS send is the canonical text. Structure, fixed: the "This week I checked [company]" opener with the category median, the flat gap with a short verified board punch ("Twelve roles, no recruiter among them"), the solvable line with role-matched proof, first shortlist within five days, the index-cut give, the coffee close. Slot template below.

**VARIANT B, the Claude candor email.** Jacopo's design, and the canonical text below is the version HE ACTUALLY SENT on 20 August (Alan, Corti, Medly), which supersedes every earlier draft. His final edits: the competitor-names line ("It surfaced Talentful, Join Talent and Chapter 2") is CUT, so "Tribe was nowhere in the results" lands directly after the test and the email never hands the prospect a shopping list. Subject is "Tribe / [category] comparison" with the category matched to the reader ("Tribe / Embedded comparison", "Tribe / RPO comparison"), never a competitor name in the subject. The walk-through question is role-matched: "how it worked at Zalando?" for an engineering-heavy prospect, "at Wolt?" for GTM or general. SPACING RULE: each opening sentence on its own line with a blank line between. As sent:

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

Rules for B: RUN THE PROMPT IN CLAUDE ONCE BEFORE EACH BATCH, if Tribe appears in the results the email is dead and the fact changes; [company] slots must never be wrong; and the opening block is identical across sends, so never use it twice in overlapping networks (two Berlin founders who know each other get different emails). OPEN QUESTION for Jacopo: the 20 Aug sends said "across five markets" (Alan) and "across 25 markets" (Medly) for Wolt, confirm the real number and standardize, a prospect who asks on a call must get the same answer the email gave.

(Parked for after the test, not to be used while it runs: diagnostic, weekly-scan-callout, 300 Club and competitor-pool openers.)

### The A/B test, started 19 August 2026

**Variant A** is the index email. **Variant B** is the Claude candor email. Rules until the test is called:

- Alternate variants across new prospects, half the batch each, founder recipients only for B.
- Tag every send in its HubSpot task body: "VARIANT A" or "VARIANT B". No untagged sends.
- Everything downstream stays identical (follow-up cadence, day-after call, BCC logging), so the only difference measured is the email itself.
- The metric is replies within 14 days of send. Opens need the HubSpot extension Track box ticked at send, so tick it on every A/B send.
- Call the test at 10 sends per arm or end of September, whichever comes first. Until then neither variant changes, an edited variant restarts its count.
- **The scoreboard, every daily run:** count sends per variant from the "VARIANT A/B" tags in HubSpot task subjects and bodies, count replies per variant from the inbox reconciliation, and report the standing in one line ("A: 3 sends 1 reply, B: 3 sends 0 replies"). The tally lives in the tags and the inbox, nowhere else, so it can always be recomputed from scratch. When the call date arrives, the verdict gets written into this file: winner, numbers, and what replaces the loser.

The variant A slot template:

> Hi [first name],
>
> This week I checked [company] against the 40 European scaleup job boards I track, [total] open roles in total. The median [their role category] role closes in [category median] days.
>
> Your [their stuck roles] are at [their days], older than [computed share] of [category] roles in that index, and [competing roles or second board fact]. [Short punch, verified from the board: "Twelve roles, no recruiter among them." / "All four compete for the same Paris fullstack pool."]
>
> That is a solvable problem, and it is the [same/exact] work we did [role-matched proof story, per the proof rules below]: a recruiter placed inside your team, working in your ATS, reporting to you, owning each search from sourcing to signed offer. First shortlist within five days, before any contract is signed.
>
> Happy to send you the index cut for [their segment], it is a useful benchmark either way.
>
> I'm always happy to connect with other founders building in [their city], even if not for collaborations, just for a coffee chat.
>
> Best,
> Jacopo

The canonical reference is JUPUS (sales, 36d median, Wolt five-markets proof, drafted 19 August): Jacopo picked it over the heavier variants, so match its weight. Paragraph two ends on a short verified punch from their board. Paragraph three carries no pricing, but for engineering and founder emails it closes with the one-line efficiency proof ("Across our clients: 4,300+ hires at an average cost per hire of 3,300 euros"), Jacopo restored it on 20 August as the scale-and-efficiency push. For TA and recruiter roles those numbers ARE the main proof. Every slot is filled from a real scan run that week, never from memory. For Heads of People, swap the coffee line for the soft concrete question per the close rules, everything else holds.

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

Jacopo's real emails are the specification. The shape:

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

**Close with the coffee line when writing to a founder or CEO.** After the ask, add: "I'm always happy to connect with other entrepreneurs in [their city], even if not for collaborations, just for a coffee chat." Localise the city. It gives a founder a reply path that is not a sales yes, and it is true, which is why it works. Skip it for Heads of People, where it reads as odd, and skip it in follow-ups only if it was already in the first email.

**Pricing, plainly.** 4K a month fixed, plus 2K per person hired. No percentage fees. No lock-ins. Being open about price this early is deliberate and it is part of the brand.

**The close.** "Worth 15 minutes?" is retired, Jacopo pulled it explicitly on 18 August. For founders and CEOs the coffee-chat line IS the close, no time-ask before it, at most one routing question earlier in the email if it earns its place. For Heads of People, where the coffee line is skipped, close with one soft concrete question ("Would it help to have Bordeaux carried while your two searches run?"), never a time-ask and never a paragraph of next steps.

**Sign:** `Best, Jacopo` in English, `Un saluto, Jacopo` in Italian, ALWAYS followed by his Tribe signature block. Drafts created through the Gmail API do not get his Gmail auto-signature (Gmail only appends it in the UI compose window, and not to existing drafts), so every draft must carry it explicitly, in the htmlBody so it renders. The block, copied from his real sent mail: "Jacopo Lupo Ferrari" (grey Verdana 9pt), "Head of Delivery @ Tribe.xyz" linking https://tribe.xyz/, "Book a meeting with me!" linking https://calendly.com/jacopo-ferrari/30min, then the Tribe logo, which Jacopo pastes in manually before sending (remote image URLs do not render reliably in API-created drafts, so the drafts carry the text part of the signature and he adds the logo himself). A draft without the signature was how the 20 Aug JUPUS email went out, do not repeat it.

Length: 150 to 200 words. His best ones are short.

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
- **Logging emails or writing notes.** Both restricted.
- **Merging records.** Companies and contacts both, UI only. Hand over record IDs and which to keep.
- **Deleting records.** No delete tool, and deleting CRM data is his call regardless.

Say what you cannot do at the moment it becomes relevant, not after he has waited for it.

## Reporting back

Give him the emails in the chat, not as a file, unless he asks for a file. He works from the thread.

Structure: the drafts first, grouped by company, then a short list of decisions that are actually his. Flag the things he cannot see from where he sits: an existing thread at the same company, a contact who has changed jobs, an address that is a guess, a public objection.

Be specific about what is uncertain. "Address unverified" on every guessed address, every time, is more useful than a general disclaimer at the end.
