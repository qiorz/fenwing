#!/usr/bin/env python3
"""Verify the native library bundle that ships inside the `gecko` HSP.

Checks performed:
  1. every ``.so`` is a 64-bit AArch64 ELF (matching abiFilters arm64-v8a);
  2. ``libohos_smoke.so`` exports ``ohos_rust_add`` (M0 Rust bridge);
  3. ``libmozjs.so`` exports SpiderMonkey runtime entry points (M1);
  4. ``libgecko_napi.so`` declares DT_NEEDED ``libace_napi.z.so`` / ``libhilog_ndk.z.so``;
  5. ``manifest.json`` SHA-256 values match the staged files.

Exit code is 1 only when a check fails; absent optional libraries are reported
as MISSING/SKIP so an M0-only bundle still validates.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gecko_tooling import elf_info, run_command, sha256_file  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LIBS_DIR = os.path.join(PROJECT_ROOT, "gecko", "src", "main", "libs", "arm64-v8a")
DEFAULT_MANIFEST = os.path.join(PROJECT_ROOT, "build", "gecko", "artifacts", "manifest.json")

ELF_MACHINE_AARCH64 = 0xB7

REQUIRED_EXPORTS = {
    "libohos_smoke.so": ["ohos_rust_add"],
    "libmozjs.so": ["JS_NewRuntime", "JS_NewContext", "JS_EvaluateScript"],
}

REQUIRED_NEEDED = {
    "libgecko_napi.so": ["libace_napi.z.so", "libhilog_ndk.z.so"],
}


def find_tool(name, explicit):
    if explicit:
        return explicit if os.path.isfile(explicit) else ""
    sdk_home = os.environ.get("DEVECO_SDK_HOME", "")
    candidates = []
    if sdk_home:
        candidates.append(os.path.join(sdk_home, "default/openharmony/native/llvm/bin", name))
    candidates.append(os.path.join(os.path.expanduser("~"), ".harmonybrew", "opt", "llvm@22", "bin", name))
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return ""


def capture(tool, flags, path, scratch):
    code, output = run_command([tool] + flags + [path], log_path=scratch)
    if code != 0:
        return ""
    return output


def dynamic_symbols(readelf, path, scratch):
    symbols = set()
    for flags in (["--dyn-syms", "--wide"], ["-s", "--wide"]):
        output = capture(readelf, flags, path, scratch)
        if not output:
            continue
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 8 or not parts[0].endswith(":"):
                continue
            name = parts[-1]
            if name in ("Name", "Ndx"):
                continue
            symbols.add(name.split("@")[0])
        if symbols:
            break
    return symbols


def needed_libraries(readelf, path, scratch):
    output = capture(readelf, ["-d", "--wide"], path, scratch)
    needed = set()
    for line in output.splitlines():
        match = re.search(r"Shared library:\s*\[(.+?)\]", line)
        if match:
            needed.add(match.group(1))
    return needed


def load_manifest(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    entries = {}
    for entry in data.get("libraries", []):
        name = entry.get("name")
        if isinstance(name, str):
            entries[name] = entry
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify the gecko HSP native bundle")
    parser.add_argument("--libs", default=DEFAULT_LIBS_DIR)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--readelf", default=None, help="Explicit llvm-readelf path")
    parser.add_argument("--strict", action="store_true", help="Fail when libohos_smoke.so / libmozjs.so are missing")
    args = parser.parse_args(argv)

    libs_dir = os.path.abspath(args.libs)
    manifest_path = os.path.abspath(args.manifest)
    scratch = os.path.join(PROJECT_ROOT, "build", "gecko", "artifacts", ".verify-scratch.log")

    library_files = []
    if os.path.isdir(libs_dir):
        for name in sorted(os.listdir(libs_dir)):
            if name.endswith(".so"):
                library_files.append(os.path.join(libs_dir, name))

    readelf = find_tool("llvm-readelf", args.readelf)
    manifest = load_manifest(manifest_path)

    rows = []
    failures = 0

    if not library_files:
        rows.append("MISSING  <no .so staged in %s>" % libs_dir)
        print("\n".join(rows))
        if args.strict:
            print("FAIL: strict mode requires libohos_smoke.so")
            return 1
        print("SKIP: bundle is empty (M0 Rust/JS artifacts not built)")
        return 0

    for path in library_files:
        name = os.path.basename(path)
        info = elf_info(path)
        if "error" in info:
            rows.append("FAIL     %-18s %s" % (name, info["error"]))
            failures += 1
            continue
        if not info.get("is64Bit") or info.get("machineId") != ELF_MACHINE_AARCH64:
            rows.append("FAIL     %-18s machine=%s, expected 64-bit AArch64" % (name, info.get("machine")))
            failures += 1
            continue
        rows.append("PASS     %-18s ELF64 AArch64  %d bytes" % (name, os.path.getsize(path)))

        if readelf:
            symbols = dynamic_symbols(readelf, path, scratch)
            for symbol in REQUIRED_EXPORTS.get(name, []):
                if symbol in symbols:
                    rows.append("PASS     %-18s exports %s" % (name, symbol))
                else:
                    rows.append("MISSING  %-18s export %s" % (name, symbol))
                    if name == "libohos_smoke.so":
                        failures += 1
            if REQUIRED_NEEDED.get(name):
                needed = needed_libraries(readelf, path, scratch)
                for library in REQUIRED_NEEDED[name]:
                    if library in needed:
                        rows.append("PASS     %-18s DT_NEEDED %s" % (name, library))
                    else:
                        rows.append("FAIL     %-18s DT_NEEDED %s absent" % (name, library))
                        failures += 1
        else:
            rows.append("SKIP     %-18s symbol checks (llvm-readelf not found)" % name)

        if manifest:
            entry = manifest.get(name)
            if entry is None:
                rows.append("SKIP     %-18s not part of the Gecko manifest" % name)
            else:
                expected = entry.get("sha256")
                actual = sha256_file(path)
                if expected == actual:
                    rows.append("PASS     %-18s sha256 matches manifest" % name)
                else:
                    rows.append("FAIL     %-18s sha256 mismatch (manifest=%s actual=%s)"
                                % (name, expected, actual))
                    failures += 1

    if args.strict:
        for name in REQUIRED_EXPORTS:
            if not os.path.isfile(os.path.join(libs_dir, name)):
                rows.append("MISSING  %-18s required in strict mode" % name)
                failures += 1

    if os.path.exists(scratch):
        os.unlink(scratch)

    print("\n".join(rows))
    if failures:
        print("\nFAIL: %d check(s) failed" % failures)
        return 1
    print("\nPASS: native bundle verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
