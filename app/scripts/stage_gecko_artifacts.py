#!/usr/bin/env python3
"""Stage Gecko / SpiderMonkey build artifacts for the HarmonyOS HSP.

Copies native libraries and public JS headers out of the out-of-tree build
directory into ``build/gecko/artifacts`` and, optionally, into the HSP
``gecko/src/main/libs/arm64-v8a`` folder, then writes ``manifest.json`` with
size, ABI and SHA-256 for every staged file.

The script never fabricates artifacts: when the build produced nothing it
reports ``MISSING`` and exits 0 unless ``--strict`` is given.

Run with the SDK Python (it avoids stdlib modules that are missing there):
    $DEVECO_SDK_HOME/default/openharmony/native/llvm/python3/bin/python3 \
        scripts/stage_gecko_artifacts.py --copy
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gecko_tooling import (  # noqa: E402
    copy_file,
    elf_info,
    ensure_dir,
    relative_depth,
    run_command,
    sha256_file,
    walk_files,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OBJ_DIR = os.path.join(PROJECT_ROOT, "build", "gecko", "obj-aarch64-ohos")
DEFAULT_ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "build", "gecko", "artifacts")
DEFAULT_LIBS_DIR = os.path.join(PROJECT_ROOT, "gecko", "src", "main", "libs", "arm64-v8a")
# hvigor ProcessLibs only collects prebuilt libs from <module>/libs/<abi>.
DEFAULT_PACK_LIBS_DIR = os.path.join(PROJECT_ROOT, "gecko", "libs", "arm64-v8a")

# Libraries that matter for the milestones defined in plan.md.
KNOWN_LIBRARIES = [
    "libmozjs.so",
    "libxul.so",
    "libmozglue.so",
    "libnss3.so",
    "libnspr4.so",
    "libplc4.so",
    "libplds4.so",
    "libsmime3.so",
    "libssl3.so",
]


def find_libraries(obj_dir):
    """Locate known libraries, preferring the shallowest build paths."""
    found = {}
    if not os.path.isdir(obj_dir):
        return found
    wanted = set(KNOWN_LIBRARIES)
    for path in walk_files(obj_dir):
        name = os.path.basename(path)
        if name not in wanted:
            continue
        current = found.get(name)
        if current is None or relative_depth(path, obj_dir) < relative_depth(current, obj_dir):
            found[name] = path
    return found


def find_js_headers(obj_dir):
    """Return the directory containing jsapi.h (Mozilla dist include layout)."""
    best = None
    if not os.path.isdir(obj_dir):
        return None
    for path in walk_files(obj_dir):
        if os.path.basename(path) != "jsapi.h":
            continue
        if best is None or relative_depth(path, obj_dir) < relative_depth(best, obj_dir):
            best = path
    return os.path.dirname(best) if best else None


def copy_tree_headers(source, destination):
    count = 0
    ensure_dir(destination)
    for path in walk_files(source):
        relative = os.path.relpath(path, source)
        copy_file(path, os.path.join(destination, relative))
        count += 1
    return count


def tool_version(command, log_path):
    code, output = run_command(command, log_path=log_path)
    if code != 0 or not output.strip():
        return "unavailable"
    return output.strip().splitlines()[0]


def build_manifest(args, libraries, header_dir, header_count):
    sdk_home = os.environ.get("DEVECO_SDK_HOME", "")
    clang = os.path.join(sdk_home, "default/openharmony/native/llvm/bin/clang++") if sdk_home else ""
    cmake = os.path.join(sdk_home, "default/openharmony/native/build-tools/cmake/bin/cmake") if sdk_home else ""
    rustc = os.path.join(os.path.expanduser("~"), ".harmonybrew", "bin", "rustc")
    log_path = os.path.join(args.artifacts_dir, ".toolchain-version.log")

    entries = []
    for name in sorted(libraries):
        path = libraries[name]
        info = elf_info(path)
        entries.append({
            "name": name,
            "source": path,
            "size": os.path.getsize(path),
            "sha256": sha256_file(path),
            "abi": info.get("machine"),
            "elfClass": info.get("elfClass"),
        })

    missing = [name for name in KNOWN_LIBRARIES if name not in libraries]
    manifest = {
        "schemaVersion": 1,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "firefoxBaseline": args.baseline,
        "targetAbi": "arm64-v8a",
        "objDir": args.obj_dir,
        "artifactsDir": args.artifacts_dir,
        "hspLibsDir": args.libs_dir,
        "toolchain": {
            "clang": tool_version([clang, "--version"], log_path) if clang else "unavailable",
            "cmake": tool_version([cmake, "--version"], log_path) if cmake else "unavailable",
            "rustc": tool_version([rustc, "--version"], log_path),
            "python": sys.version.split()[0],
        },
        "libraries": entries,
        "headers": {
            "sourceDir": header_dir,
            "fileCount": header_count,
        },
        "missing": missing,
        "status": "complete" if not missing else "partial",
    }
    if os.path.exists(log_path):
        os.unlink(log_path)
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Stage Gecko artifacts for the HSP")
    parser.add_argument("--obj-dir", default=DEFAULT_OBJ_DIR)
    parser.add_argument("--artifacts-dir", default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--libs-dir", default=DEFAULT_LIBS_DIR)
    parser.add_argument("--pack-libs-dir", default=DEFAULT_PACK_LIBS_DIR,
                        help="hvigor packaging location (<module>/libs/<abi>)")
    parser.add_argument("--baseline", default="unpinned-m0", help="Firefox baseline recorded in the manifest")
    parser.add_argument("--no-copy", action="store_true", help="Only write the manifest, do not copy into the HSP")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any known library is missing")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    args.obj_dir = os.path.abspath(args.obj_dir)
    args.artifacts_dir = os.path.abspath(args.artifacts_dir)
    args.libs_dir = os.path.abspath(args.libs_dir)

    ensure_dir(args.artifacts_dir)

    libraries = find_libraries(args.obj_dir)
    header_dir = find_js_headers(args.obj_dir)
    manifest_path = os.path.join(args.artifacts_dir, "manifest.json")

    if not libraries:
        print("MISSING: no known libraries under %s" % args.obj_dir)
        print("         run scripts/build_gecko.sh --target js first (see m1-report.md for blockers)")
        manifest = build_manifest(args, {}, None, 0)
        with open(manifest_path, "w") as handle:
            json.dump(manifest, handle, indent=2)
        print("manifest: %s (status=%s)" % (manifest_path, manifest["status"]))
        return 1 if args.strict else 0

    staged = []
    for name in sorted(libraries):
        source = libraries[name]
        copy_file(source, os.path.join(args.artifacts_dir, name))
        staged.append(name)
        if not args.no_copy:
            ensure_dir(args.libs_dir)
            copy_file(source, os.path.join(args.libs_dir, name))
            ensure_dir(args.pack_libs_dir)
            copy_file(source, os.path.join(args.pack_libs_dir, name))
            print("copied %s -> %s" % (name, args.libs_dir))
            print("copied %s -> %s" % (name, args.pack_libs_dir))

    header_count = 0
    if header_dir is not None:
        header_count = copy_tree_headers(header_dir, os.path.join(args.artifacts_dir, "include"))
        if not args.no_copy:
            copy_tree_headers(header_dir, os.path.join(args.libs_dir, "include"))

    manifest = build_manifest(args, libraries, header_dir, header_count)
    with open(manifest_path, "w") as handle:
        json.dump(manifest, handle, indent=2)

    print("staged %d libraries: %s" % (len(staged), ", ".join(staged)))
    print("headers: %d files from %s" % (header_count, header_dir))
    print("manifest: %s (status=%s)" % (manifest_path, manifest["status"]))
    if manifest["missing"]:
        print("MISSING: %s" % ", ".join(manifest["missing"]))
    if args.strict and manifest["missing"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
