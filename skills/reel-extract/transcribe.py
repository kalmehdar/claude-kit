"""Local, free transcription with word timings (faster-whisper).

  python transcribe.py <audio-or-video> [--model small.en] [--json out.json] [--prompt "Um, so, uh, like, you know..."]

Decodes through ffmpeg ourselves, because faster-whisper's PyAV path breaks on the installed PyAV
("open() got an unexpected keyword argument 'metadata_errors'").
Needs: pip install faster-whisper numpy, and ffmpeg on PATH.
"""
import argparse, json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def main():
    a = argparse.ArgumentParser(); a.add_argument('path'); a.add_argument('--model', default='small.en'); a.add_argument('--json'); a.add_argument('--prompt', help='initial prompt; use a filler-heavy one to keep um/uh/like for speaking practice')
    o = a.parse_args()
    segs, _ = WhisperModel(o.model, device='cpu', compute_type='int8').transcribe(load(o.path), word_timestamps=True, initial_prompt=o.prompt)
    words = []
    for s in segs:
        print(f'{s.start:6.2f} {s.end:6.2f} {s.text.strip()}')
        words += [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for w in s.words]
    if o.json: json.dump(words, open(o.json, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
