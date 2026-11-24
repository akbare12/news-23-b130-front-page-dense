#!/usr/bin/env python3
"""news-23 b130 front-page-dense: copy entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR/entry.png.

Stdlib only (no PIL). Never writes next to itself: it writes only to MAKEFUN_OUTPUT_DIR,
so it also works from a read-only copy (with MAKEFUN_OUTPUT_DIR pointed elsewhere).
"""
import hashlib
import os
import struct
import sys
import zlib

SRC_NAME = "entry.png"
MIN_BYTES = 10000
MAX_BYTES = 1024 * 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("error: %s" % msg, file=sys.stderr)
    return 1


def validate_png(data):
    """Validate the PNG header and chunk structure (IHDR 1024x1024, CRCs, IEND last)."""
    if len(data) < MIN_BYTES:
        return "too small: %d bytes" % len(data)
    if len(data) > MAX_BYTES:
        return "too big: %d bytes" % len(data)
    if data[:8] != PNG_SIG:
        return "bad PNG signature"
    # First chunk must be IHDR, 13 bytes: width, height, bit depth, colour type,
    # compression, filter, interlace. Layout: length@8, type@12, data@16, CRC@29.
    if len(data) < 33:
        return "truncated before IHDR"
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        return "first chunk is not a 13-byte IHDR"
    ihdr = data[16:29]
    width, height, bit_depth, colour_type, comp, filt, interlace = struct.unpack(">IIBBBBB", ihdr)
    if (width, height) != (1024, 1024):
        return "expected 1024x1024, got %dx%d" % (width, height)
    if bit_depth != 8 or colour_type not in (2, 6):
        return "expected 8-bit RGB/RGBA, got depth %d type %d" % (bit_depth, colour_type)
    if comp != 0 or filt != 0 or interlace != 0:
        return "expected compression/filter/interlace 0"
    crc_expect = struct.unpack(">I", data[29:33])[0]
    crc_actual = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    if crc_expect != crc_actual:
        return "IHDR CRC mismatch"
    # Walk the remaining chunks: length, type, data, CRC. The next chunk starts
    # at offset 33 (8 signature + 4 length + 4 type + 13 data + 4 CRC = 33),
    # NOT 37: the CRC of IHDR occupies bytes 29..33, so chunk 2 begins at 33.
    pos = 33
    idat_total = 0
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            return "truncated chunk header at %d" % pos
        clen = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        if pos + 12 + clen > len(data):
            return "truncated chunk %s" % ctype.decode("latin1", "replace")
        chunk = data[pos + 4:pos + 8 + clen]
        crc_expect = struct.unpack(">I", data[pos + 8 + clen:pos + 12 + clen])[0]
        if (zlib.crc32(chunk) & 0xFFFFFFFF) != crc_expect:
            return "CRC mismatch in chunk %s" % ctype.decode("latin1", "replace")
        if ctype == b"IDAT":
            if clen == 0:
                return "empty IDAT chunk"
            idat_total += clen
        if ctype == b"IEND":
            if clen != 0:
                return "IEND must be 0 bytes"
            if pos + 12 + clen != len(data):
                return "trailing data after IEND"
            seen_iend = True
            break
        pos += 12 + clen
    if not seen_iend:
        return "missing IEND"
    if idat_total < 1000:
        return "IDAT payload too small: %d bytes" % idat_total
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SRC_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    # Guard: refuse to write inside the repo (grader runs from a read-only copy).
    if os.path.commonpath([out_dir_abs, here]) == here:
        return fail("MAKEFUN_OUTPUT_DIR must be outside the repo: %s" % out_dir)
    if os.path.exists(out_dir_abs) and not os.path.isdir(out_dir_abs):
        return fail("MAKEFUN_OUTPUT_DIR is a file, not a directory: %s" % out_dir)
    if not os.path.exists(src):
        return fail("source not found: %s" % src)
    with open(src, "rb") as f:
        data = f.read()
    err = validate_png(data)
    if err:
        return fail("invalid %s: %s" % (SRC_NAME, err))
    os.makedirs(out_dir_abs, exist_ok=True)
    dst = os.path.join(out_dir_abs, SRC_NAME)
    if os.path.abspath(dst) == os.path.abspath(src):
        return fail("output would overwrite the source")
    with open(dst, "wb") as f:
        f.write(data)
    with open(dst, "rb") as f:
        back = f.read()
    if back != data:
        return fail("output differs from source after write")
    print("wrote %s (%d bytes, sha256 %s)" % (dst, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
