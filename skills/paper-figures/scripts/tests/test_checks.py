import os
import struct
import sys
import base64
import json
import shutil
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from checks import check_capture, main as checks_main, png_dimensions  # noqa: E402


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


class TestBadCapturesFailRatherThanCrash(unittest.TestCase):
    """A failed download leaves a zero-byte file and a 404 leaves an HTML body,
    both under a .png name — capture-recipes.md guarantees these reach the gate.
    They must be reported as failing figures; one of them must never abort the
    run and discard every other figure's verdict."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        # a valid 1x1 PNG
        self.good = os.path.join(self.d, "fig-01.png")
        with open(self.good, "wb") as fh:
            fh.write(base64.b64decode(
                b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42m"
                b"P8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="))
        open(os.path.join(self.d, "fig-02.png"), "wb").close()          # zero-byte
        with open(os.path.join(self.d, "fig-03.png"), "wb") as fh:      # HTML 404 body
            fh.write(b"<html><body>404 Not Found</body></html>")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_zero_byte_capture_is_a_failure_not_an_exception(self):
        r = check_capture(os.path.join(self.d, "fig-02.png"))
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("not a PNG", r["reason"])

    def test_html_body_capture_is_a_failure_not_an_exception(self):
        r = check_capture(os.path.join(self.d, "fig-03.png"))
        self.assertEqual(r["verdict"], "fail")

    def test_failed_downloads_keep_their_own_reason(self):
        """Two failed downloads are both zero bytes, so a naive duplicate scan
        groups them and relabels both 'byte-identical to another capture' —
        which the recipes map to 'the selector matched the wrong element',
        sending the operator after entirely the wrong remedy."""
        open(os.path.join(self.d, "fig-04.png"), "wb").close()   # a second zero-byte file
        out = os.path.join(self.d, "checks.json")
        checks_main([self.d, "-o", out])
        with open(out) as fh:
            payload = json.load(fh)
        for r in payload["results"]:
            if os.path.basename(r["path"]) in ("fig-02.png", "fig-04.png"):
                self.assertIn("not a PNG", r["reason"],
                              "a failed download must not be relabelled a duplicate")

    def test_a_dangling_symlink_does_not_abort_the_run(self):
        """check_capture's docstring promises one bad file cannot abort the run;
        os.path.getsize fails on a dangling symlink just as the PNG parse does."""
        os.symlink(os.path.join(self.d, "nowhere.png"), os.path.join(self.d, "fig-05.png"))
        out = os.path.join(self.d, "checks.json")
        checks_main([self.d, "-o", out])          # must not raise
        with open(out) as fh:
            payload = json.load(fh)
        self.assertEqual(payload["checked"], 4, "every figure must still get a verdict")

    def test_one_bad_file_does_not_lose_the_other_verdicts(self):
        out = os.path.join(self.d, "checks.json")
        rc = checks_main([self.d, "-o", out])
        self.assertNotEqual(rc, 0, "a run containing bad captures must not report success")
        with open(out) as fh:
            payload = json.load(fh)
        self.assertEqual(payload["checked"], 3, "every figure must still get a verdict")
        unreadable = [r for r in payload["results"] if "not a PNG" in r["reason"]]
        self.assertEqual(len(unreadable), 2, "both bad captures must be reported, not raised")
        # the valid PNG was still reached and classified (it is 1x1, so it fails
        # on dimensions rather than passing — the point is that it got a verdict)
        self.assertEqual(len(payload["results"]), 3)


if __name__ == "__main__":
    unittest.main()
