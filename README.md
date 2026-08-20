# Tribe Claude Skills

Claude skills powering Tribe's outbound sales desk. **This repository is PRIVATE**: it contains the full outbound playbook, client proof points, live A/B test variants, and HubSpot record references.

## The skills

**tribe-outbound-sequence** is the writing half: the Tribe Board Index (a live scan of ~40 European scaleup job boards, script in `index.py`), the two A/B-tested email variants, the proof rules, the follow-up ladder, and the CRM hygiene that goes with every send. Source: `tribe-outbound-sequence.SKILL.md`. Packaged: `tribe-outbound-sequence.skill`.

**tribe-sales-desk** is the discipline half: the daily reconciliation against Sent mail, bounce and tracking health checks, the reply playbook, deal and task hygiene, the merge queue, and the weekly sweep. Source: `tribe-sales-desk.SKILL.md`. Packaged: `tribe-sales-desk.skill`.

## Installing

Individual: claude.ai, Customize, Skills, upload a `.skill` file.

Org-wide (Team/Enterprise, org owner only): Organization settings, Skills, enable the Skills toggles, Add, upload the `.skill` file. Everyone at Tribe gets it, and re-uploading updates it for everyone.

## Updating

Edit the `.SKILL.md` source (or `index.py`). To repackage: create a folder named after the skill containing `SKILL.md` (and `scripts/index.py` for the outbound skill), zip it, and rename the zip to `<skill-name>.skill`. Replace the packaged file here and re-upload to claude.ai. The skills carry their own change history in prose (dated decisions inside the SKILL.md), keep that convention: future Claude sessions rely on it.

## Note before sharing with teammates

Both skills are currently personalized to Jacopo Lupo Ferrari (signature, Calendly link, first-person voice, decision history). They work as-is only for him. A team edition with the sender identity as a slot is the planned next step before wide rollout.
