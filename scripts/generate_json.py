#!/usr/bin/env python3
"""
Regenerates CM/members.json and CM/banlist.json from CM/members.html and
CM/banlist.html, so the HTML pages stay the single source of truth.

members.json: array of usernames, scraped from
    <div class="member">Username</div>
blocks in members.html.

banlist.json: array of UUIDs, scraped by matching the standard UUID
pattern anywhere in banlist.html. This is deliberately format-agnostic -
it doesn't care what markup wraps each UUID, only that a UUID appears -
so it keeps working even if banlist.html's layout changes later.

Run from the repo root:
    python scripts/generate_json.py
"""

import json
import re
from pathlib import Path

CM_DIR = Path(__file__).resolve().parent.parent / "CM"

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
MEMBER_DIV_PATTERN = re.compile(
    r'<div\s+class="member">\s*(.*?)\s*</div>', re.IGNORECASE | re.DOTALL
)


def generate_members_json():
    html = (CM_DIR / "members.html").read_text(encoding="utf-8")
    usernames = [m.group(1).strip() for m in MEMBER_DIV_PATTERN.finditer(html)]

    if not usernames:
        raise SystemExit("No <div class=\"member\"> entries found in members.html - aborting, refusing to overwrite members.json with an empty list.")

    out_path = CM_DIR / "members.json"
    out_path.write_text(json.dumps(usernames, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} with {len(usernames)} member(s): {usernames}")


def generate_banlist_json():
    html = (CM_DIR / "banlist.html").read_text(encoding="utf-8")

    seen = set()
    uuids = []
    for match in UUID_PATTERN.finditer(html):
        uuid = match.group(0).lower()
        if uuid not in seen:
            seen.add(uuid)
            uuids.append(uuid)

    if not uuids:
        raise SystemExit("No UUIDs found in banlist.html - aborting, refusing to overwrite banlist.json with an empty list.")

    out_path = CM_DIR / "banlist.json"
    out_path.write_text(json.dumps(uuids, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} with {len(uuids)} UUID(s).")


if __name__ == "__main__":
    generate_members_json()
    generate_banlist_json()
