---
name: learn-from-video
description: "Watch a tutorial video (YouTube or any yt-dlp link, or a local file), learn what it teaches, and turn it into a Claude skill kept in ~/.claude/skills. Use when the user says \"learn this video\", \"learn what this teaches\", \"turn this tutorial into a skill\", \"watch this and remember how\" or pastes a tutorial link with \"make a skill\". Instagram reels go through reel-extract instead."
---

# Learn from a video

Paste a tutorial; Claude watches the frames and the words, writes down what it teaches, and keeps it as a skill for later chats. The watching is the `watch` skill (in this kit). This skill adds the learning and the keeping.

## 1. Watch

- **Instagram reel:** use `reel-extract` and stop reading here.
- **Anything else:** run the watch script and keep the working files:

```
python ~/.claude/skills/watch/scripts/watch.py "<url>" --detail balanced --no-whisper --out-dir videos/<YYYY-MM-DD>-<slug>
```

- On Windows the script needs a real `yt-dlp.exe` on PATH (it launches the binary directly, so a `.cmd` wrapper fails). `pip install --user yt-dlp` puts one in Python's user Scripts folder; add that folder to PATH.
- `--no-whisper` on purpose: audio never goes to a cloud Whisper. If the video has no captions, transcribe the downloaded file locally with `python ~/.claude/skills/reel-extract/transcribe.py <audio-or-video>` (faster-whisper on your own machine).
- For a long video, run `--detail transcript` first and find the moments that teach. Then pull frames only there with `--timestamps` or `--start/--end`.
- Read every frame the script lists. On-screen steps such as menus, settings, code and formulas are usually the substance, and the narration leaves them out.

## 2. Write down what it teaches

Write `notes.md` in the same folder:
- the source link, the creator and the date watched
- each step in order, with its timestamp
- the exact menu paths, commands, settings or formulas shown on screen
- what the video assumes or skips, and anything that looks wrong or out of date (check against the real tool when you can)

Write it in your own words. Never copy the script.

## 3. Keep it

- **Check first:** grep `~/.claude/skills` and the project's `.claude/skills`. If a skill already covers this, add a section to that skill instead of making a new one.
- **Otherwise,** create `~/.claude/skills/<name>/SKILL.md`:
  - a `description` with the trigger phrases the user would actually say
  - the steps, written as instructions
  - a "Source" line with the link and the key timestamps
  - one worked example on the user's own work, where it fits

## 4. Prove it

Use the new skill once on a real case in the same session, and fix whatever the trial run shows. A skill that has never run is still a draft. Then say what it now does in one line, with its trigger phrase.

## Rules

- Never log in to a video site and never use browser cookies. If a video is gated, say so.
- If a tutorial gates its files behind "comment for the link", search GitHub (`gh search repos`) and never comment or DM.
- Third-party code a video points to gets vetted before install: read it, grep for network and shell calls, note where it came from and pin the commit.
