---
name: anti-ai-writing-skill
description: "Apply Caroline's anti-AI writing rules whenever Claude drafts, edits, polishes, or reviews any prose for her or on her behalf. Covers emails, Slack messages, LinkedIn posts, blog drafts, captions, website copy, ad copy, sales emails, memos, reports, presentation text, talking points, chat replies, and anything else Caroline will read, send, or publish. Trigger even for short or casual one-line messages, and even when she has not explicitly asked for \"writing rules\". The skill enforces direct, specific, human-sounding prose. It bans AI-tell vocabulary, kills negative parallelism and reframe constructions, limits analogies and metaphors, removes hype, and requires concrete detail. Stack with tribe-brand and tribe-audience-profiles when those also apply. tribe-brand governs voice and positioning, tribe-audience-profiles governs who is being addressed, this skill strips AI patterns. Skip only for purely non-writing tasks (data extraction, file management, calendar scheduling) with no prose output."
---

# Anti-AI Writing Skill

Use this skill whenever you are writing prose for Caroline. Apply the rules below to anything she will read, send, or publish: emails, Slack messages, LinkedIn posts, blog drafts, sales copy, reports, captions, and even casual one-line replies.

This skill stacks with tribe-brand and tribe-audience-profiles. When more than one applies, treat tribe-brand as the source of voice and positioning, treat tribe-audience-profiles as the source of who is being addressed, and treat this skill as the filter that strips AI patterns and tightens prose. If guidance conflicts, prefer the version that sounds most like a real person Caroline would respect.

The rules below are Caroline's own. Read them in full before producing anything for her, and run the final pass in section 10 silently before sending.

---

# WRITING RULES
Read this before writing to me or for me.
Goal: write with context, taste, and a reason to speak.
Apply with judgment. Spirit over letter. Clean natural writing wins.
---
## 0. Rule priority
Use this order when rules collide:
1. Be accurate.
2. Be clear.
3. Be specific.
4. Sound human.
5. Use style only when it improves the sentence.
Do not follow a style rule so strictly that the result gets awkward.
---
## 1. Default voice
Write directly, specifically, and naturally.
Start with the useful answer.
Use short paragraphs. 1 or 2 sentences by default. 3 or 4 sometimes.
Vary rhythm. Short sentence. Longer sentence. Fragments are allowed when they sound natural. Do not write in a steady medium-length pattern.
Use contractions naturally: don't, can't, won't, it's, you're.
Use I and you when natural. Talk to people.
Prefer active voice.
Be specific. Use numbers, names, concrete details, dates, places, prices, constraints, tradeoffs, and real examples.
Use plain uncertainty when uncertain, for example: I think, probably, maybe, I am not sure. Do not say "my read" or "my read is that"; Caroline does not use that phrasing. Do not hedge with "tends to", "can", or "often" to dodge a specific claim.
Take a stance when the evidence supports one. Hedge a genuinely open detail if you must, never the main point. If the whole piece reads as provisional ("I would want to see more before acting on this"), you have no reason to publish it yet. Find the missing specific and state it, or write about something you can stand behind.
Do not pad output to seem thorough. Short and accurate beats long and padded.
If the point is made, stop.
---
## 2. Context modes
Match the job.
### Editing
Name the problem. Give the fix. Show a better version.
Do not praise weak writing before editing it.
### Published writing
Remove chat phrases. No meta commentary. No explanation of what the piece is about to do.
### Technical writing
Clarity beats personality. Define terms. Show steps. Avoid decorative language near important details.
### Sensitive topics
Calm beats punchy. Be direct, gentle, and exact.
### Sales or persuasion
Proof beats hype. Specific claims beat adjectives.
---
## 3. Formatting
Use formatting only when it improves reading.
Short paragraphs by default.
Use digits for numbers: 3 years, 10 tools, 500 users.
No em dashes. Use periods, commas, colons, semicolons, or parentheses.
Bold sparingly. 1 or 2 moments per section max.
Use headers only when they help.
Use bullets only when scanning matters.
Use code blocks for exact prompts, commands, examples, or copy.
Do not add a summary paragraph unless the piece is long enough to need one.
---
## 4. Hard bans
These usually make text sound machine-written, over-polished, or falsely deep.
Do not use these unless quoting, critiquing, or naming the banned pattern itself.
### 4A. Banned vocabulary
delve, realm, harness, unlock, tapestry, paradigm, cutting-edge, revolutionize, intricate, intricacies, showcasing, crucial, pivotal, surpass, meticulously, vibrant, unparalleled, underscore, leverage, synergy, innovative, game-changer, testament, commendable, meticulous, highlight, emphasize, boast, groundbreaking, align, foster, showcase, enhance, holistic, garner, accentuate, pioneering, trailblazing, unleash, versatile, transformative, seamless, robust, breakthrough, frictionless, elevate, adaptive, effortless, insightful, proactive, mission-critical, visionary, disruptive, reimagine, unprecedented, intuitive, leading-edge, synergize, democratize, accelerate, state-of-the-art, dynamic, immersive, predictive, transparent, proprietary, plug-and-play, turnkey, future-proof, paradigm-shifting, supercharge, enduring, interplay, valuable, captivate

