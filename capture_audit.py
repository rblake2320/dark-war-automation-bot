#!/usr/bin/env python3
"""Build a deterministic, local manifest for Dark War screen captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8"


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Return PNG dimensions after validating its signature and IHDR chunk."""
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("missing IHDR")
    return struct.unpack(">II", data[16:24])


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Return JPEG dimensions from a Start-of-Frame marker."""
    if not data.startswith(JPEG_SIGNATURE):
        raise ValueError("not a JPEG")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], "big")
        if length < 2 or offset + length > len(data):
            break
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            return (
                int.from_bytes(data[offset + 5:offset + 7], "big"),
                int.from_bytes(data[offset + 3:offset + 5], "big"),
            )
        offset += length
    raise ValueError("missing JPEG Start-of-Frame marker")


def image_metadata(path: Path) -> tuple[str, int, int, bytes]:
    payload = path.read_bytes()
    if payload.startswith(PNG_SIGNATURE):
        width, height = png_dimensions(payload)
        return "png", width, height, payload
    if payload.startswith(JPEG_SIGNATURE):
        width, height = jpeg_dimensions(payload)
        return "jpeg", width, height, payload
    raise ValueError(f"unsupported image: {path.name}")


def record(path: Path) -> dict[str, Any]:
    image_type, width, height, payload = image_metadata(path)
    return {
        "file": path.name,
        "image_type": image_type,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "width": width,
        "height": height,
    }


def audit(capture_dir: Path) -> dict[str, Any]:
    files = sorted(path for path in capture_dir.iterdir() if path.suffix.lower() in {".png", ".jpg", ".jpeg"})
    return {
        "schema": "dark-war-capture-audit/v1",
        "capture_directory": str(capture_dir.resolve()),
        "screens": [record(path) for path in files],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--output", type=Path, help="Write the JSON manifest here.")
    args = parser.parse_args()
    manifest = audit(args.capture_dir)
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
