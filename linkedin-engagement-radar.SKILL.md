---
name: linkedin-engagement-radar
description: >-
  Find EU-based decision-makers who recently posted on LinkedIn so Jacopo can comment
  and warm them up before outreach. Two modes. FRESH-LEAD mode (the default, and the
  warm lane of the Lead Engine): checks the decision-makers at companies the cold feed
  just surfaced (funding rounds, board velocity, TA pressure) for recent posts, because
  a founder who announced a round this week has always posted about it and that post is
  the best commenting surface there is. ACCOUNT-LIST mode (only when Jacopo explicitly
  asks about "my accounts" or "the account list"): relationship-maintenance commenting
  on his account-list sheet contacts, which is NOT a harvest source for new outreach.
  Checks activity through Jacopo's logged-in browser, filters to EU/Europe-based people
  with a post in roughly the last 4 weeks, ranks them, and (on request) drafts comments
  in his voice. EU-based only, never random people.
---

# LinkedIn engagement radar

The job: give Jacopo a short, ranked list of **real people who posted on LinkedIn
recently**, with the post and a direct link, so he can comment and warm up the
relationship before any outreach. Then, if he wants, draft the comments in his voice.

## The two modes (Jacopo clarified this on 20 Aug 2026)

**Fresh-lead mode is the default** and is what "run the lead engine" means for the warm
lane. The people to check are the decision-makers at the NEW companies the cold feed just
surfaced: fresh funding rounds, board-velocity alerts, first-recruiter-role alerts, TA
pressure. A founder who announced a round in the last few days has always posted about it,
and that announcement post is the single best commenting surface that exists. The engine's
first live test (20 Aug 2026) proved it three for three: all three founders found by the
funding sweep had posted their round within the previous 72 hours. Comment first, variant
W inside the 72h window, cold email never while the warm-up is live.