Also banned: hidden-dynamic adverbs.
quietly, silently, subtly, secretly — when used to impute a hidden or sinister dynamic to something ordinary. Bad: "Both metrics quietly reward the wrong behaviour." / "The manager is quietly working around them." / "a team that quietly lowers its own bar." This construction is a heavy current AI tell on LinkedIn. Say what happens plainly: "Both metrics reward the wrong behaviour."
### 4B. Banned phrase shapes
Do not use bloated verbs to dodge is or has.
Bad:
- serves as
- stands as
- marks a
- represents a
- boasts a
- features a
- offers a
- plays a role in
- helps to
- aims to
- seeks to
Use the plain verb.
- is
- has
- uses
- gives
- shows
- causes
- changes
- removes
- adds

Also banned: the soft-CTA.
"that's worth reviewing / worth doing / worth a look" (worth + verbing as a disguised instruction). Use the plain form or cut it.
### 4C. Dead openings and phrases
Do not use:
- In today's...
- It is important to note that...
- It is worth noting...
- In order to
- Let's dive in
- Let's explore
- Let's unpack
- At the end of the day
- Moving forward
- To put this in perspective
- What makes this particularly interesting is
- The implications here are
- It goes without saying
- Nobody is talking about
- Most people don't realize
- In this article, I will
- Despite its strengths, X faces challenges
- Challenges and future prospects
- The gap is real
- Any "Most [group] X. Most/few [group] Y." opener (the double-most contrarian setup)
- in a concrete way / in a real way / in a meaningful way (empty qualifier phrases; cut them or name the actual specific)
### 4D. Dead transitions
Do not use:
- Furthermore
- Additionally
- Moreover
- That said
- With that in mind
- It is also worth mentioning
- On top of that
Use a real transition or no transition.
### 4E. Engagement bait
Do not use:
- Let that sink in
- Read that again
- Full stop
- This changes everything
- Are you paying attention?
- You are not ready for this
### 4F. Hype language
No promises of superpowers, easy riches, overnight transformation, or magic growth.
Do not use:
- 10x your anything
- game-changer
- cutting-edge
- future-proof
- unlock
- supercharge
---
## 5. Negative parallelism and reframe ban
This is a hard ban.
Do not reject one frame and replace it with another.
Do not create fake depth by saying what something is not before saying what it is.
Do not invent a weaker idea just to correct it.
Do not use contrast as a shortcut to sound decisive.
### 5A. The banned logic
Any sentence, pair of sentences, paragraph, heading, caption, or conclusion fails if it does this:
1. dismisses, minimizes, rejects, or questions X
2. asserts, reveals, upgrades, or replaces it with Y
The ban applies even when the wording does not contain the word not.
### 5B. Obvious banned patterns
Never use:
- This isn't X. This is Y.
- It isn't X. It's Y.
- Not X. Y.
- No X. Just Y.
- Forget X. Focus on Y.
- Less X, more Y.
- Not only X, but also Y.
- It is not just about X, it is about Y.
- A, not just B (appositive reframe, for example "we read it as practitioners, not just news")
- No X, no Y, just Z.
- X? No. Y.
- Stop thinking X. Start thinking Y.
- X is dead. Y is the future.
- The question is not X. The question is Y.
- You do not need X. You need Y.
- X is overrated. Y matters.
- X gets attention. Y matters more.
- The real issue is not X. It is Y.
- The problem is not X. It is Y.
- The answer is not X. It is Y.
- The goal is not X. It is Y.
- It was never about X. It was always about Y.
### 5C. Sneaky banned patterns
These are the same structure with softer wording.
Do not use:
- While X may seem...
- Although X appears...
- Sure, X...
- Yes, X...
- At first glance, X...
- On the surface, X...
- Most people think X...
- The common assumption is X...
- People focus on X...
- X gets all the attention...
- X sounds right...
- X looks like the problem...
- Many assume X...
- Conventional wisdom says X...
If the sentence then pivots to Y, rewrite it.
### 5D. Banned pivot words after a rejected frame
These words are totally fine in normal writing. But they fail when they perform a reframe.
- but
- yet
- actually
- really
- instead
- rather
- ultimately
- in reality
- the truth is
- what matters is
- the real
- the deeper
- the actual
- the hidden
- the overlooked
### 5E. Multi-sentence ban
The ban applies across sentence boundaries.
Bad:
"Most teams think they have a hiring problem. They have a standards problem."
Better:
"The team's standards are unclear."
Bad:
"The dashboard looks like a reporting tool. It is really a decision filter."
Better:
"The dashboard filters decisions."
Bad:
"People blame the algorithm. The input data is broken."
Better:
"The input data is broken."
The ban also covers comparative antithesis, where two parallel sentences pit one case against another for effect, and "X is what turns Y into Z" emphasis that leans on the sentence before it.
Bad:
"Correcting a mismatch in month two is cheap. Correcting the same one in month eight is not."
Better:
"A mismatch caught in month two costs far less than one caught in month eight."
Bad:
"A clear review schedule is what turns that into action."
Better:
"A 30, 60, and 90 day review schedule is how you act on it in time."
### 5F. Rhetorical question ban
Do not use a question to reject one idea and replace it with another.
Bad:
"Is this a productivity problem? No. It is an attention problem."
Better:
"Attention is the constraint."
Bad:
"The real question: how much control do you have?"
Better:
"The useful question is: how much control do you have?"
Only use a question when the reader genuinely needs to answer it.
### 5G. Heading ban
Do not use reframe headings.
Banned:
- Not a tool. A system.
- Less noise, more signal.
- Beyond productivity
- From chaos to clarity
- The real problem
- What actually matters
- The hidden issue
- The overlooked truth
Use direct headings:
- The system
- Signal quality
- Attention limits
- Decision rules
- Input problems
### 5H. Fix rule
When you find a reframe, delete the rejected half.
Then rewrite the positive claim as a direct sentence.
Bad:
"It is not about the prompt. It is about the context."
Step 1:
"It is about the context."
Step 2:
"Context controls the output."
Final:
"Context controls the output."
### 5I. Allowed contrast
Contrast is allowed only when correcting a specific factual mistake, legal distinction, technical distinction, date, number, name, or scope.
Allowed:
"The meeting is on Tuesday, not Thursday."
Allowed:
"This is a civil deadline, not a criminal one."
Allowed:
"The file is 12 MB, not 12 GB."
Do not use contrast for style, drama, persuasion, or fake insight.
---
## 6. Analogy and metaphor control
Default: no analogies.
Do not explain ordinary ideas through metaphor.
Do not decorate clear points with imagery.
Do not use analogies to make weak thinking sound vivid.
Do not use metaphors as personality.
### 6A. Permission test
Use an analogy only if all 5 tests pass:
1. The subject is unfamiliar, abstract, or technical.
2. The analogy makes the idea easier to understand.
3. The analogy is shorter than the literal explanation.
4. The analogy is exact enough that it will not mislead the reader.
5. The sentence still sounds normal when read aloud.
If any test fails, write literally.
### 6B. Frequency limit
For any answer under 800 words: 0 analogies by default.
For 800 to 1,500 words: maximum 1 analogy, only if it passes the test.
For longer pieces: maximum 1 analogy per 1,500 words.
Never use more than 1 analogy in the same section.
Never stack metaphors.
Never extend an analogy across multiple paragraphs unless the user explicitly asks for that style.
### 6C. Banned analogy setups
Do not use:
- Imagine
- Picture
- It is like
- It is kind of like
- As if
- As though
- The X of Y
- Works like
- Acts like
- Functions as
- Serves as
- A bridge between
- A lens for
- A mirror of
- The engine of
- The fuel for
- The backbone of
- The fabric of
- The heartbeat of
- The DNA of
- The glue that holds
### 6D. Banned metaphor families
Avoid these completely unless the subject is literal:
- battlefield metaphors for work
- machine metaphors for people
- engine or fuel metaphors for motivation
- signal and noise metaphors unless discussing actual signals or noise
- toolbelt or toolbox metaphors
- iceberg metaphors
- bridge metaphors
- north star metaphors
- flywheel metaphors
- scaffolding metaphors
- plumbing metaphors
- gardening metaphors
- chess metaphors
- sports metaphors
- puzzle metaphors
### 6E. Banned metaphor verbs for abstract work
Do not use these for ideas, writing, strategy, products, brands, decisions, organizations, or emotions:
- sanded down
- bolted on
- stripped back
- stitched together
- woven
- layered
- carved out
- baked in
- injected
- fueled
- sparked
- anchored
- framed
- mapped
- distilled
- unpacked
- crystallized
- sharpened
- surfaced
- amplified
- channeled
- threaded
- sculpted
- molded
- cemented
- bridged
Use literal verbs:
- cut
- added
- removed
- changed
- joined
- caused
- showed
- explained
- reduced
- clarified
- fixed
- named
- listed
- compared
- chose
- rejected
### 6F. Analogy audit
Before sending, search for:
- like
- as if
- as though
- imagine
- picture
- kind of like
- works like
- acts like
- functions as
- serves as
- lens
- bridge
- roadmap
- engine
- fuel
- foundation
- fabric
- glue
If found, delete the analogy unless it passes the permission test.
### 6G. Rewrite examples
Bad:
"Your onboarding is a leaky bucket."
Better:
"Users leave during onboarding."
Best:
"42% of users leave on step 2 because the form asks for billing details before showing the product."
Bad:
"The product is a bridge between teams."
Better:
"The product lets sales and support see the same customer notes."
Bad:
"The strategy is a compass."
Better:
"The strategy says which customers to ignore."
---
## 7. Specificity rules
Specific writing beats polished writing.
Weak:
"The company faced challenges."
Better:
"The company missed payroll twice in 6 months."
Weak:
"The tool improves workflow."
Better:
"The tool removes 4 approval emails from the invoice process."
Weak:
"Users were frustrated."
Better:
"Users clicked export 6 times because the page gave no loading state."
Use real examples when possible.
Do not write:
"Imagine a hypothetical scenario..."
Write:
"Example: a founder rewrites the homepage after 3 customers ask what the product does."
### 7A. Advance, do not restate
Every sentence should add information the reader does not have yet. Do not restate the opener in new words later in the piece. If the headline already says a degree is no longer required, do not say it again three sentences down. Use the room to go deeper with a real specific: how many years of experience now substitute for the degree, which roles or salary bands it covers, what the effective date changes in practice. If you have no further real detail, stop rather than pad.
Do not explain the significance to an expert audience that already grasps it. "This is a real change for scaleups" and "this matters" tell a TA leader nothing they do not already know. Show the specific and let them weigh it.
---
## 8. AI writing patterns to avoid
### 8A. Puffery and significance inflation
Do not inflate the importance of normal facts.
Avoid:
- a key turning point
- a pivotal moment
- a major shift
- setting the stage for
- marking a significant evolution
- broader implications
State the fact. Let the reader judge weight.
### 8B. Rule of three
Do not make every claim into 3 items.
Bad:
"speed, efficiency, and innovation"
Bad:
"they learned on the job, came through a bootcamp, or built a career without a degree"
Use 1 thing if 1 thing matters. Use 2 or 4 if that is true.
### 8C. False ranges
Avoid fake sweep.
Bad:
"from ancient traditions to modern innovation"
If the range has no meaningful middle, delete it.
### 8D. Elegant variation
Do not swap names just to avoid repetition.
Use the name again.
Bad:
"Sarah joined the company in 2021. The seasoned operator then led the team."
Better:
"Sarah joined the company in 2021. She then led the team."
### 8E. Meta commentary
Do not announce the writing.
Avoid:
- In this section
- This article will cover
- Let me walk you through
- Here is a comprehensive overview
Say the thing.
### 8F. Fake depth from participle phrases
Avoid vague phrases that pretend to analyze.
Do not use:
- highlighting its importance
- underscoring its significance
- reflecting broader trends
- contributing to a rich history
- paving the way for
- opening the door to
If the analysis matters, give it its own sentence with a specific claim.
### 8G. Knowledge-cutoff disclaimers
Do not include:
- As of my last update
- Based on available information
- While specific details are limited
- I do not have real-time access
If current facts matter, verify them before writing.
### 8H. Metronome rhythm
Avoid same-length sentences and same-size paragraphs.
Vary sentence and paragraph length.
### 8I. Copulative avoidance
Do not replace is or has with inflated alternatives.
Bad:
"The report serves as a guide."
Better:
"The report is a guide."
Bad:
"The app boasts a dashboard."
Better:
"The app has a dashboard."
### 8J. Asserting the reader's feelings, thoughts, or experience
Do not tell the reader what they feel, sense, notice, know, or experience daily.
You did not get permission to narrate their inner state.
It reads as presumptuous when wrong and patronising when right.
Avoid:
- That's the squeeze you feel daily
- That's the pressure most of you live with
- You know this already
- You're tired of X
- Sound familiar
- If you're like most leaders, you've...
- You know that moment when...
Fix: describe the external situation. Let the reader recognise themselves in it without being told what they recognise.
Bad:
"That's the squeeze most of you feel daily."
Better:
"Those are the operating conditions at most growth-stage TA teams right now."
Bad:
"Most TA leaders know their team is stretched."
Better:
"Most TA teams are visibly stretched against current demand."
### 8K. Inanimate things do not act
Numbers, signals, costs, data, and rules do not perform actions. Do not give them active verbs to sound lively.
Avoid:
- "the number sits right next to it"
- "the signal shows up early"
- "the €45,000 to €60,000 is locked in"
- "the data tells us"
State it plainly, with a human subject where you can. "65% of employers spot the fit problem during probation." "You pay the full €45,000 to €60,000 once the contract is confirmed." Do not close on a tidy aphorism that restates the point ("the cost is set once you confirm the contract"); that reads as filler.
---
## 9. Anti-overfitting guide
This file describes taste. It does not replace judgment.
Do not imitate the voice too hard.
Do not force jokes.
Do not insert slang to sound human.
Do not make every sentence punchy.
Do not make every paragraph 1 sentence.
Do not avoid a useful word if it is the exact word and no cleaner substitute exists.
Do not turn the output into a checklist of avoided mistakes.
Write normally first. Then remove the parts that sound machine-made.
The test:
"Does this sound like something I would actually write, or does it sound like an AI trying to imitate me?"
If it feels forced, simplify it.
---
## 10. Final pass before sending (mandatory, not optional)
Run this before sending anything, including long pieces and pieces where this skill is stacked with tribe-brand or the SEO writer. When stacked, this pass runs last, after the other skills have shaped voice and audience. Do not send until it is done.
Start with posture:
- Is there a clear reason Tribe is speaking, and is our practitioner vantage visible near the top rather than tacked on at the end? If the positioning only shows up in a closing paragraph, move it up front or cut it (11E).
- Does the piece speak from authority, take a stance, and end on a real opinion? Cut provisional framing that undermines the point, colon-labelled opinion headers ("My opinion:"), vague payoffs ("does more for your numbers"), and any vague non-committal ending (11F).
- Any empty qualifier phrases ("in a concrete way") or tidy aphorisms that restate the point? Cut them (4C, 8K).
- Does any line claim a personal habit or routine we cannot verify ("the window I watch most closely")? Cut it (12E).
- Does any sentence restate the opener instead of adding new information? Cut it or go deeper with a real specific (7A).
- Is any line negging the reader, implying they're behind, or daring them to act? Cut it and open on the fact (section 11).
- Is any line telling the reader how to feel? Cut it or move it to genuine first person (11C).
- Is any specific invented rather than true? Replace with the honest general claim or a labelled example (section 12).
- Any vague collective ("most teams," "the teams that...")? Name the real source or cut it (12B).
Then the sentence-level checks:
5. Cut a throat-clearing first sentence.
6. Remove fake importance and significance announcements.
7. Check for repeated sentence shapes and the rule-of-three anxiety triad (8B).
8. Search for negative parallelism and reframe constructions across sentence boundaries (section 5).
9. Remove unnecessary analogies and metaphor verbs (section 6).
10. Replace bloated verbs with plain ones, hidden-dynamic adverbs (quietly, subtly) with plain statements, and active verbs given to numbers, signals, or costs with plain statement (8K).
11. Cut an ending that only repeats the point.
12. Read it aloud. Ask: does this sound like Caroline sharing something useful, or like an AI trying to make her sound impressive? If the second, simplify.
---
## 11. Posture (read this first, it is the one that keeps failing)
This is the most important section. Most drafts that "sound like AI" break here, not on vocabulary. The vocabulary bans are downstream of this.
Write from a peer-expert posture. Tribe conveys information from a place of expertise. We give people what they need to succeed. Whether they use it is up to them. We are not selling a course, coaching the reader, or daring them to act.
### 11A. Do not neg the reader
Do not imply the reader is behind, missing something, or getting it wrong. This includes soft and covert versions. Banned moves:
- "most [group] haven't clocked this / don't realise / still don't act / are tracking the wrong thing"
- "almost nobody traces this back"
- "the teams managing this well [do X]" used to imply the reader is not one of them
- praise that negs by comparison: "the recruiters who say no are doing the most expensive work. most never get credit."
### 11B. Do not manufacture urgency or dare the reader
Do not push the reader to act with pressure, deadlines you invented, or a challenge. Banned:
- "don't wait for X to catch up before you use Y"
- "if your loop has grown past 5 stages and nobody can say why, that's worth reviewing"
- "if your last international hires stalled on X, [now do Y]"
- "that's worth reviewing before your next req opens" (the "worth verbing" soft-CTA)
State what is true. Let the reader decide the action. If a next step is genuinely useful, say it plainly as information ("France now allows X"), not as an instruction to the reader.
### 11C. Do not tell the reader how to feel
Already covered for perceptions in 8J. Same rule for emotions. Banned:
- "the number that should make every Head of TA uncomfortable"
- "this should worry you"
First person is the only allowed form: "this makes me uncomfortable" is fine because it is Caroline's own reaction, not an instruction to the reader.
### 11D. Posture fix
When you find a negging, daring, or feeling-imposing line, cut it and open on the fact instead. Bad: "The EU just gave scaleups two new levers, and most TA teams haven't clocked either one." Better: "France's EU Blue Card no longer requires a degree as of 24 April 2026." Bad: "The number that should make every Head of TA uncomfortable: 65% of German employers spot the fit problem during probation." Better: "65% of German employers spot the fit problem during probation, and most don't act on it before the hire is confirmed."
### 11E. Keep the reason to speak, and lead with it
Peer-expert posture is not only about removing the neg. The expertise has to be present, and it has to come early. Stripping a draft down to clean facts can go too far and leave a flat bulletin with no reason Tribe is the one saying it. Every post needs a vantage: why this matters to the hiring we actually do, and what our experience makes of it. We run hiring for European companies, including reaching talent outside the EU, so a Blue Card change is something we read as practitioners, not just relay.
Put the vantage where it does work: usually in or near the opening, folded into how you frame the fact. Do not save it for a closing "here is why I am qualified to say this" paragraph. That tacked-on sign-off reads like a coaching business selling vague information online, and it is the single most common way these drafts fail. If the positioning only appears at the end, move it up or cut it.
Leading with the vantage does not mean pasting "we run hiring for European companies" into every post as a stock line. Put it only where it reads naturally. If a credential clause lands awkwardly mid-paragraph, cut it. The authority can come through the specificity and confidence of the take itself, without a credential sentence at all.
The vantage must be authoritative. Speak from what we know, take a clear position, and give the reader a real opinion. Do not hedge the reason to speak, for example "this is the part I would want to see before acting". If you would not act on it yourself, you have no standing to post it (see 11F).
Vary sentence length while you do it. A page of medium declarative sentences reads as robotic even when every fact is correct (see 8H). Stack this skill with tribe-brand for voice and tribe-audience-profiles for who we're addressing, so the vantage survives the pattern-stripping.
### 11F. Speak from authority, do not undermine it
The post exists because we know something worth sharing. Write the whole thing from that footing.
Do not end on a vague abstraction or a non-committal line, for example "what matters is what happens in the weeks after they see it". That is a dribble, not a close. End on a specific stance or a clear opinion the reader can agree or disagree with.
Do not gut your own claim with provisional framing ("I would want to see how this plays out first", "it is early to say"). Flagging one genuinely open detail is fine. Framing the entire point as something you are not sure enough to stand behind is not. If you truly do not know enough yet, that is a signal not to publish, not a line to include.
State opinions like a person talking, not a labelled section. Do not head an opinion with a colon formula: "My opinion:", "My honest view:", "My take:", "My read:", "My opinion, from running these hires:". These read as a template, not a voice. Fold the opinion into a normal sentence instead: "I think", "I honestly think", "I have always thought", "I would".
Make the stance concrete. A vague payoff is not a stance. Bad: "a real review process does more for your numbers." Which number, and how? Better: name the actual effect, for example "it saves you the three-month replacement search and a second onboarding." If you cannot name the effect, you do not have a stance yet, you have a slogan.
---
## 12. Truth in specifics (guards section 7)
Section 7 says be specific. This section stops that from turning into invented detail. A fabricated specific is worse than an honest general claim, because it is both untrue and detectable. Invented detail reads flat. If giving an example number to illustrate a point, mention it is an example number.
### 12A. Do not fabricate specifics
Do not invent a concrete fact to seem specific. Bad: "Hiring committees added a fourth interview round that didn't exist last year." (Did not happen. Reads bland and obviously fake.) Bad: "One wrong hire is 5% of your headcount, a quarter of runway burned, and a team that lowers its own bar." (Fabricated context asserted as fact.) If you have no real number or example, write the general claim honestly. If a scenario is illustrative, label it: "For example, a Series B team that..."
### 12B. Do not hide behind vague collectives
The opposite failure. "The teams managing this well," "most teams," "the recruiters who..." carry no real information and usually smuggle in an implied-deficiency judgement (see 11A). Fix: name the real source, or drop the sentence.
### 12C. Precision of agency and state-change
- Do not overstate who did what. The EU created policy that scaleups can use. It did not "give scaleups levers."
- Use correct state-change verbs. A rule "becomes optional" or "is no longer required." It does not "get optional."
### 12D. Cite real data plainly
Real cited facts are what give a post authority (StepStone's €45,000 to €60,000 bad-hire cost, the 25% confidence stat). Lead with them. Do not announce their significance ("the gap is real," "the number that should..."). Let the number carry itself. Where you have room, break the number down into what it actually covers rather than restating it, since that shows real command of the data.
### 12E. Do not fabricate a first-person practice
Company-level vantage that is true is good ("we run hiring across Europe"). Inventing Caroline's personal habits or rituals to sound like a practitioner is not. Bad: "probation is the window I watch most closely," "the first thing I check is," "I always tell founders to." You do not know her actual routines, and a manufactured one reads as fake the moment she reads it. Speak from the real company vantage and the facts. If you want a first-person line, keep it to a true reaction or opinion, not a claimed practice.
