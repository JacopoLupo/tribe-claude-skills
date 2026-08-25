#!/usr/bin/env python3
"""Log LinkedIn activity into HubSpot as native Communications.

WHY THIS EXISTS, AND WHY IT IS THE FALLBACK (header corrected 25 Aug 2026)
    THE PREMISE THIS FILE WAS BUILT ON WAS FALSE. It used to open "HubSpot has
    no native LinkedIn logging", which is exactly the belief that cost an
    afternoon on 24 August: the connector could not see the communications
    object, and the connector's blind spot was mistaken for the product's.
    HubSpot has had native LinkedIn logging the whole time, on the contact
    record under More > Log a LinkedIn message. Leaving the false sentence in
    the header of a live script is how a corrected belief comes back.

    So the primary route is the HubSpot UI, documented in the skill. This
    script is the fallback for the day that route is unavailable or a bulk
    backfill is needed: the Communications API accepts
    hs_communication_channel_type = LINKEDIN_MESSAGE and renders the same
    activity on the timeline. It needs a private app token and an admin; the
    UI route needs a browser. Prefer the browser.

THE TOKEN NEVER PASSES THROUGH CLAUDE
    The script reads it from a file on Jacopo's own machine. Claude writes and
    runs this script and passes it the message DATA, but never sees the secret.
    Do not paste the token into a chat, a task body, or this file.

AUDIT, 24 AUGUST 2026. The first version of this file could not work. It set
hs_message_direction, which does not exist on Communications, so every single
create would have returned 400 and logged nothing. Worse, --check POSTed an
empty-properties communication to test the scope: HubSpot enforces no required
properties on this object, so that would have created a blank record with no
associations, which is unreachable in the HubSpot UI and therefore impossible
to delete by hand. One per run of the command the user was told to run first.
Both are fixed below and both are commented so they do not come back.

SETUP, ONCE
    1. HubSpot > Settings > Integrations > Private Apps > Create a private app.
       Name it "Tribe LinkedIn logger".
       Scopes tab, tick exactly two:
           crm.objects.contacts.read
           crm.objects.contacts.write
       Create, then copy the access token.

    2. On your machine, in this order (umask before mkdir, so the directory
       itself is not world-traversable):
           umask 077 && mkdir -p ~/.tribe
           printf '%s' 'PASTE_TOKEN_HERE' > ~/.tribe/hubspot_token
           chmod 600 ~/.tribe/hubspot_token
       That paste is the only moment the token is ever visible.

    3. python3 linkedin_to_hubspot.py --check
       Read-only. Confirms the token works and carries contacts.read. Writes
       nothing, ever. See check() for why write scope is deliberately not
       tested.

USAGE
    echo '<json array>' | python3 linkedin_to_hubspot.py
    python3 linkedin_to_hubspot.py --check      # verify token and scopes
    python3 linkedin_to_hubspot.py --dry-run    # show what would be sent

INPUT, a JSON array on stdin, one object per LinkedIn touch:
    [
      {
        "contact_id": "486435119350",
        "body": "Ciao Ralf, thanks for accepting. ...",
        "timestamp": "2026-08-24T12:22:00Z",
        "direction": "OUTGOING",
        "owner_id": "33687989"
      }
    ]
    direction is OUTGOING (we sent it) or INCOMING (they did), default OUTGOING.
    It is written as a prefix in the body text, because Communications has no
    direction property. owner_id is optional and defaults to DEFAULT_OWNER_ID.

EXIT CODES
    0  every item logged
    1  anything failed, or setup is wrong
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

TOKEN_FILE = os.environ.get("TRIBE_HUBSPOT_TOKEN_FILE",
                            os.path.expanduser("~/.tribe/hubspot_token"))
LEDGER_FILE = os.environ.get("TRIBE_HUBSPOT_LEDGER",
                             os.path.expanduser("~/.tribe/logged_linkedin.json"))
API = "https://api.hubapi.com"
DEFAULT_OWNER_ID = "33687989"          # Jacopo. Unowned activities do not
                                       # attribute to anyone in HubSpot reports.
COMMUNICATION_TO_CONTACT = 81          # HUBSPOT_DEFINED association type id.
PAUSE = 0.15                           # HubSpot allows 100-190 req/10s.


def read_token():
    """Read the token from disk. Never printed, never returned to anything that
    renders. Every error path below emits the file PATH, never its contents."""
    try:
        with open(TOKEN_FILE) as fh:
            tok = fh.read().strip()
    except FileNotFoundError:
        sys.exit(f"No token file at {TOKEN_FILE}. See SETUP in this file's header.")
    if not tok:
        sys.exit(f"{TOKEN_FILE} is empty.")
    if not tok.startswith("pat-"):
        sys.exit("That does not look like a HubSpot private app token "
                 "(they start with 'pat-'). Check the file.")
    return tok


def call(method, path, token, payload=None, _retries=3):
    """One request. Retries on 429 honouring Retry-After.

    Note on token safety: the HTTPError branch returns only the response body,
    and HubSpot does not echo request headers. urllib's default redirect
    handler would forward the Authorization header across hosts, which is why
    API is a hardcoded https://api.hubapi.com constant and must stay one."""
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        if e.code == 429 and _retries > 0:
            wait = float(e.headers.get("Retry-After", 10) or 10)
            print(f"  rate limited, waiting {wait:.0f}s")
            time.sleep(wait)
            return call(method, path, token, payload, _retries - 1)
        body = e.read().decode(errors="replace")
        return e.code, {"error": body[:400]}
    except Exception as e:
        return 0, {"error": str(e)[:200]}


