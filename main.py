#!/usr/bin/env python3
"""news-image-20261125 entrypoint.

Copies the bundled front-page image (entry.png, 1024x1024, rendered from
Wednesday 25 November 2026's sourced news by render25.py) to the output
path, after verifying it is a whole, in-limits PNG: correct magic, an
IHDR first chunk, an exact IEND trailer, the declared 1024x1024
dimensions, and at most 1 MiB. No network, no randomness, no clock:
the same bytes are written on every run.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
WANT_W, WANT_H = 1024, 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_TRAILER = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def load_checked():
    try:
        with open(SOURCE, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        fail("cannot read bundled entry.png: %s" % exc)
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))
    if data[:8] != PNG_MAGIC:
        fail("entry.png is not a PNG (bad magic)")
    if data[12:16] != b"IHDR":
        fail("entry.png has no IHDR first chunk")
    if not data.endswith(IEND_TRAILER):
        fail("entry.png has no exact IEND trailer")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WANT_W, WANT_H):
        fail("entry.png is %dx%d, want 1024x1024" % (width, height))
    return data, width, height


def main():
    data, width, height = load_checked()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(data)
    if os.path.getsize(target) != len(data):
        fail("written file size does not match the bundled image")
    print("wrote %s (%d bytes, %dx%d)" % (target, len(data), width, height))


if __name__ == "__main__":
    main()
