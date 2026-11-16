---
name: reel-extract
description: "Pull everything out of an Instagram reel (or a video file): caption, likes and comments, the spoken words with timings, every on-screen text card. Then turn what it teaches into Claude skills, workflows and tools. Use when the user pastes an instagram.com/reel/ or /p/ link, or says \"extract this reel\", \"what's in this reel\", \"break this down\", \"pull the content out of this\"."
argument-hint: "<instagram reel url | path to .mp4>"
---

# reel-extract

One script does the fetching; you do the watching.

```bash
python ~/.claude/skills/reel-extract/extract.py "<url or file>"
```

Needs once: `pip install yt-dlp faster-whisper numpy`, and `ffmpeg` on PATH. Transcription runs locally with `transcribe.py` in this folder (free; the first run downloads the Whisper model).

It writes `reels/<date>-<account>-<id>/` under the current folder (change it with `--out-root`):

| File | What |
|---|---|
| `reel.mp4` | the video |
| `meta.json` | account, date, likes, comments, caption, music if Instagram gives it |
| `transcript.txt`, `words.json` | spoken words from local Whisper (timestamped; it mishears names and jargon) |
| `frames/hook-NN.jpg` | every 0.5 s for the first 3 s |
| `frames/body-NNN.jpg` | every second after that (body-001 is 3 s, body-002 is 4 s, and so on) |
| `sheet-N.jpg` | contact sheets, 12 labelled frames each: read these, not the single frames |
| `extract.md` | the facts filled in, the analysis sections left for you |

## Every reel becomes Claude skills and workflows

The point of a reel is what it TEACHES. Turn that content into Claude skills, workflows and tools. Extract the substance, not the editing.

- **Read the content properly.** Every tool, site, command, framework, checklist or rule shown, item by item. When text on a card is too small on the sheets, pull full-size stills with ffmpeg at those timestamps and read them; never guess a card you couldn't read.
- **Find the real source, never DM for it.** When a reel names or shows a tool but gates the link ("comment X", "DM me for the repo", "link in bio"), search GitHub yourself: `gh search repos "<name>" --sort stars --limit 10`, then `gh repo view <owner/repo>` to confirm the README matches what the reel shows (same name, same screenshots or features). Use names, logos, README text and URLs visible in the frames; web search if `gh` finds nothing. Record the repo URL, stars, last push and licence in **What it teaches**. If two candidates fit, list both and say which matches the frames. Never comment on or DM the creator.
- **Then decide, per item:** a new skill in `~/.claude/skills/`, a change to an existing skill (check the list first), a script or scheduled workflow, a tool to adopt, or skip with the reason. Prefer extending an existing skill over a new one.
- **Summarise other people's material in your own words**; never paste a creator's cards or script wholesale into a skill.
- **Hooks, beats and posting tactics are out of scope** unless the user asks for them. A one-line note at most.

Start the work straight away when it's local and reversible (writing or editing a skill counts); ask first for anything that installs on a server, spends money, touches production or posts publicly.

## Then

1. Read every `sheet-*.jpg` in one message (parallel Reads); pull full-size stills for anything unreadable.
2. Fill `extract.md`: **What it teaches** (the deliverable), **On-screen text**, **Turn it into Claude skills and workflows**, **Implementation plan**.
3. Add a row to `reels/BACKLOG.md` (one line per reel: date, account, what it teaches, status) and re-rank it.
4. Reply with a short version: what the reel teaches, which skills or workflows it becomes, the first step, the folder.

## Rules

- Never log in to Instagram and never pass `--cookies-from-browser`. A reel Instagram hides behind a login comes back as `INSTAGRAM BLOCKED`: ask the user to save or screen-record it and send the file, then run the script on the file.
- Views are usually hidden from logged-out requests; say "not shown", never guess.
- Downloaded videos are for study only. Never repost them.
- Several links at once: run the script once per link, then group items that several reels share in BACKLOG.md.
