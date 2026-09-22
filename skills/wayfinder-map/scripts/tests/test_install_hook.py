"""Tests for install_hook.py, against temp settings files only."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import install_hook as ih  # noqa: E402

EXISTING = {
    "model": "opus",
    "hooks": {
        "Stop": [{"hooks": [{"type": "prompt", "prompt": "keep me"}]}],
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "true"}]}],
    },
}


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        d = Path(self._tmp.name)
        self.settings = d / "settings.json"
        self.backups = d / "backups"
        self.settings.write_text(json.dumps(EXISTING, indent=2))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_it(self, *extra: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ih.main(["--settings", str(self.settings), "--backups", str(self.backups), *extra])
        return code, out.getvalue(), err.getvalue()

    def test_installs_once_keeping_other_keys(self):
        code, _, _ = self.run_it()
        self.assertEqual(code, 0)
        data = json.loads(self.settings.read_text())
        self.assertEqual(data["model"], "opus")
        self.assertEqual(data["hooks"]["PreToolUse"], EXISTING["hooks"]["PreToolUse"])
        self.assertEqual(data["hooks"]["Stop"][0], EXISTING["hooks"]["Stop"][0])
        self.assertEqual(data["hooks"]["Stop"][1], ih.ENTRY)
        self.assertTrue(self.settings.read_text().startswith('{\n  "model"'))

    def test_second_run_changes_nothing(self):
        self.run_it()
        before = self.settings.read_text()
        code, out, _ = self.run_it()
        self.assertEqual(code, 0)
        self.assertIn("already installed", out)
        self.assertEqual(self.settings.read_text(), before)

    def test_backup_written(self):
        self.run_it()
        backups = list(self.backups.glob("settings.json.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), EXISTING)

    def test_creates_hooks_and_stop_when_absent(self):
        self.settings.write_text(json.dumps({"model": "opus"}))
        self.run_it()
        self.assertEqual(json.loads(self.settings.read_text())["hooks"], {"Stop": [ih.ENTRY]})

    def test_dry_run_writes_nothing(self):
        before = self.settings.read_text()
        code, out, _ = self.run_it("--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)[1], ih.ENTRY)
        self.assertEqual(self.settings.read_text(), before)
        self.assertFalse(self.backups.exists())

    def test_invalid_json_exits_1_untouched(self):
        self.settings.write_text("{ not json")
        code, _, err = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", err)
        self.assertEqual(self.settings.read_text(), "{ not json")
        self.assertFalse(self.backups.exists())


if __name__ == "__main__":
    unittest.main()
