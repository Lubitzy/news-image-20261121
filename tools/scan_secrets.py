"""Scan the working folder and every stored Git object without printing secrets.

This bounded pattern scan supplements review; it cannot prove the absence of
all possible secrets. Matching values and their encoded forms are never shown.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private-key-block": re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "github-token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
    "provider-token": re.compile(rb"\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|af_[A-Za-z0-9_-]{20,})"),
    "aws-access-key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "google-api-key": re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "secret-assignment": re.compile(
        rb"(?i)(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*[\"']([A-Za-z0-9/_+.-]{16,})[\"']"
    ),
    "possible-keypair-array": re.compile(rb"\[(?:\s*\d{1,3}\s*,){31,63}\s*\d{1,3}\s*\]"),
}


def findings(data: bytes) -> list[str]:
    return [label for label, pattern in PATTERNS.items() if pattern.search(data)]


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          check=True, timeout=60).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    hits = []
    file_count = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(ROOT).parts:
            continue
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        name = path.name.lower()
        if name == ".env" or name.startswith(".env.") or name in {"credentials", "auth.json"} or "keypair" in name:
            hits.append({"scope": "working-folder", "file": relative,
                         "rule": "sensitive-filename"})
        file_count += 1
        for rule in findings(path.read_bytes()):
            hits.append({"scope": "working-folder", "file": relative, "rule": rule})
    # Includes reachable history and any dangling objects still in this repository.
    objects = git("cat-file", "--batch-all-objects", "--batch-check").decode("ascii").splitlines()
    object_count = 0
    for ordinal, line in enumerate(objects, 1):
        object_id, object_type, _size = line.split()
        object_count += 1
        for rule in findings(git("cat-file", "-p", object_id)):
            hits.append({"scope": "git-object", "object_ordinal": ordinal,
                         "object_type": object_type, "rule": rule})
    report = {"status": "pass" if not hits else "stop", "working_files_scanned": file_count,
              "all_git_objects_scanned": object_count, "findings": hits,
              "matching_values_printed": False,
              "limitation": "Known-pattern and sensitive-filename scan, not a proof of absence"}
    serialized = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    if hits:
        sys.exit(1)


if __name__ == "__main__":
    main()
