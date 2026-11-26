#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261125 entry.

The picture itself is the deliverable: this program validates the
bundled entry.png (intact PNG, contest size limits) and copies it to
the output directory the runner provides.
"""

import os
import struct
import sys
import zlib

LIMIT_BYTES = 1024 * 1024
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_TAIL = b"IEND\xaeB`\x82"


def fail(message):
    print(f"entry: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_image_bytes():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    with open(path, "rb") as handle:
        return handle.read()


def check_image(data):
    if len(data) > LIMIT_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the {LIMIT_BYTES} byte limit")
    if not data.startswith(PNG_MAGIC):
        fail("entry.png does not start with the PNG signature")
    if not data.endswith(IEND_TAIL):
        fail("entry.png does not end with a complete IEND chunk")
    # The first chunk must be a 13-byte IHDR: length(4) type(4) data(13).
    ihdr_length, ihdr_type = struct.unpack(">I4s", data[8:16])
    if ihdr_type != b"IHDR" or ihdr_length != 13:
        fail("the first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        fail(f"entry.png is {width}x{height}, expected "
             f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}")
    # The IHDR CRC sits right after its 13 data bytes (offset 29..33)
    # and covers the chunk type plus data (offset 12..29).
    stored_crc, = struct.unpack(">I", data[29:33])
    if zlib.crc32(data[12:29]) & 0xFFFFFFFF != stored_crc:
        fail("the IHDR CRC does not match its contents")


def main():
    data = load_image_bytes()
    check_image(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    if os.path.getsize(target) != len(data):
        fail("the written file does not match the source size")
    print(f"wrote {target} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
