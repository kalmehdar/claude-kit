"""Pull everything out of one reel: caption, stats, video, frames, spoken words.

  python ~/.claude/skills/reel-extract/extract.py <instagram-reel-url | local .mp4> [--out-root reels]

Writes reels/<date>-<account>-<id>/ with reel.mp4, meta.json, transcript.txt,
words.json, frames/ (hook-NN every 0.5 s for 3 s, then body-NNN every second from 3 s) and extract.md (the facts filled in, the analysis sections left for
Claude to write after reading the frames). Never logs in and never uses browser cookies: a reel
Instagram hides behind a login comes back as an error asking for the file instead.
"""
import argparse, datetime, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WHISPER = HERE / 'transcribe.py'


def run(cmd, **kw):
    # Children print UTF-8 (Whisper emits emoji like the music note); Windows defaults to cp1252 and crashes.
    env = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, **kw)


def fetch(url, out):
    r = run([sys.executable, '-m', 'yt_dlp', '-J', '--no-warnings', url])
    if r.returncode:
        err = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'unknown error'
        if re.search(r'login|cookies|rate.?limit|private', err, re.I):
            sys.exit(f'INSTAGRAM BLOCKED: {err}\nThis reel is gone, private, or needs a login. Ask the user to send the video file '
                     '(save it or screen-record it) and run this script on the file instead.')
        sys.exit(f'FETCH FAILED: {err}')
    meta = json.loads(r.stdout)
    acct = re.sub(r'[^\w.-]', '', meta.get('channel') or meta.get('uploader_id') or meta.get('uploader') or 'unknown')
    day = meta.get('upload_date') or datetime.date.today().strftime('%Y%m%d')
    folder = out / f'{day[:4]}-{day[4:6]}-{day[6:]}-{acct}-{meta.get("id", "reel")}'
    folder.mkdir(parents=True, exist_ok=True)
    d = run([sys.executable, '-m', 'yt_dlp', '--no-warnings', '-f', 'best[ext=mp4]/best', '--merge-output-format', 'mp4',
             '-o', str(folder / 'reel.%(ext)s'), url])
    if d.returncode:
        sys.exit(f'DOWNLOAD FAILED: {d.stderr.strip()[-400:]}')
    return meta, folder, next(folder.glob('reel.*'))


def local(path, out):
    p = Path(path).resolve()
    folder = out / f'{datetime.date.today()}-file-{re.sub(r"[^\w-]", "", p.stem)[:40]}'
    folder.mkdir(parents=True, exist_ok=True)
    dur = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)]).stdout.strip()
    return {'id': p.stem, 'duration': float(dur or 0), 'webpage_url': str(p)}, folder, p


def main():
    a = argparse.ArgumentParser()
    a.add_argument('source')
    a.add_argument('--out-root', default='reels')
    o = a.parse_args()
    out = Path(o.out_root)
    meta, folder, video = local(o.source, out) if Path(o.source).exists() else fetch(o.source, out)
    keep = {k: meta.get(k) for k in ('id', 'webpage_url', 'uploader', 'uploader_id', 'channel', 'upload_date', 'duration',
                                     'view_count', 'like_count', 'comment_count', 'title', 'description', 'track', 'artist')}
    (folder / 'meta.json').write_text(json.dumps(keep, indent=1, ensure_ascii=False), encoding='utf-8')

    # Frames: 2 a second through the hook (first 3 s), then 1 a second, 768 px wide so on-screen text reads.
    if not keep.get('duration'):
        keep['duration'] = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                      str(video)]).stdout.strip() or 0)
    fd = folder / 'frames'; fd.mkdir(exist_ok=True)
    for args in (['-t', '3', '-vf', 'fps=2,scale=768:-2', str(fd / 'hook-%02d.jpg')],
                 ['-ss', '3', '-vf', 'fps=1,scale=768:-2', str(fd / 'body-%03d.jpg')]):
        f = run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-q:v', '3', *args])
        if f.returncode:
            print(f'WARNING: frame extraction failed: {f.stderr[-300:]}', file=sys.stderr)
    frames = sorted(fd.glob('*.jpg'), key=lambda p: (not p.name.startswith('hook'), p.name))
    (folder / 'meta.json').write_text(json.dumps(keep, indent=1, ensure_ascii=False), encoding='utf-8')

    # Contact sheets: 12 labelled frames per image, so a reel is read in a handful of images, not 50.
    sheets = []
    for i in range(0, len(frames), 12):
        chunk = frames[i:i + 12]
        lab = lambda f: f.stem.replace('-', ' ')
        filt = ''.join(f"[{k}:v]scale=360:-2,drawtext=text='{lab(f)}':x=8:y=8:fontsize=22:fontcolor=yellow:box=1:boxcolor=black[v{k}];"
                       for k, f in enumerate(chunk))
        filt += ''.join(f'[v{k}]' for k in range(len(chunk)))
        filt += f"xstack=inputs={len(chunk)}:layout={'|'.join(f'{(k % 6) * 360}_{(k // 6) * 640}' for k in range(len(chunk)))}:fill=black"
        sheet = folder / f'sheet-{i // 12 + 1}.jpg'
        r = run(['ffmpeg', '-v', 'error', '-y', *sum((['-i', str(f)] for f in chunk), []), '-filter_complex', filt, str(sheet)])
        if sheet.exists():
            sheets.append(sheet)
        else:
            print(f'WARNING: contact sheet {sheet.name} failed: {r.stderr[-200:]}', file=sys.stderr)

    # Words: local Whisper, free, timestamped.
    t = run([sys.executable, str(WHISPER), str(video), '--json', str(folder / 'words.json')])
    transcript = t.stdout.strip() if t.returncode == 0 else f'(transcription failed: {t.stderr.strip()[-200:]})'
    (folder / 'transcript.txt').write_text(transcript + '\n', encoding='utf-8')

    stat = lambda k: f'{keep[k]:,}' if isinstance(keep.get(k), int) else 'not shown'
    music = ' by '.join(x for x in (keep.get('track'), keep.get('artist')) if x) or 'not given'
    rel = lambda p: p.relative_to(folder).as_posix()
    md = f"""# Reel: {keep.get('uploader') or keep.get('channel') or 'local file'} ({keep.get('id')})

Source: {keep.get('webpage_url')}
Extracted: {datetime.date.today()} · posted {keep.get('upload_date') or 'unknown'} · {round(keep.get('duration') or 0, 1)} s
Views {stat('view_count')} · likes {stat('like_count')} · comments {stat('comment_count')} · music: {music}

## Caption

{(keep.get('description') or '(none)').strip()}

## Spoken words (local Whisper, may mishear names)

```
{transcript or '(no speech)'}
```

## Frames

Contact sheets (read these): {', '.join(rel(x) for x in sheets) or '(none)'}
Single frames for a closer look: frames/ ({len(frames)} files)

## What it teaches
_(to fill: the substance, item by item: every tool, site, command, framework, rule or step the reel shows, with what each one does and any link or name needed to find it. Summarise in our words; this is the deliverable)_

## On-screen text
_(to fill: every text card in order, with its time)_

## Turn it into Claude skills and workflows
_(to fill: per item, new skill, change to an existing skill, workflow/script, tool to adopt, or skip, with where it lives and why)_

## Implementation plan
_(to fill: the order, the first step, and what needs your yes)_
"""
    (folder / 'extract.md').write_text(md, encoding='utf-8')
    print(f'FOLDER {folder}\nFRAMES {len(frames)}\nWORDS {len(transcript.splitlines())} lines\nNEXT read every sheet-*.jpg, then fill extract.md')


if __name__ == '__main__':
    main()
