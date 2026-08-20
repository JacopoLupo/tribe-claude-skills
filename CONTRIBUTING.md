# Improving these skills

These skills get better the way the playbook got built: someone hits a real problem on a real account, and the fix becomes a rule. If you're Martin, Blake, Salem or Kris reading this, here's how to contribute without breaking the machine.

## The golden convention: dated decisions

Every rule in the SKILL.md files carries its date and its story ("Jacopo tightened this on 20 Aug", "this exists because the Choco send went out with the wrong proof names"). This is not decoration: Claude sessions read this history to understand WHY a rule exists and when it was last confirmed. When you change something, write it the same way, what changed, when, and what prompted it. Never delete the history a rule carries; supersede it ("overrides the earlier X rule").

## How to propose a change

1. Edit the `.SKILL.md` file directly on GitHub (pencil icon on the file page).
2. In the commit dialog, choose **"Create a new branch and start a pull request"**, don't commit straight to main. The PR is where the change gets discussed.
3. One change per PR, with the reasoning in the description: what went wrong or what could be better, and which account or send taught you that.
4. Jacopo merges. After a merge, the skill needs repackaging (below) and re-uploading to claude.ai, otherwise the live skill and the repo drift apart.

## Repackaging after a merge

Create a folder named exactly after the skill, put `SKILL.md` inside (plus `scripts/index.py` for the outbound skill), zip the folder, rename the zip `<skill-name>.skill`, replace the file in this repo, and upload it to claude.ai (Customize → Skills, or org settings for everyone).

## What NOT to touch

- **The two A/B email variants**, while the test runs (verdict due end of September 2026). An edited variant restarts its count and corrupts weeks of data. Propose changes as "variant C candidates" in a PR instead.
- **The slug list in `index.py`** without noting the change in the SKILL.md: adding boards changes the index totals, and week-over-week comparability is the whole value. Adding is fine, silently is not.
- **The banned sentence shapes and voice rules.** These came from real prospects going quiet. If you think one is wrong, bring the reply data.

## Ideas that are wanted

New scaling signals for the cold feed (what tells you a company is about to hire, before their board shows it?), real search stories for the proof library (role, company, time to fill, all verified), better follow-up hooks, and anything from your own accounts that the reply playbook doesn't cover. The proof library especially: it only grows when someone who ran a search writes down what actually happened.
