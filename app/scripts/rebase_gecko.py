#!/usr/bin/env python3
"""Replay the OHOS patch queue on a new Gecko baseline.

Flow:
  1. verify the source tree exists and is a git checkout;
  2. fetch the target ref (or use an existing local ref);
  3. optionally check out the target and replay every patch in
     third_party/gecko/patches in filename order;
  4. write build/gecko/artifacts/rebase-report.md with applied / conflicted /
     skipped patches and the recommended next action.

``--dry-run`` only runs ``git apply --check`` against the current worktree, so a
release manager can estimate the conflict surface without touching the tree.

Placeholder patches (no ``diff --git`` line) are reported as SKIPPED, matching
scripts/fetch_gecko.py.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gecko_tooling import ensure_dir, run_command  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(PROJECT_ROOT, "third_party", "gecko", "source")
PATCH_DIR = os.path.join(PROJECT_ROOT, "third_party", "gecko", "patches")
BASELINE_FILE = os.path.join(PROJECT_ROOT, "third_party", "gecko", "baseline.json")
REPORT_FILE = os.path.join(PROJECT_ROOT, "build", "gecko", "artifacts", "rebase-report.md")
GIT = os.path.join(os.path.expanduser("~"), ".harmonybrew", "bin", "git")


def git_binary():
    if os.path.isfile(GIT) and os.access(GIT, os.X_OK):
        return GIT
    return "git"


def list_patches():
    if not os.path.isdir(PATCH_DIR):
        return []
    return sorted(
        os.path.join(PATCH_DIR, name)
        for name in os.listdir(PATCH_DIR)
        if name.endswith(".patch")
    )


def is_placeholder(path):
    try:
        with open(path, "r") as handle:
            content = handle.read()
    except OSError:
        return True
    return "diff --git" not in content


def read_baseline():
    if not os.path.isfile(BASELINE_FILE):
        return {}
    try:
        with open(BASELINE_FILE, "r") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def write_report(report):
    ensure_dir(os.path.dirname(REPORT_FILE))
    lines = [
        "# Gecko rebase report",
        "",
        "- generated: %s" % report["generatedAt"],
        "- target: %s" % report["target"],
        "- mode: %s" % report["mode"],
        "- status: %s" % report["status"],
        "",
        "## applied",
    ]
    for item in report["applied"]:
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## conflicted")
    for item in report["conflicted"]:
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## skipped (placeholder)")
    for item in report["skipped"]:
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## next action")
    lines.append(report["nextAction"])
    with open(REPORT_FILE, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rebase the OHOS patch queue onto a new Gecko baseline")
    parser.add_argument("--to", required=True, help="Target tag/branch/commit")
    parser.add_argument("--repo", default=os.environ.get("GECKO_REPO_URL", ""),
                        help="Optional remote to fetch from (not hardcoded on purpose)")
    parser.add_argument("--dry-run", action="store_true", help="Only check patch applicability")
    parser.add_argument("--keep-going", action="store_true", help="Continue after the first conflict")
    args = parser.parse_args(argv)

    report = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": args.to,
        "mode": "dry-run" if args.dry_run else "apply",
        "status": "blocked",
        "applied": [],
        "conflicted": [],
        "skipped": [],
        "nextAction": "",
    }

    if not os.path.isdir(SOURCE_DIR) or not os.path.isfile(os.path.join(SOURCE_DIR, ".git", "HEAD")):
        report["nextAction"] = "run scripts/fetch_gecko.py first; no git checkout found"
        write_report(report)
        print("BLOCKED: %s" % report["nextAction"])
        return 2

    git = git_binary()

    if args.repo:
        print("==> git fetch %s" % args.repo)
        code, _ = run_command([git, "fetch", args.repo, "--tags"], workdir=SOURCE_DIR)
        if code != 0:
            report["nextAction"] = "git fetch failed; check network/credentials"
            write_report(report)
            print("BLOCKED: fetch failed")
            return 2

    if not args.dry_run:
        print("==> git checkout %s" % args.to)
        code, _ = run_command([git, "checkout", args.to], workdir=SOURCE_DIR)
        if code != 0:
            report["nextAction"] = "target ref not found locally; pass --repo or fetch it first"
            write_report(report)
            print("BLOCKED: checkout failed")
            return 2

    for patch in list_patches():
        name = os.path.basename(patch)
        if is_placeholder(patch):
            report["skipped"].append(name)
            continue
        check_code, _ = run_command([git, "apply", "--check", patch], workdir=SOURCE_DIR)
        if check_code != 0:
            report["conflicted"].append(name)
            if not args.keep_going:
                break
            continue
        if args.dry_run:
            report["applied"].append(name + " (check only)")
            continue
        apply_code, _ = run_command([git, "apply", patch], workdir=SOURCE_DIR)
        if apply_code == 0:
            report["applied"].append(name)
        else:
            report["conflicted"].append(name + " (apply failed)")
            if not args.keep_going:
                break

    if report["conflicted"]:
        report["status"] = "conflicts"
        report["nextAction"] = ("resolve each conflicted patch manually, regenerate it with "
                               "'git diff > patches/<name>.patch', then update baseline.json")
    else:
        report["status"] = "clean"
        report["nextAction"] = ("update third_party/gecko/baseline.json with the new tag/commit, "
                               "then run the regression checklist in upstream-maintenance.md")

    write_report(report)
    print("==> applied=%d conflicted=%d skipped=%d"
          % (len(report["applied"]), len(report["conflicted"]), len(report["skipped"])))
    print("==> report: %s" % REPORT_FILE)
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
