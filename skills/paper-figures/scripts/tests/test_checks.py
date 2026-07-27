import os
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from checks import check_capture, png_dimensions  # noqa: E402


def write_png(path, w, h, rgb, noise=False):
    rows = []
    for y in range(h):
        if noise:
            px = b"".join(
                bytes(((x * 7 + y * 13) % 256, (x * 3) % 256, (y * 5) % 256))
                for x in range(w)
            )
        else:
            px = bytes(rgb) * w
        rows.append(b"\x00" + px)
    raw = b"".join(rows)

    def chunk(tag, data):
        body = tag + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    blob = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(blob)
    return path


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.join(os.path.dirname(__file__), "_tmp")
        os.makedirs(self.tmp, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, f))
        os.rmdir(self.tmp)

    def test_png_dimensions(self):
        p = write_png(os.path.join(self.tmp, "a.png"), 900, 600, (255, 255, 255))
        self.assertEqual(png_dimensions(p), (900, 600))

    def test_blank_image_fails(self):
        p = write_png(os.path.join(self.tmp, "blank.png"), 900, 600, (255, 255, 255))
        r = check_capture(p)
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("blank", r["reason"])

    def test_dense_image_passes(self):
        p = write_png(os.path.join(self.tmp, "real.png"), 300, 200, None, noise=True)
        r = check_capture(p)
        self.assertEqual(r["verdict"], "pass")

    def test_degenerate_dimensions_fail(self):
        p = write_png(os.path.join(self.tmp, "thin.png"), 2, 600, (10, 20, 30))
        r = check_capture(p)
        self.assertEqual(r["verdict"], "fail")

    def test_duplicate_hashes_are_reported(self):
        from checks import find_duplicates

        a = write_png(os.path.join(self.tmp, "x.png"), 60, 40, (1, 2, 3))
        b = write_png(os.path.join(self.tmp, "y.png"), 60, 40, (1, 2, 3))
        c = write_png(os.path.join(self.tmp, "z.png"), 60, 40, (9, 9, 9))
        dupes = find_duplicates([a, b, c])
        self.assertEqual(len(dupes), 1)
        self.assertEqual(sorted(os.path.basename(p) for p in dupes[0]), ["x.png", "y.png"])


if __name__ == "__main__":
    unittest.main()
