#!/usr/bin/env python3
"""Fetch the Firefox/Gecko source tree and apply the OHOS patch queue.

Design constraints:
  * never fabricate source - when the network or the baseline is missing the
    script exits with code 2 and an actionable message;
  * the repository URL is NOT hardcoded: supply ``--repo`` or set
    ``GECKO_REPO_URL``. This keeps the tool free of guessed mirrors;
  * patches are applied in filename order, and placeholder patches (no
    ``diff --git`` line) are reported as SKIPPED instead of failing the run.

Usage:
    $DEVECO_SDK_HOME/.../python3 scripts/fetch_gecko.py --repo <url> --tag <tag>
    scripts/fetch_gecko.py --tag ESR_140_0_RELEASE          # uses GECKO_REPO_URL
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gecko_tooling import ensure_dir, run_command  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(PROJECT_ROOT, "third_party", "gecko", "source")
PATCH_DIR = os.path.join(PROJECT_ROOT, "third_party", "gecko", "patches")
BASELINE_FILE = os.path.join(PROJECT_ROOT, "third_party", "gecko", "baseline.json")
REPORT_FILE = os.path.join(PROJECT_ROOT, "build", "gecko", "artifacts", "fetch-report.md")

GIT = os.path.join(os.path.expanduser("~"), ".harmonybrew", "bin", "git")


def read_baseline():
    if not os.path.isfile(BASELINE_FILE):
        return {}
    try:
        with open(BASELINE_FILE, "r") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


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


def is_placeholder(patch_path):
    try:
        with open(patch_path, "r") as handle:
            content = handle.read()
    except OSError:
        return True
    return "diff --git" not in content


def apply_patches(report):
    git = git_binary()
    applied = []
    skipped = []
    failed = []
    for patch in list_patches():
        name = os.path.basename(patch)
        if is_placeholder(patch):
            skipped.append(name + " (placeholder, no diff)")
            continue
        check_code, _ = run_command([git, "apply", "--check", patch], workdir=SOURCE_DIR)
        if check_code != 0:
            failed.append(name + " (apply --check failed)")
            continue
        code, _ = run_command([git, "apply", patch], workdir=SOURCE_DIR)
        if code == 0:
            applied.append(name)
        else:
            failed.append(name + " (apply failed)")
    report["applied"] = applied
    report["skipped"] = skipped
    report["failed"] = failed
    return failed


def write_report(report):
    ensure_dir(os.path.dirname(REPORT_FILE))
    lines = [
        "# Gecko fetch report",
        "",
        "- generated: %s" % report.get("generatedAt", ""),
        "- baseline tag: %s" % report.get("tag", ""),
        "- source dir: %s" % SOURCE_DIR,
        "- status: %s" % report.get("status", ""),
        "",
        "## applied patches",
    ]
    for item in report.get("applied", []):
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## skipped patches")
    for item in report.get("skipped", []):
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## failed patches")
    for item in report.get("failed", []):
        lines.append("- %s" % item)
    lines.append("")
    lines.append("## blocker")
    lines.append(report.get("blocker", "none"))
    with open(REPORT_FILE, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch Gecko source and apply OHOS patches")
    parser.add_argument("--repo", default=os.environ.get("GECKO_REPO_URL", ""),
                        help="Git repository URL (or set GECKO_REPO_URL); not hardcoded on purpose")
    parser.add_argument("--tag", default="", help="Baseline tag/branch to check out")
    parser.add_argument("--force", action="store_true", help="Remove an existing source tree first")
    parser.add_argument("--no-patches", action="store_true", help="Clone only, do not apply patches")
    parser.add_argument("--depth", default="1", help="Clone depth (default 1 for a bring-up checkout)")
    args = parser.parse_args(argv)

    import time

    baseline = read_baseline()
    tag = args.tag or baseline.get("tag", "")
    report = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tag": tag,
        "status": "blocked",
        "applied": [],
        "skipped": [],
        "failed": [],
        "blocker": "",
    }

    if not tag:
        report["blocker"] = ("no baseline tag: pass --tag or set third_party/gecko/baseline.json "
                            "(M0 must lock the latest ESR before fetching)")
        write_report(report)
        print("BLOCKED: %s" % report["blocker"])
        return 2

    ensure_dir(os.path.dirname(SOURCE_DIR))

    if os.path.isdir(SOURCE_DIR) and os.listdir(SOURCE_DIR):
        if args.force:
            print("==> removing existing source tree (--force)")
            run_command(["rm", "-rf", SOURCE_DIR])
        else:
            print("==> source tree already present, skipping clone: %s" % SOURCE_DIR)

    if not os.path.isdir(SOURCE_DIR) or not os.listdir(SOURCE_DIR):
        if not args.repo:
            report["blocker"] = ("no repository URL: pass --repo or set GECKO_REPO_URL "
                                "(the URL is intentionally not hardcoded)")
            write_report(report)
            print("BLOCKED: %s" % report["blocker"])
            return 2

        print("==> git clone --depth %s --branch %s" % (args.depth, tag))
        code, output = run_command(
            [git_binary(), "clone", "--depth", args.depth, "--branch", tag, args.repo, SOURCE_DIR])
        if code != 0:
            report["blocker"] = ("git clone failed (exit %s); network or tag/URL problem. "
                                "See the console output for the git error." % code)
            write_report(report)
            print("BLOCKED: %s" % report["blocker"])
            print(output)
            return 2

    if args.no_patches:
        report["status"] = "cloned"
        write_report(report)
        print("==> cloned without patches")
        return 0

    failed = apply_patches(report)
    report["status"] = "patched" if not failed else "patched-with-failures"
    if failed:
        report["blocker"] = "some patches failed; see the failed list"
    write_report(report)

    print("==> applied: %d, skipped: %d, failed: %d"
          % (len(report["applied"]), len(report["skipped"]), len(report["failed"])))
    print("==> report: %s" % REPORT_FILE)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
