---
name: linkedin-engagement-radar
description: >-
  Find EU-based people from Jacopo's Tribe account list who have recently posted on
  LinkedIn, so he can go comment on them. Use whenever Jacopo asks to find posts to
  comment on, "who from my accounts posted recently", "find me people to engage with
  on LinkedIn", "commenting radar", "give me posts to comment on", or wants to warm up
  target accounts through LinkedIn engagement. Pulls contacts from the account-list
  Google Sheet, checks each person's recent LinkedIn activity through Jacopo's logged-in
  browser, filters to EU/Europe-based people with a post in roughly the last 4 weeks,
  ranks them, and (on request) drafts comments in his voice. EU-based only, never random
  people. If fewer than 5 qualifying posts are found in the account list, it expands to a
  wider but still-relevant EU ICP.
---

# LinkedIn engagement radar

The job: give Jacopo a short, ranked list of **real people from his target accounts who
posted on LinkedIn recently**, with the post and a direct link, so he can comment and warm
up the relationship. Then, if he wants, draft the comments in his voice.

Two hard constraints that come straight from Jacopo and must never be relaxed:

1. **EU / Europe based only.** Never surface someone based in the US, LatAm, APAC, etc.
   When in doubt about location, verify or drop them. Do not pad the list with people who
   are not clearly in Europe.
2. **No random people.** Everyone on the list starts from his account list. Only expand
   beyond it if the account list yields fewer than 5 qualifying posts (see Fallback), and
   even then stay inside his genuine ICP.

## Inputs and defaults

- **Account-list sheet** (default): `30-Account-Target-List-Template`
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

### 1. Read the account list
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
