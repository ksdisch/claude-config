"""Regression tests for vtt-to-text.py.

Every case here is a defect that actually shipped on this branch and was caught
by review rather than by running the thing. They are written as the fixture that
would have caught each one, so the next edit to the parser has to stay honest:

  - rollup overlap must collapse, and a fixed line-window cannot do it
  - genuinely repeated short utterances must survive
  - Whisper's hours-less timestamps must parse
  - cue payload must not be filtered by what the text looks like
  - the output filename must be inert in a shell word

The module has a hyphen in its name, so it is loaded by path rather than
imported by name.
"""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

_MODULE = Path(__file__).resolve().parents[1] / "vtt-to-text.py"
_spec = importlib.util.spec_from_file_location("vtt_to_text", _MODULE)
vtt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vtt)


def cue(timing: str, *lines: str) -> str:
    return timing + "\n" + "\n".join(lines) + "\n"


def vtt_file(*cues: str, header: str = "WEBVTT\nKind: captions\nLanguage: en\n") -> str:
    return header + "\n" + "\n".join(cues)


class TestRollupOverlap(unittest.TestCase):
    """The defect that made the first fix worse than the bug (F2, reopened).

    yt-dlp auto-captions re-send every line still on screen with each new cue,
    so a repeated line sits two or three *emitted* lines back — not one. Any
    fixed window either misses this or eats real speech; dedup keys on cue
    membership instead.
    """

    ROLLUP = vtt_file(
        cue("00:00:00.030 --> 00:00:02.669 align:start position:0%", "so the thing"),
        cue("00:00:02.679 --> 00:00:04.940 align:start position:0%",
            "so the thing", "is we keep shipping"),
        cue("00:00:04.950 --> 00:00:07.190 align:start position:0%",
            "is we keep shipping", "and measuring"),
        cue("00:00:07.200 --> 00:00:09.500 align:start position:0%",
            "and measuring", "that is the whole trick"),
    )

    def test_each_phrase_appears_once(self):
        self.assertEqual(
            vtt.to_text(self.ROLLUP),
            ["so the thing", "is we keep shipping", "and measuring",
             "that is the whole trick"],
        )

    def test_no_dedup_keeps_the_overlap(self):
        # The escape hatch must actually be an escape hatch.
        self.assertEqual(len(vtt.to_text(self.ROLLUP, dedup=False)), 7)


class TestGenuineRepetitionSurvives(unittest.TestCase):
    """The defect the first fix was aimed at (F2, original).

    Back-channel speech recurs a few lines apart constantly in interviews. The
    source VTT is deleted after conversion, so anything dropped here is gone.
    """

    def test_short_utterance_repeated_across_cues(self):
        text = vtt_file(
            cue("00:00:01.000 --> 00:00:02.000", "Yeah."),
            cue("00:00:02.000 --> 00:00:03.000", "Right, exactly."),
            cue("00:00:03.000 --> 00:00:04.000", "Yeah."),
        )
        self.assertEqual(vtt.to_text(text), ["Yeah.", "Right, exactly.", "Yeah."])

    def test_phrase_repeated_much_later(self):
        cues = [cue("00:00:00.000 --> 00:00:01.000", "that's the tradeoff")]
        cues += [cue(f"00:0{i}:00.000 --> 00:0{i}:01.000", f"filler {i}")
                 for i in range(1, 9)]
        cues += [cue("00:40:00.000 --> 00:40:01.000", "that's the tradeoff")]
        self.assertEqual(vtt.to_text(vtt_file(*cues)).count("that's the tradeoff"), 2)


class TestWhisperTimestamps(unittest.TestCase):
    """Whisper's WriteVTT sets always_include_hours=False (F16).

    Requiring the hours field yielded zero cues and a hard exit on the one path
    the skill treats as expensive and gates behind a confirmation.
    """

    def test_sub_hour_timestamps_parse(self):
        text = vtt_file(
            cue("00:00.000 --> 00:02.960", "This is what whisper writes."),
            cue("00:02.960 --> 00:05.100", "No hours field."),
            header="WEBVTT\n",
        )
        self.assertEqual(
            vtt.to_text(text),
            ["This is what whisper writes.", "No hours field."],
        )

    def test_long_form_and_multi_digit_hours_parse(self):
        text = vtt_file(
            cue("00:00:01.000 --> 00:00:02.000", "standard"),
            cue("100:00:01.000 --> 100:00:02.000", "very long stream"),
            header="WEBVTT\n",
        )
        self.assertEqual(vtt.to_text(text), ["standard", "very long stream"])