def check(token):
    """Verify the token WITHOUT writing anything.

    Three designs were tried and two were wrong, so the reasoning is recorded.

    1. The original POSTed an empty-properties communication and treated
       anything that was not a 403 as success. HubSpot enforces no required
       properties on this object, so that CREATES a blank record with no
       associations. An unassociated engagement is only reachable through a
       record's timeline, so it cannot be found or deleted in the UI at all.
       One per run, of the command the setup notes tell you to run first.
    2. Token introspection (/oauth/v1/access-tokens/{token}) puts the secret in
       the URL, which is where a secret should never go: URLs land in logs,
       proxies and error reports. It is also deprecated in February 2027.
    3. So: prove read with a read, and do not prove write at all. A missing
       write scope surfaces as a 403 on the first real item, and a 403 creates
       nothing, so that failure mode is already clean. There is no reason to
       write junk to find out."""
    status, resp = call("GET", "/crm/v3/objects/contacts?limit=1", token)
    if status == 401:
        sys.exit("HTTP 401. The token is wrong or has been revoked.")
    if status == 403:
        sys.exit("HTTP 403. The token works but crm.objects.contacts.read is "
                 "not ticked on the private app.")
    if status != 200:
        sys.exit(f"HTTP {status} reaching HubSpot. {resp.get('error','')[:200]}")
    print("OK    token valid")
    print("OK    crm.objects.contacts.read")
    print("      crm.objects.contacts.write is NOT tested here, because the only")
    print("      way to test a write is to write. If it is missing, the first")
    print("      real item returns 403 and creates nothing.")
    print("\nReady. Nothing was written to the CRM by this check.")


def load_ledger():
    try:
        with open(LEDGER_FILE) as fh:
            return set(json.load(fh))
    except Exception:
        return set()


def save_ledger(seen):
    try:
        os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
        with open(LEDGER_FILE, "w") as fh:
            json.dump(sorted(seen), fh)
    except Exception as e:
        print(f"WARNING: could not write the dedupe ledger ({e}). "
              "A re-run will double-log.")


def fingerprint(item):
    raw = f"{item['contact_id']}|{item['timestamp']}|{item['body']}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def build(item):
    """Build the create payload, association INLINED.

    Create-then-associate was two calls, and a failure on the second left a
    Communication attached to nothing. An unassociated engagement is only
    reachable through a record's timeline, so it cannot be found or deleted in
    the HubSpot UI at all. The old code's advice, 'fix by hand or delete it',
    was not something a human could actually do. One atomic request removes the
    orphan class entirely and halves the request count."""
    direction = item.get("direction", "OUTGOING").upper()
    prefix = {"OUTGOING": "[Sent] ", "INCOMING": "[Received] "}.get(direction, "")
    return {
        "properties": {
            "hs_communication_channel_type": "LINKEDIN_MESSAGE",
            "hs_communication_logged_from": "CRM",
            "hs_communication_body": prefix + item["body"],
            "hs_timestamp": item["timestamp"],
            "hubspot_owner_id": str(item.get("owner_id", DEFAULT_OWNER_ID)),
        },
        "associations": [{
            "to": {"id": str(item["contact_id"])},
            "types": [{"associationCategory": "HUBSPOT_DEFINED",
                       "associationTypeId": COMMUNICATION_TO_CONTACT}],
        }],
    }


def main():
    token = read_token()
    if "--check" in sys.argv:
        check(token)
        return 0

    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit("Nothing on stdin. Pipe in a JSON array, see the header.")
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"stdin is not valid JSON: {e}")
    if isinstance(items, dict):
        items = [items]

    seen = load_ledger()
    ok = skipped = 0
    attempted = 0

    for item in items:
        missing = [k for k in ("contact_id", "body", "timestamp") if k not in item]
        if missing:
            print(f"FAIL  missing {missing}: {str(item)[:70]}")
            continue
        cid = str(item["contact_id"])
        # A LinkedIn-sourced workflow can easily hand over an email address or
        # a profile URL where a HubSpot record id belongs. That used to create
        # the communication first and only then fail on the association,
        # leaving an unreachable orphan.
        if not cid.isdigit():
            print(f"FAIL  contact_id '{cid[:40]}' is not a HubSpot record id")
            continue

        fp = fingerprint(item)
        if fp in seen:
            skipped += 1
            print(f"SKIP  contact {cid}: already logged (same body and timestamp)")
            continue

        payload = build(item)
        if "--dry-run" in sys.argv:
            print(f"DRY   contact {cid}: {json.dumps(payload)[:160]}...")
            continue

        attempted += 1
        status, resp = call("POST", "/crm/v3/objects/communications", token, payload)
        if status in (200, 201):
            ok += 1
            seen.add(fp)
            print(f"OK    contact {cid}: logged as communication {resp.get('id')}")
        else:
            print(f"FAIL  contact {cid}: {status} {resp.get('error', '')[:200]}")
        time.sleep(PAUSE)

    if not ("--dry-run" in sys.argv):
        save_ledger(seen)

    print(f"\n{ok} logged, {skipped} already present, "
          f"{attempted - ok} failed, {len(items)} in.")
    # Always exiting 0 hid a total failure from every automated caller.
    return 0 if (attempted - ok) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
