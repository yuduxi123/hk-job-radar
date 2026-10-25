#!/usr/bin/env python3
"""Validate an evidence matrix and grade eligibility; no network or LLM calls."""
import argparse
import json
from pathlib import Path

def evaluate(data):
    if not isinstance(data, dict):
        raise ValueError("Expected an object")
    if data.get("status") not in {"open", "closed", "expired", "unverified", "inaccessible"}:
        raise ValueError("Invalid job status")
    if not isinstance(data.get("core_match"), bool):
        raise ValueError("core_match must be a boolean")
    requirements = data.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("A nonempty requirements matrix is required")
    for r in requirements:
        if not isinstance(r, dict) or not isinstance(r.get("hard"), bool):
            raise ValueError("Each requirement needs boolean hard")
        if r.get("state") not in {"met", "unknown", "not_met"}:
            raise ValueError("Invalid evidence state")
        for field in ["requirement", "evidence"]:
            if not isinstance(r.get(field), str) or not r[field].strip():
                raise ValueError("Each requirement needs text and evidence")
    conflicts = [r["requirement"] for r in requirements if r["hard"] and r["state"] == "not_met"]
    unknown = [r["requirement"] for r in requirements if r["hard"] and r["state"] == "unknown"]
    if data["status"] in {"closed", "expired"} or conflicts or not data["core_match"]:
        grade = "C"
    elif data["status"] != "open" or unknown:
        grade = "B"
    else:
        grade = "A"
    return dict(grade=grade, hard_conflicts=conflicts, hard_unknown=unknown,
                recommendable=grade != "C", note="Evidence-based triage, not an offer probability")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
