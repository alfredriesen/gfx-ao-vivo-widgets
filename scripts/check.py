#!/usr/bin/env python3
"""Checks registry.json the way the app reads it: every entry is complete,
each ZIP has the listed SHA-256 and a manifest.json with the entry's name and
version, and each preview exists. Exits non-zero on the first problem list."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = ["name", "displayName", "description", "category", "version", "zip", "sha256", "author"]


def local(link, problems, where):
    """A link relative to registry.json, as a path, or None for an https URL."""
    url = urlparse(link)
    if url.scheme == "https":
        return None
    if url.scheme or link.startswith("/") or ".." in Path(link).parts:
        problems.append(f"{where}: {link} must be a path inside this repo or an https:// URL")
        return None
    return ROOT / link


def zip_manifest(data):
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as z:
        names = [n for n in z.namelist() if n.endswith("manifest.json")]
        if not names:
            raise ValueError("manifest.json not found in ZIP")
        return json.loads(z.read(names[0]))


def check(registry):
    problems = []
    seen = set()
    for i, entry in enumerate(registry.get("widgets", [])):
        where = f"widgets[{i}] ({entry.get('name', '?')})"
        missing = [k for k in REQUIRED if not entry.get(k)]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if not NAME.match(entry["name"]):
            problems.append(f"{where}: name may only use a-z, 0-9, - and _")
        if entry["name"] in seen:
            problems.append(f"{where}: listed twice")
        seen.add(entry["name"])
        if not SHA256.match(entry["sha256"]):
            problems.append(f"{where}: sha256 must be 64 lowercase hex digits")
        if not isinstance(entry.get("official", False), bool):
            problems.append(f"{where}: official must be true or false")
        zip_path = local(entry["zip"], problems, where)
        if zip_path is not None:
            if not zip_path.is_file():
                problems.append(f"{where}: {entry['zip']} is missing")
            else:
                data = zip_path.read_bytes()
                if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    problems.append(f"{where}: sha256 does not match {entry['zip']} (run ./pack.sh again)")
                try:
                    m = zip_manifest(data)
                    if (m.get("name"), m.get("version")) != (entry["name"], entry["version"]):
                        problems.append(f"{where}: the ZIP's manifest is {m.get('name')} {m.get('version')}")
                except Exception as e:  # noqa: BLE001 - any broken ZIP is a problem to report
                    problems.append(f"{where}: {entry['zip']}: {e}")
        if entry.get("preview"):
            preview = local(entry["preview"], problems, where)
            if preview is not None and not preview.is_file():
                problems.append(f"{where}: {entry['preview']} is missing")
    listed = {(ROOT / e["zip"]).resolve() for e in registry.get("widgets", []) if e.get("zip")}
    for z in sorted((ROOT / "widgets").glob("*.zip")):
        if z.resolve() not in listed:
            problems.append(f"widgets/{z.name} is not listed in registry.json (delete it)")
    return problems


if __name__ == "__main__":
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    problems = check(registry)
    for p in problems:
        print(f"::error::{p}")
    print(f"{len(registry.get('widgets', []))} widgets, {len(problems)} problems")
    sys.exit(1 if problems else 0)
