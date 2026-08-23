import hashlib
import tempfile
import unittest
from pathlib import Path

from capture_audit import audit, image_metadata


def png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big")


class CaptureAuditTests(unittest.TestCase):
    def test_audit_records_dimensions_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "base.png"
            payload = png(390, 844)
            path.write_bytes(payload)
            result = audit(Path(directory))
        self.assertEqual(result["schema"], "dark-war-capture-audit/v1")
        self.assertEqual(result["screens"][0]["width"], 390)
        self.assertEqual(result["screens"][0]["height"], 844)
        self.assertEqual(result["screens"][0]["sha256"], hashlib.sha256(payload).hexdigest())

    def test_png_dimensions_rejects_non_png(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not-a-screen.png"
            path.write_bytes(b"nope")
            with self.assertRaises(ValueError):
                image_metadata(path)
