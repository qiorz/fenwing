#!/usr/bin/env python3
"""Shared helpers for the Gecko staging / verification scripts.

Why this file exists: the HarmonyOS SDK Python 3.12.10 on this device ships an
EMPTY ``lib-dynload`` directory, so ``struct``, ``subprocess``, ``math``,
``binascii`` and ``hashlib.sha256`` are unavailable. These helpers therefore
stick to modules that are known to work (``os``, ``sys``, ``json``, ``re``,
``argparse``, ``time``) and implement ELF parsing / SHA-256 locally.

This keeps ``stage_gecko_artifacts.py`` and ``verify_gecko_bundle.py`` runnable
on the device without a host Python installation.
"""

from __future__ import annotations

import os
import shlex

ELF_MACHINES = {
    0x03: "x86",
    0x28: "ARM",
    0x3E: "x86-64",
    0xB7: "AArch64",
    0xF3: "RISC-V",
}

# ---------------------------------------------------------------------------
# SHA-256 (pure Python fallback, prefer the openssl binary when present)
# ---------------------------------------------------------------------------

_K = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
]

_H0 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]


def _rotr(value: int, shift: int) -> int:
    return ((value >> shift) | (value << (32 - shift))) & 0xFFFFFFFF


def sha256_bytes(data: bytes) -> str:
    """Pure-Python SHA-256. Used only when the openssl binary is unavailable."""
    message = bytearray(data)
    bit_length = len(message) * 8
    message.append(0x80)
    while len(message) % 64 != 56:
        message.append(0)
    message += bit_length.to_bytes(8, "big")

    state = list(_H0)
    for offset in range(0, len(message), 64):
        block = message[offset:offset + 64]
        schedule = [0] * 64
        for index in range(16):
            schedule[index] = int.from_bytes(block[index * 4:index * 4 + 4], "big")
        for index in range(16, 64):
            prev15 = schedule[index - 15]
            prev2 = schedule[index - 2]
            s0 = _rotr(prev15, 7) ^ _rotr(prev15, 18) ^ (prev15 >> 3)
            s1 = _rotr(prev2, 17) ^ _rotr(prev2, 19) ^ (prev2 >> 10)
            schedule[index] = (schedule[index - 16] + s0 + schedule[index - 7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h = state
        for index in range(64):
            s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            choice = (e & f) ^ ((~e & 0xFFFFFFFF) & g)
            temp1 = (h + s1 + choice + _K[index] + schedule[index]) & 0xFFFFFFFF
            s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            majority = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + majority) & 0xFFFFFFFF
            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF
        state = [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]

    return "".join(f"{value:08x}" for value in state)


def find_openssl() -> str:
    candidates = [
        os.path.join(os.path.expanduser("~"), ".harmonybrew", "bin", "openssl"),
        "/usr/bin/openssl",
    ]
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(directory, "openssl")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return ""


def sha256_file(path: str) -> str:
    """SHA-256 of a file. Prefers openssl; falls back to pure Python."""
    openssl = find_openssl()
    if openssl:
        code, output = run_command([openssl, "dgst", "-sha256", path])
        if code == 0:
            marker = "="
            if marker in output:
                digest = output.rsplit(marker, 1)[1].strip()
                if len(digest) == 64:
                    return digest
    with open(path, "rb") as handle:
        return sha256_bytes(handle.read())


# ---------------------------------------------------------------------------
# ELF + process helpers
# ---------------------------------------------------------------------------

def elf_info(path: str) -> dict:
    """Minimal ELF header probe without the ``struct`` module."""
    try:
        with open(path, "rb") as handle:
            header = handle.read(20)
    except OSError as error:
        return {"error": str(error)}
    if len(header) < 20 or header[:4] != b"\x7fELF":
        return {"error": "not an ELF file"}
    elf_class = "ELF64" if header[4] == 2 else "ELF32"
    little_endian = header[5] == 1
    machine = int.from_bytes(header[18:20], "little" if little_endian else "big")
    return {
        "elfClass": elf_class,
        "is64Bit": header[4] == 2,
        "endianness": "little" if little_endian else "big",
        "machine": ELF_MACHINES.get(machine, f"0x{machine:02x}"),
        "machineId": machine,
    }


def run_command(args: list, workdir: str = None, log_path: str = None) -> tuple:
    """Runs a command through /bin/sh and returns (exit_code, output)."""
    command = " ".join(shlex.quote(str(item)) for item in args)
    if workdir:
        command = f"cd {shlex.quote(str(workdir))} && {command}"
    if log_path:
        command = f"{command} > {shlex.quote(str(log_path))} 2>&1"
    status = os.system(command)
    if hasattr(os, "waitstatus_to_exitcode"):
        code = os.waitstatus_to_exitcode(status)
    else:
        code = status
    output = ""
    if log_path and os.path.exists(log_path):
        with open(log_path, "r", errors="replace") as handle:
            output = handle.read()
    return code, output


def ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path)


def copy_file(source: str, destination: str) -> None:
    ensure_dir(os.path.dirname(destination))
    with open(source, "rb") as reader:
        with open(destination, "wb") as writer:
            while True:
                chunk = reader.read(1024 * 1024)
                if not chunk:
                    break
                writer.write(chunk)


def walk_files(root: str):
    """Yields absolute file paths under root (no followlinks)."""
    for current, directories, files in os.walk(root):
        directories.sort()
        for name in sorted(files):
            yield os.path.join(current, name)


def relative_depth(path: str, root: str) -> int:
    relative = os.path.relpath(path, root)
    return len(relative.split(os.sep))