class TestPayloadIsNotFilteredByAppearance(unittest.TestCase):
    """Cue payload is recognized by position, never by what it looks like.

    Matching header keywords against every line swallowed an ALL-CAPS cue
    opening with "NOTE" (F5); dropping lines containing `-->` or consisting of
    digits ate real speech (F6).
    """

    def test_all_caps_cue_starting_with_note(self):
        text = vtt_file(
            cue("00:00:01.000 --> 00:00:04.000",
                "NOTE THE DIFFERENCE HERE", "BECAUSE IT CHANGES EVERYTHING"),
            cue("00:00:04.000 --> 00:00:05.000", "NEXT CUE SURVIVES"),
        )
        self.assertEqual(len(vtt.to_text(text)), 3)

    def test_arrow_and_bare_number_speech(self):
        text = "WEBVTT\n\n1\n" + cue("00:00:01.000 --> 00:00:02.000", "2024") + \
            "\n2\n" + cue("00:00:02.000 --> 00:00:03.000", "the arrow --> operator")
        self.assertEqual(vtt.to_text(text), ["2024", "the arrow --> operator"])

    def test_real_note_block_before_cues_is_dropped(self):
        text = ("WEBVTT\n\nNOTE\nthis is a genuine note block\nspanning lines\n\n"
                + cue("00:00:01.000 --> 00:00:02.000", "actual speech"))
        self.assertEqual(vtt.to_text(text), ["actual speech"])

    def test_markup_and_entities_are_cleaned(self):
        text = vtt_file(
            cue("00:00:01.000 --> 00:00:02.000",
                "we ship<00:00:01.500><c> &amp; measure</c>"),
        )
        self.assertEqual(vtt.to_text(text), ["we ship & measure"])


class TestSafeFilename(unittest.TestCase):
    """The output name is echoed into later commands, so it must be inert (F13).

    Keeping the title off the command line is the primary defence; this is the
    second one, for the name the skill then reports.
    """

    def test_shell_executors_do_not_survive(self):
        stem = vtt.safe_filename("How `id` works: $(whoami) & ${HOME}")
        for char in ("`", "$", "'", '"', ";", "&", "|", "(", ")"):
            self.assertNotIn(char, stem, f"{char!r} survived into {stem!r}")

    def test_path_traversal_does_not_survive(self):
        self.assertNotIn("/", vtt.safe_filename("../../etc/passwd"))

    def test_empty_and_punctuation_only_titles_fall_back(self):
        self.assertEqual(vtt.safe_filename(""), "transcript")
        self.assertEqual(vtt.safe_filename("..."), "transcript")

    def test_ordinary_title_stays_readable(self):
        self.assertEqual(
            vtt.safe_filename("Andrej Karpathy: Software Is Changing Again"),
            "Andrej Karpathy- Software Is Changing Again",
        )

    def test_length_is_capped(self):
        self.assertLessEqual(len(vtt.safe_filename("x" * 500)), 120)


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.vtt = self.dir / "in.vtt"
        self.vtt.write_text(vtt_file(cue("00:00:01.000 --> 00:00:02.000", "hello")))

    def test_title_file_names_the_output(self):
        title = self.dir / "title.txt"
        title.write_text("My Talk: Part 1\n")
        rc = vtt.main([str(self.vtt), "--title-file", str(title), "--dir", str(self.dir)])
        self.assertEqual(rc, 0)
        self.assertTrue((self.dir / "My Talk- Part 1.txt").is_file())

    def test_output_and_title_file_are_mutually_exclusive(self):
        title = self.dir / "title.txt"
        title.write_text("t")
        rc = vtt.main([str(self.vtt), "-o", str(self.dir / "x.txt"),
                       "--title-file", str(title)])
        self.assertEqual(rc, 1)

    def test_missing_input_is_an_error(self):
        self.assertEqual(vtt.main([str(self.dir / "nope.vtt")]), 1)

    def test_file_with_no_cues_writes_nothing(self):
        empty = self.dir / "empty.vtt"
        empty.write_text("WEBVTT\n")
        out = self.dir / "out.txt"
        self.assertEqual(vtt.main([str(empty), "-o", str(out)]), 1)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