**Account-list mode runs only when Jacopo explicitly asks** ("who from my accounts posted
recently", "check the account list"). Commenting on account-list people is relationship
maintenance on existing territory, not lead harvesting, and it produces outreach only when
Jacopo says he commented and wants the follow-through. The first test run made this
mistake in reverse (crawled the account list while hunting new leads); the mode split
exists so it never happens again. Side benefit of that crawl worth keeping: the sheet
drifts badly, so any account-list run should report job changes it finds (it caught a
Head of TA who had left a Tier 1 account, invalidating a scheduled follow-up contact).

Two hard constraints that come straight from Jacopo and must never be relaxed:

1. **EU / Europe based only.** Never surface someone based in the US, LatAm, APAC, etc.
   When in doubt about location, verify or drop them. Do not pad the list with people who
   are not clearly in Europe.
2. **No random people.** Fresh-lead mode starts from companies a real market signal
   surfaced; account-list mode starts from the sheet. Never pad either list with people
   who came from neither.

## Inputs and defaults

- **Fresh-lead mode source** (default): the current harvest's companies. Per company,
  resolve the CEO/founder or the most senior People/TA leader via LinkedIn people search
  (`/search/results/people/?keywords=<Company>%20founder%20CEO`), verify name + company
  on the result, then check their recent activity. CEO/founder/Head-of only, never TA ICs.
- **Account-list sheet** (account-list mode only): `30-Account-Target-List-Template`
  - fileId: `1Dj40gCj9qlEU34C7DEELRqJ25P4UYorEbjj5JNhZUHE`
  - Use the tab **named "Jacopo: Account List"**. Important: do not trust the `gid` in a
    pasted URL. The `gid` often points at whatever tab was open when the link was copied
    (it has resolved to "Tijana: Account List" before). Always select the tab by its
    **name**, and note the internal title cell of Jacopo's tab still reads "Director:
    [Your Name]" (a copy-paste leftover) — that is fine, it is the right tab.
- **Recency window** (default): posts within the **last ~4 weeks**. `1w`, `2w`, `3w`,
  `1mo` count. `2mo`+ is too stale to comment on and should be dropped (mention them
  separately as "active but stale" if the topic is a strong fit).
- **Target contacts**: the People / Talent leaders first (Head of TA, VP People, CPO,
  CHRO, People Ops), then founders / CEOs / CFOs listed as budget holders or influencers.
  People/TA peers are the highest-value comment targets for Jacopo.

If Jacopo names a different tab (e.g. his newest list), a different sheet, or a different
recency window, use those instead.

## Step by step

### 1. Get the people to check
**Fresh-lead mode:** take the current harvest's companies and resolve each decision-maker
via LinkedIn people search (step 3's technique). Skip to step 2.
**Account-list mode:** read the account list as follows.
Use the Google Drive tool to read the sheet, then isolate the **Jacopo: Account List**
tab. The full-sheet export concatenates every tab without labels, so confirm tab identity
and order through the browser if needed (see step 2's browser session):
```js
[...document.querySelectorAll('.docs-sheet-tab')].map(t=>({
  name: t.querySelector('.docs-sheet-tab-name')?.innerText,
  active: t.classList.contains('docs-sheet-active-tab')
}))
```
Extract, per company: company, tier, country, key contact (name + title + LinkedIn),
budget holder, influencer. Many LinkedIn cells are rich-text links on the word "LinkedIn",
so their URLs do **not** survive CSV/gviz export. You will have explicit `/in/...` URLs for
some contacts and only a name for others. That is expected — resolve the rest in step 3.

### 2. Connect Jacopo's browser (logged-in LinkedIn)
Use the Claude-in-Chrome tools. `list_connected_browsers` → if Jacopo wants to pick,
`switch_browser`; otherwise `select_browser` with the deviceId. Create/It reuse one tab and
drive everything through it. LinkedIn must be logged in as Jacopo — this is ordinary
first-person browsing of profiles, nothing more. **If LinkedIn shows a checkpoint,
captcha, or "unusual activity" screen, stop immediately and tell Jacopo.** Never try to
solve or bypass it, and slow down the pace.

### 3. Resolve missing LinkedIn URLs
For contacts where the sheet only gives a name, resolve the profile through LinkedIn
people search, then read the top result:
```
https://www.linkedin.com/search/results/people/?keywords=<Name>%20<Company>
```
```js
// after a ~2.5s wait
const clean=s=>(s||'').replace(/\s+/g,' ').trim();
const seen=new Set(), res=[];
for(const a of document.querySelectorAll('a[href*="/in/"]')){
  const m=a.href.match(/\/in\/([^\/?#]+)/); if(!m||seen.has(m[1])) continue;
  seen.add(m[1]); res.push({slug:m[1], name:clean(a.innerText).slice(0,60)});
  if(res.length>=3) break;
}
JSON.stringify(res);
```
Take the first result whose name + current title actually match the contact. Watch for
job changes — the sheet can be stale (e.g. a "Head of TA at X" who has since moved to Y).
Note the move; only keep them if they are still EU-based and a sensible target.

### 4. Check each person's recent activity
Navigate to `https://www.linkedin.com/in/<slug>/recent-activity/all/` and extract the
top posts with timestamps. Batch several people per `browser_batch` call (navigate + the
script below, repeated), which is much faster. The script waits for the feed to render:
```js
const wait=ms=>new Promise(r=>setTimeout(r,ms));
let cards=[];
for(let i=0;i<12;i++){
  cards=[...document.querySelectorAll('div.feed-shared-update-v2, div.update-components-update-v2')];
  if(cards.length) break; await wait(600);
}
const clean=s=>(s||'').replace(/\s+/g,' ').trim();
const me=clean(document.querySelector('h1')?.innerText)||location.pathname;
const out=cards.slice(0,5).map(c=>({
  head: clean(c.querySelector('.update-components-header__text-view')?.innerText).slice(0,60), // "reposted"/"commented" context; empty = original post
  time: clean(c.querySelector('.update-components-actor__sub-description')?.innerText).split(' • ')[0], // e.g. "3d", "2w", "1mo"
  text: clean(c.querySelector('.update-components-text')?.innerText).slice(0,160)
}));
JSON.stringify({me, count: cards.length, out});
```
Classify each item: an empty `head` is an **original post** (best to comment on). A `head`
containing "reposted"/"commented on"/"likes" is weaker — reposts are commentable but rank
below original posts; pure likes/comments do not count.

### 5. Filter and rank
Keep a person only if they have an **original post (or a substantive repost) within the
recency window** and are **EU/Europe based**. Rank by:
1. Recency (3d > 1w > 2w > 3w > 1mo).
2. Relevance to Jacopo — People/TA peers and substantive content beat pure company PR.
3. Warmth / tier — Tier 1 accounts first when recency is similar.

Flag UK-based people explicitly (Europe, but not EU-27) so Jacopo can decide, and be
honest about anyone whose exact location you could not confirm.

### 6. Fallback — only if fewer than 5 qualify
If the whole account list yields **fewer than 5** EU posters in the window, expand to a
wider ICP, still EU-only and still genuinely relevant: EU-based Heads of TA / VP People /
CPO / founders at Seed–Series C European startups in payments, fintech, and adjacent
scale-ups, who have posted recently. Search by role + region and verify EU location before
adding. State clearly which people came from the account list and which are ICP expansion.

## Output

Deliver a ranked shortlist in chat (this is a point-in-time action list, not a persisted
artifact). Per person: name, company, role, how recent the post is, a one-line summary of
the post, and the direct activity link
(`linkedin.com/in/<slug>/recent-activity/all/`). Add a one-line "my call" on who to hit
first. Keep a short "checked but skipped" note (inactive / stale / non-EU) so Jacopo sees
the coverage. Cite the sheet at the end.

## Drafting the comments

Only when Jacopo asks. **Always draft comments through the `jacopo-linkedin-voice`
skill** — read it and follow its hard rules. For comments specifically:

- 1–3 sentences, conversational, reacting to the actual post (read the full post first,
  not just the extracted snippet).
- Add one Jacopo-perspective observation (embedded recruiting / TA / people economics)
  where it fits naturally. Do not force a recruiting angle onto every post, and never make
  it a pitch.
- Same AI-tell bans as posts: no em dashes, no "it's not X, it's Y" inversion, no
  tricolons of abstract nouns, no rhetorical closing questions, no arrows, none of the
  banned B2B words ("align", "leverage", "journey", "ecosystem", "landscape", etc.).
- On celebratory / PR posts, stay warm and brief with one substantive nod. On
  thought-leadership posts, add a genuine peer idea.
- If the post is in Italian (or another language Jacopo writes), draft the comment in that
  language — it reads as more authentic. Jacopo is Italian and based in Prague.

End by telling Jacopo which 2–3 to comment on first and why.

## Notes and pitfalls

- Do the whole thing in one browser tab; pace the profile visits and stop on any LinkedIn
  security screen.
- The sheet drifts: people change jobs, links point to same-name strangers. Verify the
  name **and** current title on each profile before trusting it.
- Don't over-collect. A tight, correct list of 6–8 beats a padded 20 with weak or
  non-EU entries — that padding is exactly what Jacopo does not want.
