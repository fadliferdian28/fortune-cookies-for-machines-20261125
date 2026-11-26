#!/usr/bin/env python3
"""Copy the verified fortune line to MAKEFUN_OUTPUT_DIR."""

import hashlib
import os
import pathlib
import shutil
import sys

EXPECTED_SHA256 = "e0c3ed55078668542218b3b23870976b5e24b4cdf2e20fc6b7114c749b264744"

ENTRY_NAME = "entry.txt"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def main():
    entry_path = pathlib.Path(__file__).resolve().parent / ENTRY_NAME
    if not entry_path.is_file():
        return fail(f"missing {ENTRY_NAME} next to main.py ({entry_path})")

    raw = entry_path.read_bytes()

    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        return fail(
            f"sha256 mismatch for {ENTRY_NAME}: expected {EXPECTED_SHA256}, got {actual_sha}"
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(f"{ENTRY_NAME} is not valid UTF-8: {exc}")

    if "\n" in text or "\r" in text:
        return fail(f"{ENTRY_NAME} must be a single line with no newline")

    count = len(text)
    if count < 1 or count > 200:
        return fail(f"{ENTRY_NAME} must be 1-200 characters, got {count}")
    if not text.strip():
        return fail(f"{ENTRY_NAME} is whitespace-only")

    out_dir_env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir_env:
        return fail(
            "MAKEFUN_OUTPUT_DIR is not set; set it to the directory that should receive entry.txt"
        )

    out_dir = pathlib.Path(out_dir_env)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ENTRY_NAME

    if not os.access(out_dir, os.W_OK):
        return fail(f"output directory is not writable: {out_dir}")

    try:
        shutil.copyfile(entry_path, out_path)
    except shutil.SameFileError:
        print(f"note: {out_path} is the same file as the source; nothing to copy")
        print(f"characters: {count}")
        print(f"sha256: {actual_sha}")
        return 0
    except OSError as exc:
        return fail(f"could not write {out_path}: {exc}")

    print(f"characters: {count}")
    print(f"sha256: {actual_sha}")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
