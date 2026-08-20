---
name: youtube-transcript
description: >-
  Download a YouTube video's transcript with yt-dlp — manual captions first, auto-generated
  as fallback, local Whisper transcription only as a gated last resort — and convert it to
  deduplicated plain text named after the video. Use when given a YouTube URL and asked for
  the transcript, captions, or subtitles, when asked to "transcribe a YouTube video", or
  when another skill needs a video's text. Trigger on "youtube transcript", "get the
  transcript", "download captions", "get subtitles", "transcribe this video".
allowed-tools: Bash, Read, Write
---

# YouTube Transcript

Fetch a YouTube video's text. The whole skill is one decision — **what is the cheapest
source of text that actually exists for this video** — and then a conversion step.

Preference order, never reversed:

1. **Manual captions** (`--write-sub`) — human-written, punctuated, no scroll overlap.
2. **Auto-generated captions** (`--write-auto-sub`) — nearly always present, needs cleanup.
3. **Whisper on downloaded audio** — accurate but slow and bandwidth-hungry. **Gated.**

Most videos resolve at step 1 or 2 in a few seconds. Step 3 is rare and always costs Kyle
something, so it never happens without him saying yes.

---

## Invariants

These hold on every run. Everything else in this file is guidance.

- **`--list-subs` before any download.** Guessing which captions exist and reacting to the
  failure wastes a round trip and produces confusing errors when the real problem is a
  private or geo-blocked video. Look first.
- **Whisper is opt-in, with the cost shown.** Never download audio or install Whisper
  without quoting the duration and approximate audio size and getting an explicit yes.
  These are the only steps in the skill that consume real bandwidth or disk.
- **Never install anything silently.** `yt-dlp` missing is a question, not a `brew install`.
- **Ask in chat, never in the shell.** The Bash tool has no stdin — a script that ends in
  `read -r RESPONSE` hangs or reads EOF and takes the default branch. Every confirmation in
  this skill is a turn in the conversation, and the shell only runs after the answer.
- **One command per Bash call, no orchestration scripts.** Long chained scripts hide which
  step failed and re-run expensive steps on retry. Run a step, read the output, decide.
- **The `.vtt` is an intermediate.** The deliverable is `.txt`. Delete the VTT once the
  conversion succeeds — but not before, and never if the conversion errored.

---

## Steps

### 1. Confirm yt-dlp is available

```
command -v yt-dlp
```

If it prints a path, continue. If not, tell Kyle it's missing and offer the install for his
platform — `brew install yt-dlp` on this Mac, `pip3 install yt-dlp` anywhere. Wait for yes.
If the install fails, stop and point at
<https://github.com/yt-dlp/yt-dlp#installation>; don't improvise a workaround.

### 2. Read the video's metadata and caption inventory

```
yt-dlp --print "%(title)s|%(duration)s|%(id)s" "<URL>"
yt-dlp --list-subs "<URL>"
```

The first gives the title for the output filename and the duration for the Whisper cost
estimate. The second says which of the three paths below you're on.

If either errors, report yt-dlp's own message. The common causes — private, members-only,
age-restricted, geo-blocked, or a bad URL — are all things Kyle needs to know about rather
than something to retry around.

### 3. Get the captions

Work down the list until one produces a `.vtt`. `--skip-download` keeps this to a few KB;
`--sub-langs en` avoids pulling every language when only English is wanted.

**Manual captions** (if `--list-subs` showed a non-automatic English track):

```
yt-dlp --write-sub --sub-langs en --skip-download --output transcript "<URL>"
```

**Auto-generated captions** (fallback):

```
yt-dlp --write-auto-sub --sub-langs en --skip-download --output transcript "<URL>"
```

Either writes `transcript.en.vtt` into the working directory.

If the video isn't in English, take whatever track `--list-subs` actually offers and say
which language you used — a silent language substitution produces a transcript Kyle can't
read and won't expect.

### 4. Whisper — only if steps 3's options both came up empty

Stop and ask, quoting real numbers from step 2:

> No captions exist for this video (42 min, ~38 MB of audio). I can download the audio and
> transcribe it locally with Whisper — several minutes of CPU. Want me to?

Only after yes:

1. `command -v whisper` — if missing, ask again before `pip3 install openai-whisper`
   (~1–3 GB with models, and it needs `ffmpeg`).
2. `yt-dlp -x --audio-format mp3 --output "audio_%(id)s.%(ext)s" "<URL>"`
3. `whisper "audio_<id>.mp3" --model base --output_format vtt`
4. Offer to delete the mp3 once the VTT exists.

Use `--model base` unless Kyle asks otherwise; `small` and up buy accuracy at a steep time
cost, and `tiny` is noticeably worse on technical vocabulary.

### 5. Convert to plain text

```
python3 <skill>/scripts/vtt-to-text.py transcript.en.vtt -o "<Video Title>.txt"
```

The script strips the WEBVTT header, cue timings, `NOTE`/`STYLE` blocks, karaoke `<c>`
tags, and HTML entities, then removes the scroll overlap that makes auto-captions read
every phrase two or three times.

Its deduplication is **local** — a line is dropped only when it repeats one of the last 10
emitted lines. That matters: whole-file deduplication is the obvious approach and it
silently loses genuine repetition, so a speaker who returns to a phrase 30 minutes later
has that moment deleted from the transcript. Pass `--window 0` to disable dedup entirely
when working with manual captions, which have no overlap to remove.

Sanitize the title for the filename — replace `/` and `:`, drop `?` and quotes. The script
creates the output's parent directory if needed and refuses to write an empty file.

### 6. Clean up and report

Delete the `.vtt` once the `.txt` exists. Tell Kyle the output path, the line count, and
which of the three sources the text came from — manual captions and Whisper output read
very differently from auto-captions, and knowing which he has changes how much he trusts
the punctuation.

---

## Where the file goes

Default to the **current working directory** — the transcript is usually wanted right where
Kyle is working.

Two exceptions:

- **Feeding `youtube-breakdown`.** The transcript is an intermediate, not a deliverable.
  Write it to the session scratchpad and don't leave it in the repo. `youtube-breakdown`
  calls this skill for URL input and saves its own output separately.
- **Kyle names a destination.** Then use that.

Never write into a git repo's tracked tree without saying so — a stray 200 KB transcript in
`git status` is noise at best and a committed accident at worst.

---

## Troubleshooting

| Symptom | What's actually wrong |
|---|---|
| `--list-subs` shows tracks, download writes nothing | Language mismatch — `--sub-langs en` on a video with only `es` tracks silently writes no file. Re-run with the language that's actually listed. |
| Output text is one-third repeated phrases | The VTT was converted with something other than the script (or `--window 0`). Re-run the conversion. |
| `HTTP Error 403` / "Sign in to confirm you're not a bot" | yt-dlp is out of date, or YouTube wants a session. Update first (`brew upgrade yt-dlp`); mention `--cookies-from-browser chrome` as the next option but don't run it without asking — it reads Kyle's browser cookies. |
| Whisper fails on start | Missing `ffmpeg` (`brew install ffmpeg`) or insufficient disk for the model. |
| Transcript ends early | Some videos have partial captions. Compare the last timestamp in the VTT against the duration from step 2 before assuming the file is fine. |

---

## Related

- **`youtube-breakdown`** — the usual consumer. It calls this skill when given a URL, then
  processes the text into structured notes.
